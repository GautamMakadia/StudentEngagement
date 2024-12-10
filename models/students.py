from datetime import datetime

from asyncpg import Record


class Users(Record):
    id: int
    create_time: datetime
    email: str
    password: str
    last_login: datetime
    phone: str
    firstname: str
    midname: str
    role: str
    lastname: str


class Venue(Record):
    id: int
    name: str
    qr_id: str
    category: str
    number: int

class Session(Record):
    id: int
    description: str
    user_id: int
    venue_id: int
    punch_in_time: datetime
    punch_out_time: datetime
    duration: str
    is_active: bool

class QRCode(Record):
    id: str
    url: str
    venue_id: int