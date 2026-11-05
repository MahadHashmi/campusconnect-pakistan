import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    acronym = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    departments = relationship("Department", back_populates="university", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    university = relationship("University", back_populates="departments")
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    department = relationship("Department", back_populates="courses")
    resources = relationship("Resource", back_populates="course", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="SET NULL"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    semester = Column(Integer, default=1)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=False)  # 'past_paper', 'notes', 'slides'
    exam_type = Column(String(50), nullable=True)       # 'midterm', 'final', 'quiz'
    year = Column(Integer, nullable=True)
    file_url = Column(Text, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    downloads_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    course = relationship("Course", back_populates="resources")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String(150), default="Student")
    campus_name = Column(String(150), default="All Pakistan")
    content = Column(Text, nullable=False)
    media_url = Column(Text, nullable=True)
    media_type = Column(String(50), default="photo")  # 'photo', 'reel', 'text'
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class MarketplaceItem(Base):
    __tablename__ = "marketplace_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)            # In PKR, e.g. 1500
    category = Column(String(50), nullable=False)       # 'book', 'calculator', 'gig', 'hostel'
    image_url = Column(Text, nullable=True)
    seller_name = Column(String(150), nullable=False)
    whatsapp_number = Column(String(50), nullable=False) # e.g. "03001234567"
    campus_name = Column(String(150), default="PU • New Campus")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
