import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("knowiix.firebase")

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth as firebase_auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    firestore = None
    firebase_auth = None

class FirebaseService:
    def __init__(self):
        self.initialized = False
        self.db = None
        self._init_firebase()

    def _init_firebase(self):
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
        if FIREBASE_AVAILABLE and cred_path and os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
                logger.info("Connected to Firebase Firestore successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Firebase Admin SDK: {e}. Falling back to internal datastore.")
        else:
            logger.info("Using internal high-performance datastore (Firebase simulation mode).")

    def verify_id_token(self, token: str) -> Optional[Dict[str, Any]]:
        if self.initialized and firebase_auth:
            try:
                return firebase_auth.verify_id_token(token)
            except Exception as e:
                logger.error(f"Error verifying Firebase token: {e}")
                return None
        return None

firebase_service = FirebaseService()
