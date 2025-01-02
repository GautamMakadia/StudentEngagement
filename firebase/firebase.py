import firebase_admin
from firebase_admin import credentials, storage
from config import env

cred = credentials.Certificate(env.FIREBASE_CONF)
app = firebase_admin.initialize_app(cred)

firebase_bucket = storage.bucket(app=app, name=env.FIREBASE_STORAGE_BUCKET)
