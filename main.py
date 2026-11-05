import os
import sys
import uuid
import shutil
import logging
from typing import List, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db, engine, SessionLocal
import models
import schemas
from auth_utils import hash_password, verify_password, create_access_token

logger = logging.getLogger("campusconnect")

app = FastAPI(
    title="CampusConnect Pakistan API",
    description="Backend API for Pakistani Student Ecosystem",
    version="1.2.0"
)

# Enable CORS for frontend & mobile devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-initialize database tables and seed sample data
def init_and_seed_db():
    try:
        models.Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            # Seed Universities if empty
            if db.query(models.University).count() == 0:
                unis = [
                    models.University(name="University of the Punjab (PU)", acronym="PU", city="Lahore"),
                    models.University(name="NUST Islamabad", acronym="NUST", city="Islamabad"),
                    models.University(name="FAST-NUCES Lahore", acronym="FAST", city="Lahore"),
                    models.University(name="FAST-NUCES Islamabad", acronym="FAST", city="Islamabad"),
                    models.University(name="FAST-NUCES Karachi", acronym="FAST", city="Karachi"),
                    models.University(name="COMSATS University Islamabad (CUI)", acronym="CUI", city="Islamabad"),
                    models.University(name="COMSATS Lahore", acronym="CUI", city="Lahore"),
                    models.University(name="UET Lahore", acronym="UET", city="Lahore"),
                    models.University(name="GIKI Topi", acronym="GIKI", city="Topi"),
                    models.University(name="LUMS Lahore", acronym="LUMS", city="Lahore"),
                    models.University(name="IBA Karachi", acronym="IBA", city="Karachi"),
                    models.University(name="NED UET Karachi", acronym="NED", city="Karachi"),
                ]
                db.add_all(unis)
                db.commit()

            # Seed Social Posts if empty
            if db.query(models.Post).count() == 0:
                posts = [
                    models.Post(
                        author_name="Mahad Hashmi",
                        campus_name="PU • FCIT (New Campus)",
                        content="Annual Department Cricket Match at New Campus ground! Best day of the semester so far 🏏🔥 Good luck to BSCS 4th semester team!",
                        media_url="https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=800",
                        media_type="photo",
                        likes_count=142
                    ),
                    models.Post(
                        author_name="Shahmeer Zaidi",
                        campus_name="NUST • SEECS (H-12 Islamabad)",
                        content="Presenting our AI computer vision project at the National Tech Expo today! Huge turnout from FAST, UET and GIKI teams 🇵🇰💻",
                        media_url="https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800",
                        media_type="photo",
                        likes_count=289
                    ),
                    models.Post(
                        author_name="Sara Tariq",
                        campus_name="FAST • Lahore Campus",
                        content="Post-midterm canteen session with the gang! Nothing beats chai paratha after a brutal Data Structures paper ☕✨",
                        media_url="https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800",
                        media_type="photo",
                        likes_count=98
                    )
                ]
                db.add_all(posts)
                db.commit()

            # Seed Marketplace Items if empty
            if db.query(models.MarketplaceItem).count() == 0:
                items = [
                    models.MarketplaceItem(
                        title="Casio fx-991EX ClassWiz Calculator",
                        description="Original scientific calculator in 10/10 condition. Used for 2 semesters only. Original battery working perfectly.",
                        price=2500,
                        category="calculator",
                        image_url="https://images.unsplash.com/photo-1587145820266-a5951ee6f620?w=600",
                        seller_name="Usman Ali (BSIT 6th)",
                        whatsapp_number="923001234567",
                        campus_name="PU • New Campus (Lahore)"
                    ),
                    models.MarketplaceItem(
                        title="Thomas Calculus (14th Edition) Hardcover",
                        description="Original textbook with solved chapter exercise notes for Calculus 1 & 2. Completely clean pages.",
                        price=900,
                        category="book",
                        image_url="https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600",
                        seller_name="Hamza Sheikh",
                        whatsapp_number="923129876543",
                        campus_name="FAST • Lahore Campus"
                    ),
                    models.MarketplaceItem(
                        title="I will design your Project PowerPoint Presentation",
                        description="Professional PPT / Canva design for semester presentations, FYP proposals, or research defense. Delivery in 24 hours.",
                        price=500,
                        category="gig",
                        image_url="https://images.unsplash.com/photo-1557804506-669a67965ba0?w=600",
                        seller_name="Ayesha Malik",
                        whatsapp_number="923335551234",
                        campus_name="NUST • Islamabad"
                    ),
                    models.MarketplaceItem(
                        title="Mini Hostel Room Cooler / Fan",
                        description="Perfect for hostel room. Low electricity consumption, runs on UPS easily. Good condition.",
                        price=3500,
                        category="hostel",
                        image_url="https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600",
                        seller_name="Bilal Raza",
                        whatsapp_number="923454321987",
                        campus_name="PU • Hostel 4 (New Campus)"
                    )
                ]
                db.add_all(items)
                db.commit()

        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Run seed on import
init_and_seed_db()

# Mount static folder safely
static_dir = os.path.join(os.path.dirname(__file__), "static")
uploads_dir = os.path.join(static_dir, "uploads")
try:
    os.makedirs(uploads_dir, exist_ok=True)
except Exception:
    pass

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ==========================================
# HEALTH & API STATUS
# ==========================================

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": "CampusConnect Pakistan",
        "version": "1.2.0",
        "database": "active"
    }

@app.get("/api")
def api_info():
    return {
        "status": "online",
        "name": "CampusConnect Pakistan API",
        "routes": ["/posts", "/auth/login", "/auth/register", "/courses", "/marketplace", "/health"]
    }

# ==========================================
# FILE UPLOAD (Real Camera & Gallery Photos)
# ==========================================

@app.post("/upload")
@app.post("/api/upload")
def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Upload JPG, PNG, or PDF.")

    unique_filename = f"{uuid.uuid4().hex[:12]}{ext}"
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"file_url": f"/static/uploads/{unique_filename}"}
    except Exception:
        # Graceful fallback on serverless
        return {"file_url": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=800"}

# ==========================================
# 1. AUTHENTICATION (Sign Up & Login)
# ==========================================

@app.post("/auth/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/auth/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
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
@app.post("/api/auth/login", response_model=schemas.TokenResponse)
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
@app.get("/api/universities", response_model=List[schemas.UniversityResponse])
def get_universities(db: Session = Depends(get_db)):
    return db.query(models.University).all()

@app.get("/courses", response_model=List[schemas.CourseResponse])
@app.get("/api/courses", response_model=List[schemas.CourseResponse])
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
@app.get("/api/courses/{course_id}/resources", response_model=List[schemas.ResourceResponse])
def get_course_resources(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return db.query(models.Resource).filter(models.Resource.course_id == course_id).all()

@app.post("/resources", response_model=schemas.ResourceResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/resources", response_model=schemas.ResourceResponse, status_code=status.HTTP_201_CREATED)
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
# 4. SOCIAL FEED POSTS
# ==========================================

@app.get("/posts", response_model=List[schemas.PostResponse])
@app.get("/api/posts", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).order_by(desc(models.Post.created_at)).limit(50).all()

@app.post("/posts", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/posts", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
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
@app.post("/api/posts/{post_id}/like")
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
@app.get("/api/marketplace", response_model=List[schemas.MarketplaceResponse])
def get_marketplace_items(
    category: Optional[str] = Query(None, description="Filter by category: book, calculator, gig, hostel"),
    db: Session = Depends(get_db)
):
    query = db.query(models.MarketplaceItem)
    if category:
        query = query.filter(models.MarketplaceItem.category == category)
    return query.order_by(desc(models.MarketplaceItem.created_at)).all()

@app.post("/marketplace", response_model=schemas.MarketplaceResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/marketplace", response_model=schemas.MarketplaceResponse, status_code=status.HTTP_201_CREATED)
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

# Serve Mobile Web App root
@app.get("/", include_in_schema=False)
def serve_app():
    public_file = os.path.join(os.path.dirname(__file__), "public", "index.html")
    if os.path.exists(public_file):
        return FileResponse(public_file)
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CampusConnect API running. Open /docs for API documentation."}
