import os
import sys
import uuid
import shutil
from typing import List, Optional

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db, engine
import models
import schemas
from auth_utils import hash_password, verify_password, create_access_token

# Automatically create tables if not existing (graceful on serverless cold starts)
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Table verification skipped or completed: {e}")

app = FastAPI(
    title="CampusConnect API",
    description="Backend API for Pakistani Student Ecosystem MVP",
    version="1.0.0"
)

# Enable CORS so frontend/mobile app can communicate freely with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder
static_dir = os.path.join(os.path.dirname(__file__), "static")
uploads_dir = os.path.join(static_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve the Mobile Web App at the root URL
@app.get("/", include_in_schema=False)
def serve_app():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CampusConnect API running. Open /docs for API documentation."}

# ==========================================
# FILE UPLOAD (Real Camera & Gallery Photos)
# ==========================================

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Upload JPG, PNG, or PDF.")

    unique_filename = f"{uuid.uuid4().hex[:12]}{ext}"
    file_path = os.path.join(uploads_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"file_url": f"/static/uploads/{unique_filename}"}

# ==========================================
# 1. AUTHENTICATION (Sign Up & Login)
# ==========================================

@app.post("/auth/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    hashed_pwd = hash_password(user_data.password)

    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_pwd,
        university_id=user_data.university_id,
        department_id=user_data.department_id,
        semester=user_data.semester
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id), "email": new_user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user
    }

@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token({"sub": str(user.id), "email": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

# ==========================================
# 2. COURSES & ACADEMIC DIRECTORY
# ==========================================

@app.get("/universities", response_model=List[schemas.UniversityResponse])
def get_universities(db: Session = Depends(get_db)):
    return db.query(models.University).all()

@app.get("/courses", response_model=List[schemas.CourseResponse])
def get_courses(
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester (1-8)"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Course)
    if semester is not None:
        query = query.filter(models.Course.semester == semester)
    return query.all()

# ==========================================
# 3. PAST PAPERS & ACADEMIC VAULT
# ==========================================

@app.get("/courses/{course_id}/resources", response_model=List[schemas.ResourceResponse])
def get_course_resources(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return db.query(models.Resource).filter(models.Resource.course_id == course_id).all()

@app.post("/resources", response_model=schemas.ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(resource_data: schemas.ResourceCreateRequest, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == resource_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course does not exist")

    new_resource = models.Resource(
        title=resource_data.title,
        resource_type=resource_data.resource_type,
        exam_type=resource_data.exam_type,
        year=resource_data.year,
        file_url=resource_data.file_url,
        course_id=resource_data.course_id
    )

    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return new_resource

# ==========================================
# 4. SOCIAL FEED POSTS (Persistent in Supabase)
# ==========================================

@app.get("/posts", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).order_by(desc(models.Post.created_at)).limit(50).all()

@app.post("/posts", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post_data: schemas.PostCreateRequest, db: Session = Depends(get_db)):
    new_post = models.Post(
        author_name=post_data.author_name or "Student",
        campus_name=post_data.campus_name or "PU • New Campus",
        content=post_data.content,
        media_url=post_data.media_url,
        media_type=post_data.media_type or "photo",
        likes_count=1
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes_count += 1
    db.commit()
    return {"id": post.id, "likes_count": post.likes_count}

# ==========================================
# 5. STUDENT MARKETPLACE (Hostel OLX & Micro-gigs)
# ==========================================

@app.get("/marketplace", response_model=List[schemas.MarketplaceResponse])
def get_marketplace_items(
    category: Optional[str] = Query(None, description="Filter by category: book, calculator, gig, hostel"),
    db: Session = Depends(get_db)
):
    query = db.query(models.MarketplaceItem)
    if category:
        query = query.filter(models.MarketplaceItem.category == category)
    return query.order_by(desc(models.MarketplaceItem.created_at)).all()

@app.post("/marketplace", response_model=schemas.MarketplaceResponse, status_code=status.HTTP_201_CREATED)
def create_marketplace_item(item_data: schemas.MarketplaceCreateRequest, db: Session = Depends(get_db)):
    new_item = models.MarketplaceItem(
        title=item_data.title,
        description=item_data.description,
        price=item_data.price,
        category=item_data.category,
        image_url=item_data.image_url,
        seller_name=item_data.seller_name,
        whatsapp_number=item_data.whatsapp_number,
        campus_name=item_data.campus_name or "PU • New Campus"
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item
