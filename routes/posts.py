from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from bson.objectid import ObjectId
from core.database import get_client
from models.post import Post
from fastapi.responses import StreamingResponse
from gridfs import GridFS
from urllib.parse import quote

router = APIRouter()

def get_db_client():
    try:
        return get_client()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API to fetch all posts
@router.get("")
def get_all_posts(db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers
        docs_cursor = db.whispers.find()
        posts = [
            {
                "id": str(doc["_id"]),
                "title": doc.get("title", "Untitled"),
                "author": doc.get("author", "Anonymous"),
                "description": doc.get("description", "No description available"),
                "genre": doc.get("genre", "General"),
                "fileUrl": doc.get("fileUrl", None),
            }
            for doc in docs_cursor
        ]
        if not posts:
            return {"message": "No posts found"}
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# API to create a new post
@router.post("/create")
def create_post(post: Post, db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers  # Access the database
        result = db.whispers.insert_one(post.dict())  # Insert the post into the collection
        return {"message": "Post created successfully", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# API to update an existing post
@router.put("/update/{post_id}")
def update_post(post_id: str, post: Post, db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers  # Access the database
        result = db.whispers.update_one(
            {"_id": ObjectId(post_id)},  # Filter by the ObjectId of the post
            {"$set": post.dict()}  # Update the post with the provided data
        )
        if result.matched_count == 0:  # If no documents matched, the post wasn't found
            raise HTTPException(status_code=404, detail="Post not found")
        return {"message": "Post updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# API to delete a post
@router.delete("/delete/{post_id}")
def delete_post(post_id: str, db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers  # Access the database
        result = db.whispers.delete_one({"_id": ObjectId(post_id)})  # Delete the post by its ObjectId
        if result.deleted_count == 0:  # If no documents were deleted, the post wasn't found
            raise HTTPException(status_code=404, detail="Post not found")
        return {"message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.post("/upload")
def upload_file(file: UploadFile = File(...), db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers
        fs = GridFS(db)

        file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)
        return {"message": "File uploaded successfully", "file_id": str(file_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.get("/file/{file_id}")
async def get_file(file_id: str, db_client=Depends(get_db_client)):
    try:
        db = db_client.whispers
        fs = GridFS(db)

        file = fs.get(ObjectId(file_id))

        safe_filename = quote(file.filename)

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
        }
        return StreamingResponse(file, headers=headers, media_type=file.content_type)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")