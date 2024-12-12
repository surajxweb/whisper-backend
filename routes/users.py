from typing import Dict

from fastapi import APIRouter, HTTPException, Depends
from core.database import get_client
from models.user import User
from pydantic import BaseModel

router = APIRouter()

def get_db_client():
    try:
        return get_client()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API to get new user
@router.post("/create")
def create_user(user:User, db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers
        user_data = user.dict()
        new_user = db.users.insert_one(user_data)
        return {"message": "User created successfully", "id": str(new_user.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")



# API to check if a user exists by user_key
@router.get("/key/{user_key}")
def verify_user_by_key(user_key: str, db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers
        user = db.users.find_one({"key": user_key})
        if user:
            return {"exists": True, "username": user.get("username")}
        else:
            return {"exists": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# API to check if a user exists by username
@router.get("/username/{username}")
def verify_user_by_username(username: str, db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers
        user = db.users.find_one({"username": username})
        if user:
            return {"exists": True, "key": user.get("key")}
        else:
            return {"exists": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


class UpdateRequest(BaseModel):
    user_key: str
    new_key: str

# API to replace an existing user key with a new one
@router.put("/key/update")
def update_user_key(update_request : UpdateRequest, db_client=Depends(get_db_client)):
    print("user_key --- ", update_request.user_key)
    print("new_key --- ", update_request.new_key)

    try:
        db = db_client.whispers
        result = db.users.update_one({"key": update_request.user_key}, {"$set": {"key": update_request.new_key}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User with the given key not found")
        return {"message": "User key updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


