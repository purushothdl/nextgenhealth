import json
import os
import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings


# Initialize Firebase
def initialize_firebase():
    # Read the service account key JSON from environment variable
    service_account_key_json = settings.FIREBASE_SERVICE_ACCOUNT_KEY_JSON

    if service_account_key_json:
        # Parse the JSON content
        service_account_key = json.loads(service_account_key_json)

        # Initialize Firebase Admin SDK with the dictionary
        cred = credentials.Certificate(service_account_key)
        firebase_admin.initialize_app(cred)
    else:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY_JSON environment variable is not set.")