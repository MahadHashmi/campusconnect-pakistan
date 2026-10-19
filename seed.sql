-- ========================================================
-- Seed Data for Testing (University of the Punjab - FCIT example)
-- Run this after running schema.sql
-- ========================================================

-- Insert University
INSERT INTO universities (id, name, acronym, city) 
VALUES (1, 'University of the Punjab', 'PU', 'Lahore')
ON CONFLICT (id) DO NOTHING;

-- Insert Department
INSERT INTO departments (id, university_id, name, code)
VALUES (1, 1, 'Faculty of Computing & Information Technology', 'FCIT')
ON CONFLICT (id) DO NOTHING;

-- Insert Common BS Courses (Semesters 1-4)
INSERT INTO courses (department_id, name, code, semester) VALUES
-- Semester 1
(1, 'Programming Fundamentals', 'CS-101', 1),
(1, 'Introduction to ICT', 'CS-102', 1),
(1, 'Calculus & Analytical Geometry', 'MATH-101', 1),

-- Semester 2
(1, 'Object Oriented Programming', 'CS-103', 2),
(1, 'Digital Logic Design', 'CS-104', 2),
(1, 'Discrete Structures', 'MATH-102', 2),

-- Semester 3
(1, 'Data Structures & Algorithms', 'CS-201', 3),
(1, 'Computer Organization & Assembly', 'CS-202', 3),
(1, 'Linear Algebra', 'MATH-201', 3),

-- Semester 4
(1, 'Database Systems', 'CS-203', 4),
(1, 'Operating Systems', 'CS-204', 4),
(1, 'Software Engineering', 'SE-201', 4);

-- Sample Resource Entry
INSERT INTO resources (title, resource_type, exam_type, year, file_url, course_id)
VALUES 
('DSA Midterm Past Paper 2023 Solved', 'past_paper', 'midterm', 2023, 'https://example.com/sample_dsa_midterm.pdf', 7),
('Database Systems Normalization Quick Notes', 'notes', NULL, 2024, 'https://example.com/sample_db_notes.pdf', 10);
