import traceback
from hashlib import sha1
from io import BytesIO
from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Form, HTTPException

from database.db import database
from firebase.firebase import firebase_bucket
from lib.qrcode import generate_qr_code
from models.students import Venue

router = APIRouter(prefix="/venue", tags=["venue",])

@router.post("")
async def add_new_venue(
    venue_id: Annotated[str, Form()],
    category: Annotated[str, Form()]
):
    conn: Connection

    try:
        async with database.pool.acquire() as conn:
            async with conn.transaction():
                venue: Venue = await conn.fetchrow(
                    "select * from venue where id=$1;",
                    int(venue_id), record_class=Venue)

                if venue is not None:
                    raise HTTPException(409, detail={
                        "venue_id": venue["id"],
                        "message": "venue already exist",
                        "venue": {
                            "id": venue["id"],
                            "category": venue["category"],
                        }
                    })

                img, tag = generate_qr_code(venue_id, category)
                qr_id = sha1(BytesIO(tag.encode('utf-8')).read()).hexdigest()

                try:
                    blob = firebase_bucket.blob(tag)
                    blob.upload_from_file(img, content_type="image/png", rewind=True)
                    blob.make_public()
                    qr_image_url = blob.public_url

                except Exception as error:
                    print(traceback.format_exc())
                    raise HTTPException(500, detail={
                        "name": error.args,
                        "error": "file upload error",
                    })

                await conn.execute("insert into qr_code values($1, $2);", qr_id, qr_image_url)

                values = (int(venue_id), qr_id, category)
                venue = await conn.fetchrow(
                    "insert into venue(id, qr_id, category) values($1, $2, $3) returning *;",
                    *values, record_class=Venue
                )

    except HTTPException as error: raise error
    except Exception as error:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail={
            "error": error.args,
            "trace": traceback.format_exc()
        })

    return {
        "venue": {
            "id": venue['id'],
            "qr_code_url": qr_image_url,
            "category": venue['category']
        },
        "message": "qr_code created successfully",
    }


@router.get("/{id}")
async def get_session(id: int):
    try:
        conn: Connection
        async with database.pool.acquire() as conn:
            async with conn.transaction():
                stmt = """
                    select 
                       v.category, v.id, qr.id as qr_id, qr.url
                    from 
                        venue v
                    inner join
                        qr_code as qr 
                    on v.qr_id = qr.id
                    where v.id = $1
                """
                venue: Venue = await conn.fetchrow(stmt, id, record_class=Venue)

                if venue is None:
                    raise HTTPException(404, detail={
                        "session_id": id,
                        "error": "Resource Not Found",
                        "status": 404,
                    })

                response: dict = {
                    "id": id,
                    "category": venue['category'],
                    "qr_code": {
                        "id": venue['qr_id'],
                        "url": venue['url']
                    }
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