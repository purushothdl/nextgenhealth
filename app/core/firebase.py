import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase
def initialize_firebase():
    cred = credentials.Certificate("service_account_key.json")
    firebase_admin.initialize_app(cred)