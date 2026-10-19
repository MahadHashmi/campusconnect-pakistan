-- ========================================================
-- CampusConnect MVP: Lightweight PostgreSQL Database Schema
-- Optimized for Free Tier (Supabase / Neon.tech)
-- ========================================================

-- Enable UUID extension (built-in for PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. UNIVERSITIES
CREATE TABLE IF NOT EXISTS universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    acronym VARCHAR(50) NOT NULL,            -- e.g., 'PU', 'NUST', 'FAST'
    city VARCHAR(100) NOT NULL,               -- e.g., 'Lahore', 'Islamabad'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. DEPARTMENTS
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    university_id INT NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,               -- e.g., 'Faculty of Computing & Information Technology'
    code VARCHAR(50) NOT NULL,                -- e.g., 'FCIT', 'CS'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. COURSES / SUBJECTS
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    department_id INT NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,               -- e.g., 'Data Structures & Algorithms'
    code VARCHAR(50) NOT NULL,                -- e.g., 'CS-201'
    semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. USERS (STUDENTS)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    university_id INT REFERENCES universities(id) ON DELETE SET NULL,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    semester INT DEFAULT 1 CHECK (semester BETWEEN 1 AND 8),
    avatar_url TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. ACADEMIC RESOURCES (Past Papers, Notes, Slides)
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,              -- e.g., 'DSA Midterm 2023 Solved Paper'
    resource_type VARCHAR(50) NOT NULL,       -- 'past_paper', 'notes', 'slides'
    exam_type VARCHAR(50) DEFAULT NULL,       -- 'midterm', 'final', 'quiz'
    year INT DEFAULT NULL,                    -- e.g., 2023, 2024
    file_url TEXT NOT NULL,                   -- Hosted link (Cloudinary / Supabase Storage)
    course_id INT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    downloads_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. CAMPUS POSTS / Q&A FEED
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    university_id INT NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. COMMENTS / REPLIES
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- INDEXES FOR INSTANT QUERY SPEED
-- ========================================================
CREATE INDEX IF NOT EXISTS idx_courses_dept_sem ON courses(department_id, semester);
CREATE INDEX IF NOT EXISTS idx_resources_course ON resources(course_id);
CREATE INDEX IF NOT EXISTS idx_posts_uni_dept ON posts(university_id, department_id);
