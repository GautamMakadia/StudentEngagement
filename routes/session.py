import traceback
from datetime import datetime
from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, HTTPException, Form
from pyparsing import Empty

from database.db import database
from models.students import Session

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/user/{uid}")
async def get_user_sessions(uid: int):
    try:
        conn: Connection
        async with database.pool.acquire() as conn:
            async with conn.transaction():
                stmt = """
                    select 
                        *
                    from session 
                    where
                        user_id = $1  
                """

                sessions: list[Session] = await conn.fetch(stmt, uid, record_class=Session)

                if sessions is Empty:
                    sessions: str = "no session found"
                    return

                for session in sessions:
                    session.punch_in_time.strftime("%A, %d %b %Y")

                response = dict(
                    uid=uid,
                    sessions=sessions
                )

                return response

    except Exception as error:
        raise error



@router.get("/{id}")
async def get_session(id: int):
    try:
        conn: Connection
        async with database.pool.acquire() as conn:
            stmt = """
                select 
                    s.id, s.description, s.user_id, s.venue_id, s.punch_in_time, s.punch_out_time, s.is_active, 
                    v.category as venue_category,
                from session as s 
                inner join
                    venue as v
                on 
                    s.venue_id = v.id
                where
                    s.id = $1  
            """
            session: Session = await conn.fetchrow(stmt, id, record_class=Session)

            if session is None:
                raise HTTPException(404, detail={
                    "session_id": id,
                    "error": "Resource Not Found",
                    "status": 404,
                })

            punch_in: datetime = datetime.fromisoformat(session["punch_in_time"])
            punch_out: datetime = datetime.fromisoformat(session["punch_out_time"])

            response = {
                "id": session["id"],
                "description": session['description'],
                "user_id": session["user_id"],
                "punch_in": punch_in.strftime("%A %d %b %y"),
                "punch_out": punch_out.strftime("%A %d %b %y"),
                "is_active": session['is_active'],
                "venue_id": session['venue_id'],
                "venue_category": session['venue_category']
            }


            return response

    except HTTPException as error: raise error
    except Exception as error:
        print(traceback.format_exc())
        raise HTTPException(500, detail={
            "name": f"{type(error).__class__.__name__}",
            "error": error.args,
            "trace": traceback.format_exc()
        })

@router.post("")
async def register_session(
    uid: Annotated[int, Form()],
    venue_id: Annotated[int, Form()],
    desc: Annotated[str, Form()] = ""
):
    try:
        conn: Connection
        async with database.pool.acquire() as conn:
            async with conn.transaction():
                stmt = """
                    select * from session
                    where user_id = $1 and venue_id = $2 and is_active = true;
                """
                session: Session = await conn.fetchrow(stmt, uid, venue_id, record_class=Session)

                if session is not None:
                    return HTTPException(309, detail={
                        "message": "session already registered",
                        "session": {
                            "id": session['id'],
                            "user_id": uid,
                            "venue_id": venue_id,
                            "punch_in_time": session['punch_in_time'],
                        }
                    })

                stmt = """
                    insert into session (description, user_id, venue_id, punch_in_time)
                    values($1, $2, $3, $4) returning id; 
                """
                date = datetime.now()
                values = (desc, uid, venue_id, date)
                session: Session = await conn.fetchrow(stmt, *values, record_class=Session)

                response: dict = {
                    "id": session['id'],
                    "user_id": uid,
                    "venue_id": venue_id,
                    "punch_in_time": date.date() + date.time(),
                    "is_active": True
                }

                return response

    except HTTPException as error: raise error
    except Exception as error:
        print(traceback.format_exc())
        raise HTTPException(500, detail={
            "name": f"{type(error).__class__.__name__}",
            "error": error.args,
            "trace": traceback.format_exc()
        })

@router.put("")
async def close_session(id: Annotated[int, Form()]):
    try:
        conn: Connection
        async with database.pool.acquire() as conn:
            async with conn.transaction():
                stmt = """
                    select * from session 
                    where id = $1 and is_active = true
                """

                session: Session = await conn.fetchrow(stmt, id, record_class=Session)

                if session is None:
                    raise HTTPException(404, detail={
                        "session": id,
                        "message": "session is already closed",
                    })

                date = datetime.now()
                stmt = """
                    update session
                    set 
                        punch_out_time = $1, duration = age($1, punch_in_time), is_active = false
                    returning duration::text;
                """
                session: Session = await conn.fetchrow(stmt, date, record_class=Session)

                response: dict = dict(
                    id=id,
                    puch_out_time=date,
                    duration=session['duration'],
                    message="session closed"
                )

                return response

    except HTTPException as error: raise error
    except Exception as error:
        print(traceback.format_exc())
        raise HTTPException(500, detail={
            "name": f"{type(error).__class__.__name__}",
            "error": error.args,
            "trace": traceback.format_exc()
        })
