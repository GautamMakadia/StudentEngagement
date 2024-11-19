import firebase_admin
from firebase_admin import credentials, storage
from database.db import setting

cred = credentials.Certificate(setting.FIREBASE_CONF)
app = firebase_admin.initialize_app(cred)

firebase_bucket = storage.bucket(app=app, name="student-engagement-17af4.appspot.com")
