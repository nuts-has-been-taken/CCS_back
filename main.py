from fastapi import FastAPI, UploadFile, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from minio import Minio
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

load_dotenv()
minio_url = os.getenv("MINIO_URL")
minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_bucket_name = "file"

MINIO_CLIENT = Minio(endpoint=minio_url,
                     access_key=minio_access_key,
                     secret_key=minio_secret_key,
                     secure=False)
    
if not MINIO_CLIENT.bucket_exists(minio_bucket_name):
    MINIO_CLIENT.make_bucket(minio_bucket_name)
    print(f"Bucket '{minio_bucket_name}' created successfully.")
else:
    print(f"Bucket '{minio_bucket_name}' already exists.")

@app.get("/")
def read_root():
    return {"message": "Cloud MinIO class hw1"}

@app.post("/upload")
def upload_file(file: UploadFile):
    try:
        remote_file_name = f"{file.filename}"
        
        MINIO_CLIENT.put_object(
            bucket_name="file",
            object_name=remote_file_name,
            data=file.file,
            length=file.size,
            content_type=file.content_type,
        )
        return {"message": f"File '{file.filename}' uploaded successfully as '{remote_file_name}'."}
    except Exception as e:
        return {"error": f"Error uploading file: {e}"}

@app.get("/download/{file_name}")
def download_file(file_name: str):
    try:
        response = MINIO_CLIENT.get_object("file", file_name)
        res = Response(content=response.read())
        return res
    except Exception as e:
        return {"error": f"Error downloading file: {e}"}

@app.get("/download")
def get_all_file():
    try:
        objects = MINIO_CLIENT.list_objects("file")
        file_names = [obj.object_name for obj in objects]
        return {"data":file_names}
    except Exception as e:
        return {"error": f"Error get file: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)