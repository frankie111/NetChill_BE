from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from firebase import get_auth, get_firestore_db, verify_token
from models import User

users = APIRouter()


# def register_user(email, password):
#     try:
#         user = get_auth().create_user(email=email, password=password)
#         print('Successfully created new user: {0}'.format(user.uid))
#         return user
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Error creating new user: {e}')


def save_user_data(user: User):
    try:
        db = get_firestore_db()
        user_ref = db.collection('users').document(user.uid)
        user_ref.set({
            'email': user.email,
            'name': user.name,
            'is_admin': user.is_admin
        })
        print('Successfully saved user data to Firestore')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error saving user data {e}')


def get_user_data_by_id(uid) -> User:
    try:
        db = get_firestore_db()
        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail=f"User {uid} doesn't exist")

        user_dict = user_doc.to_dict()
        return User(uid=uid, **user_dict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error retrieving user data {e}')


class AddUserModelResponse(BaseModel):
    message: str


@users.post(
    "/user/",
    tags=["Users"],
    response_model=AddUserModelResponse,
    description="Register a new user"
)
async def add_user(
        user_data: User,
        user: User = Depends(verify_token)
):
    user_data.is_admin = False
    save_user_data(user_data)
    return AddUserModelResponse(message=f"Added user {user.uid}")


class DeleteUserModelResponse(BaseModel):
    message: str


@users.delete(
    "/user/",
    tags=["Users"],
    response_model=DeleteUserModelResponse,
    description="Delete a user by id"
)
def delete_user(
        uid: str,
        user: User = Depends(verify_token)
):
    try:
        # Check if user is admin / user has permission to delete themselves:
        user_data = get_user_data_by_id(user.uid)
        if not user_data.is_admin and user_data.uid != uid:
            raise HTTPException(status_code=403, detail="User does not have permission to delete this user")

        # Delete user from Firebase Authentication
        get_auth().delete_user(uid)
        print('Successfully deleted user from Firebase Authentication')

        # Delete user data from Firestore
        db = get_firestore_db()
        user_ref = db.collection('users').document(uid)
        user_ref.delete()

        return DeleteUserModelResponse(message=f"User {uid} deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error deleting user: {e}')
