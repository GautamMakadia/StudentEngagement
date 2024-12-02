import io
import traceback
from datetime import datetime
from hashlib import sha256
from typing import *
from venv import logger

from asyncpg import Connection
from asyncpg.transaction import Transaction
from fastapi import APIRouter, Form, HTTPException

from database.db import tables, database
from models.students import Users
from util import log

router = APIRouter(prefix="/auth", tags=["auth", ])

@router.post("/login")
async def login(
    id: Annotated[int, Form()],
    password: Annotated[str, Form()],
):

    pass_hash = sha256(io.BytesIO(password.encode('utf-8')).read()).hexdigest()

    try:
        conn: Connection
        async with database.pool.acquire() as conn:
            async with conn.transaction():
                stmt = f"select * from users where id=$1 "
                data = (int(id),)
                user: Users = await conn.fetchrow(stmt, *data, record_class=Users)

                if user is None:
                    raise HTTPException(status_code=404, detail={
                        "id": id,
                        "message": "No User Found",
                    })

                if user["password"] != pass_hash:
                    raise HTTPException(status_code=401, detail={
                        "message": "password is incorrect",
                        "error": "invalid credentials"
                    })

                stmt = "update users set last_login=$1 where id=$2"
                date = datetime.now()
                args = (date, id)
                await conn.execute(stmt, *args)

                return dict(
                    id=id,
                    status=200,
                    message="authentication successful",
                    user={
                        "firstname": user["firstname"],
                        "midname": user["midname"],
                        "lastname": user["lastname"],
                        "email": user["email"],
                        "phone": user['phone'],
                        "role": user["role"],
                        "create_time": user['create_time'],
                        "last_login": f"{date}"
                    }
                )

    except HTTPException as error:
        raise error
    except Exception as error:
        log("/auth/login", error)
        raise HTTPException(status_code=500, detail={
            "error": error,
            "message": traceback.format_stack(),
            "origin": "auth/login",
        })




@router.post('/signup')
async def sign_up(
        id: Annotated[int, Form()],
        password: Annotated[str, Form()],
        email: Annotated[str, Form()],
        phone: Annotated[str, Form()],
        firstname: Annotated[str, Form()],
        midname: Annotated[str, Form()],
        lastname: Annotated[str, Form()],
        role: Annotated[str, Form()]
):
    try:
        conn: Connection
        async with database.pool.acquire() as conn:
            pass_hash = sha256(io.BytesIO(password.encode('utf-8')).read()).hexdigest()
            transaction: Transaction
            async with conn.transaction():
                users: Users = await conn.fetchrow(
                    f"select * from {tables["users"]} where id=$1", id, record_class=Users)

                if users is not None:
                    raise HTTPException(status_code=409, detail={
                            "id": users['id'],
                            "user": {
                                "username": users["firstname"] + users["lastname"],
                                "email": users["email"]
                            },
                            "message": "User Already Exist",
                        }
                    )
                date = datetime.now()
                stmt:str = """
                        insert into users (id, create_time, email, password, phone, role, firstname, midname, lastname)
                        values($1, $2, $3, $4, $5, $6, $7, $8, $9);    
                """
                value = (id, date, email, pass_hash, int(phone), role, firstname, midname, lastname)

                await conn.execute(stmt, *value)

                return dict(
                    id=id,
                    status=201,
                    message="user created successfully",
                    time=date
                )
    except HTTPException as error:
        raise error
    except Exception as error:
        logger.error(traceback.format_exc())
        log("/auth/signup", error)
        raise HTTPException(status_code=500, detail={
            "name": "Signup error.",
            "path": "/auth/signup",
            "error": traceback.format_exc(),
            "status": 500,
            "message": "contact support"
        })