"""Firestore-backed implementation of user storage."""
from typing import Optional
from google.cloud.firestore import Client as FirestoreClient
from src.objects.user import User
from src.storage.user import UserStorage

USERS_COLLECTION = "users"


class FirestoreUserStorage(UserStorage):
    """Stores users as documents in a Firestore `users` collection, keyed by user id."""

    def __init__(self, client: FirestoreClient):
        self.__client = client

    def get(self, user_id: str) -> Optional[User]:
        snapshot = self.__client.collection(USERS_COLLECTION).document(user_id).get()
        if not snapshot.exists:
            return None
        return User(**snapshot.to_dict())

    def create(self, user: User) -> User:
        self.__client.collection(USERS_COLLECTION).document(user.id).set(user.model_dump())
        return user

    def update(self, user: User) -> User:
        self.__client.collection(USERS_COLLECTION).document(user.id).set(user.model_dump(), merge=True)
        return user

    def delete(self, user_id: str) -> None:
        self.__client.collection(USERS_COLLECTION).document(user_id).delete()
