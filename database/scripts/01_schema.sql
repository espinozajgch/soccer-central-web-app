-- =============================================
-- Soccer Central LMS - Simplified Database Schema
-- Learning Management System for Sports Education
-- =============================================
-- This schema supports educational courses for soccer academy personnel
-- including coaches, players, medical staff, physical trainers, and marketing teams.
-- Universities and academies can offer courses with certification.
-- =============================================

-- Drop existing tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS certificates;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS organizations;
DROP TABLE IF EXISTS users;

-- =============================================
-- Table: users
-- Description: Unified user table with role-based access
-- Roles: student, instructor, coach, admin
-- =============================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role ENUM('student', 'instructor', 'coach', 'admin') NOT NULL DEFAULT 'student',
    specialization VARCHAR(255) NULL COMMENT 'Area of expertise (e.g., Physical Training, Nutrition, Tactics)',
    organization_id VARCHAR(36) NULL COMMENT 'Reference to affiliated organization',
    profile_data JSON NULL COMMENT 'Additional profile information (phone, bio, certifications, etc.)',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_organization (organization_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Table: organizations
-- Description: Universities and sports academies offering courses
-- =============================================
CREATE TABLE organizations (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    type ENUM('university', 'academy', 'training_center', 'other') NOT NULL,
    location VARCHAR(255) NULL COMMENT 'City, State',
    contact_email VARCHAR(255) NULL,
    metadata JSON NULL COMMENT 'Additional organization info (website, accreditation, etc.)',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add foreign key for users -> organizations
ALTER TABLE users
    ADD CONSTRAINT fk_users_organization 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) 
    ON DELETE SET NULL;

-- =============================================
-- Table: courses
-- Description: Educational courses offered by universities/academies
-- Categories: Coaching, Management, Nutrition, Marketing, Medical, Physical Training
-- =============================================
CREATE TABLE courses (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category ENUM(
        'coaching', 
        'management', 
        'nutrition', 
        'marketing', 
        'medical', 
        'physical_training',
        'tactics',
        'psychology',
        'other'
    ) NOT NULL,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    duration_hours INT NOT NULL COMMENT 'Estimated course duration in hours',
    language VARCHAR(10) DEFAULT 'en' COMMENT 'Primary language (en, es, etc.)',
    organization_id VARCHAR(36) NOT NULL COMMENT 'University or academy offering the course',
    instructor_id VARCHAR(36) NULL COMMENT 'Primary instructor',
    thumbnail_url VARCHAR(512) NULL,
    metadata JSON NULL COMMENT 'Additional course info (prerequisites, recognition, external_program, etc.)',
    is_published BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_category (category),
    INDEX idx_organization (organization_id),
    INDEX idx_instructor (instructor_id),
    INDEX idx_published (is_published),
    INDEX idx_featured (is_featured)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Table: modules
-- Description: Course modules for organizing content
-- =============================================
CREATE TABLE modules (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    course_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    order_index INT NOT NULL COMMENT 'Display order within course',
    duration_hours DECIMAL(5,2) NULL COMMENT 'Estimated module duration',
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_course (course_id),
    INDEX idx_order (course_id, order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Table: lessons
-- Description: Individual lessons within modules
-- Supports multilingual content via JSON
-- =============================================
CREATE TABLE lessons (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    module_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content_type ENUM('video', 'text', 'quiz', 'assignment', 'document', 'interactive') NOT NULL,
    order_index INT NOT NULL COMMENT 'Display order within module',
    duration_minutes INT NULL COMMENT 'Estimated lesson duration',
    content JSON NOT NULL COMMENT 'Multilingual lesson content (text, video_url, quiz_data, etc.)',
    resources JSON NULL COMMENT 'Additional resources (downloads, links, etc.)',
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    INDEX idx_module (module_id),
    INDEX idx_order (module_id, order_index),
    INDEX idx_content_type (content_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Table: enrollments
-- Description: User course registrations with progress tracking
-- =============================================
CREATE TABLE enrollments (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    course_id VARCHAR(36) NOT NULL,
    status ENUM('enrolled', 'in_progress', 'completed', 'dropped') DEFAULT 'enrolled',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Overall course completion percentage',
    lessons_completed INT DEFAULT 0,
    total_lessons INT DEFAULT 0,
    last_accessed_lesson_id VARCHAR(36) NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (user_id, course_id),
    INDEX idx_user (user_id),
    INDEX idx_course (course_id),
    INDEX idx_status (status),
    INDEX idx_progress (progress_percentage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Table: certificates
-- Description: Digital certificates for completed courses
-- =============================================
CREATE TABLE certificates (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    enrollment_id VARCHAR(36) NOT NULL,
    certificate_number VARCHAR(50) UNIQUE NOT NULL COMMENT 'Unique certificate identifier',
    issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_url VARCHAR(512) NULL COMMENT 'Public verification URL',
    metadata JSON NULL COMMENT 'Certificate details (final_score, hours_completed, etc.)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
    INDEX idx_enrollment (enrollment_id),
    INDEX idx_certificate_number (certificate_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Table: reviews
-- Description: Course ratings and feedback from students
-- =============================================
CREATE TABLE reviews (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    course_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    rating DECIMAL(2,1) NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
    comment TEXT NULL,
    is_verified BOOLEAN DEFAULT FALSE COMMENT 'Only enrolled students can leave verified reviews',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_review (course_id, user_id),
    INDEX idx_course (course_id),
    INDEX idx_user (user_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Table: notifications
-- Description: User notification system for course updates and communications
-- =============================================
CREATE TABLE notifications (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    type ENUM('course_update', 'enrollment', 'certificate', 'announcement', 'reminder', 'other') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_id VARCHAR(36) NULL COMMENT 'Related entity ID (course, enrollment, etc.)',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_is_read (user_id, is_read),
    INDEX idx_type (type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Triggers for automatic progress tracking
-- =============================================

-- Trigger to generate unique certificate numbers
DELIMITER //
CREATE TRIGGER before_certificate_insert
BEFORE INSERT ON certificates
FOR EACH ROW
BEGIN
    IF NEW.certificate_number IS NULL OR NEW.certificate_number = '' THEN
        SET NEW.certificate_number = CONCAT('CERT-', YEAR(NOW()), '-', LPAD(FLOOR(RAND() * 999999), 6, '0'));
    END IF;
END//
DELIMITER ;

-- =============================================
-- Views for common queries
-- =============================================

-- View: Course statistics with enrollment and rating data
CREATE VIEW course_statistics AS
SELECT 
    c.id,
    c.title,
    c.category,
    c.organization_id,
    o.name AS organization_name,
    COUNT(DISTINCT e.id) AS total_enrollments,
    COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.id END) AS completed_enrollments,
    AVG(r.rating) AS average_rating,
    COUNT(DISTINCT r.id) AS total_reviews,
    c.is_published,
    c.created_at
FROM courses c
LEFT JOIN organizations o ON c.organization_id = o.id
LEFT JOIN enrollments e ON c.id = e.course_id
LEFT JOIN reviews r ON c.id = r.course_id
GROUP BY c.id, c.title, c.category, c.organization_id, o.name, c.is_published, c.created_at;

-- View: User learning progress
CREATE VIEW user_learning_progress AS
SELECT 
    u.id AS user_id,
    u.full_name,
    u.email,
    COUNT(DISTINCT e.id) AS total_enrollments,
    COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.id END) AS completed_courses,
    COUNT(DISTINCT cert.id) AS certificates_earned,
    AVG(e.progress_percentage) AS average_progress
FROM users u
LEFT JOIN enrollments e ON u.id = e.user_id
LEFT JOIN certificates cert ON e.id = cert.enrollment_id
WHERE u.role = 'student'
GROUP BY u.id, u.full_name, u.email;

-- =============================================
-- Comments and Documentation
-- =============================================

-- This schema provides:
-- 1. Unified user management with role-based access (student, instructor, coach, admin)
-- 2. Organization support for universities and academies
-- 3. Course management with categorization and multilingual support
-- 4. Structured learning paths via modules and lessons
-- 5. Enrollment tracking with automatic progress calculation
-- 6. Digital certification system
-- 7. Course review and rating system
-- 8. Notification system for user engagement

-- Compatible with MySQL 5.7+ and MariaDB 10.2+
-- Supports JSON data types for flexible metadata storage
-- Uses UTF-8 encoding for international character support
