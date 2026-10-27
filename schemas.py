from typing import Optional, List
import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime

# 1. Course Schemas
class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    semester: int

    class Config:
        from_attributes = True

# 2. Resource Schemas
class ResourceResponse(BaseModel):
    id: int
    title: str
    resource_type: str
    exam_type: Optional[str] = None
    year: Optional[int] = None
    file_url: str
    course_id: int
    downloads_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResourceCreateRequest(BaseModel):
    title: str
    resource_type: str  # 'past_paper', 'notes', 'slides'
    exam_type: Optional[str] = None  # 'midterm', 'final', 'quiz'
    year: Optional[int] = 2024
    file_url: str
    course_id: int

# 3. University Schemas
class UniversityResponse(BaseModel):
    id: int
    name: str
    acronym: str
    city: str

    class Config:
        from_attributes = True

# 4. User / Auth Schemas
class UserRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    university_name: Optional[str] = "Punjab University (PU)"
    department_name: Optional[str] = "Computer Science"
    university_id: Optional[int] = 1
    department_id: Optional[int] = 1
    semester: int = 1

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    semester: int
    university_id: Optional[int] = None
    department_id: Optional[int] = None
    university_name: Optional[str] = "Punjab University (PU)"
    department_name: Optional[str] = "Computer Science"

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# 5. Social Feed Post Schemas
class PostCreateRequest(BaseModel):
    author_name: Optional[str] = "Student"
    campus_name: Optional[str] = "PU • New Campus"
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = "photo"

class PostResponse(BaseModel):
    id: int
    author_name: str
    campus_name: str
    content: str
    media_url: Optional[str] = None
    media_type: str
    likes_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# 6. Marketplace Item Schemas
class MarketplaceCreateRequest(BaseModel):
    title: str
    description: str
    price: int
    category: str  # 'book', 'calculator', 'gig', 'hostel'
    image_url: Optional[str] = None
    seller_name: str
    whatsapp_number: str
    campus_name: Optional[str] = "PU • New Campus"

class MarketplaceResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    category: str
    image_url: Optional[str] = None
    seller_name: str
    whatsapp_number: str
    campus_name: str
    created_at: datetime

    class Config:
        from_attributes = True
