-- =============================================
-- Soccer Central LMS - Sample Data Script
-- =============================================
-- This script populates the database with sample data including:
-- - US universities and academies
-- - Sample users (admins, instructors, students)
-- - Sample courses with modules and lessons
-- =============================================

-- =============================================
-- Organizations - US Universities and Academies
-- =============================================

INSERT INTO organizations (id, name, type, location, contact_email, metadata) VALUES
-- Major Texas Universities
('org-001', 'University of Texas at San Antonio (UTSA)', 'university', 'San Antonio, TX', 'sports@utsa.edu', 
 '{"website": "https://www.utsa.edu", "accreditation": "SACS", "sports_programs": ["soccer", "athletic_training", "kinesiology"]}'),

('org-002', 'Texas A&M University', 'university', 'College Station, TX', 'athletics@tamu.edu',
 '{"website": "https://www.tamu.edu", "accreditation": "SACS", "sports_programs": ["sport_management", "exercise_science", "coaching"]}'),

('org-003', 'Southern Methodist University (SMU)', 'university', 'Dallas, TX', 'sports@smu.edu',
 '{"website": "https://www.smu.edu", "accreditation": "SACS", "sports_programs": ["sport_management", "business_sports", "coaching"]}'),

('org-004', 'University of Houston', 'university', 'Houston, TX', 'athletics@uh.edu',
 '{"website": "https://www.uh.edu", "accreditation": "SACS", "sports_programs": ["sport_administration", "athletic_training"]}'),

('org-005', 'St. Mary''s University', 'university', 'San Antonio, TX', 'sports@stmarytx.edu',
 '{"website": "https://www.stmarytx.edu", "accreditation": "SACS", "sports_programs": ["sport_management", "coaching"]}'),

-- Soccer Academies
('org-006', 'Soccer Central Academy', 'academy', 'San Antonio, TX', 'info@soccercentral.com',
 '{"website": "https://www.soccercentral.com", "founded": "2010", "focus": "youth_development", "programs": ["MLS_Next", "training", "education"]}'),

('org-007', 'FC Dallas Youth Academy', 'academy', 'Frisco, TX', 'youth@fcdallas.com',
 '{"website": "https://www.fcdallas.com/youth", "affiliation": "MLS", "programs": ["MLS_Next", "residential"]}'),

('org-008', 'Houston Dynamo Youth Academy', 'academy', 'Houston, TX', 'youth@houstondynamo.com',
 '{"website": "https://www.houstondynamofc.com/youth", "affiliation": "MLS", "programs": ["MLS_Next", "development"]}');

-- =============================================
-- Users - Admins, Instructors, Coaches, Students
-- =============================================

-- Note: Password hashes should be generated using bcrypt in production
-- These are example hashes for password "password123"

-- Admin Users
INSERT INTO users (id, email, password_hash, full_name, role, organization_id, profile_data) VALUES
('user-001', 'admin@soccercentral.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'John Administrator', 'admin', 'org-006',
 '{"phone": "+1-210-555-0100", "bio": "Platform administrator with 10+ years in sports education"}');

-- University Instructors
INSERT INTO users (id, email, password_hash, full_name, role, specialization, organization_id, profile_data) VALUES
('user-002', 'dr.smith@utsa.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Dr. Sarah Smith', 'instructor', 'Sport Management', 'org-001',
 '{"phone": "+1-210-555-0101", "bio": "PhD in Sport Management, 15 years teaching experience", "credentials": ["PhD", "NASM-CPT"]}'),

('user-003', 'coach.rodriguez@tamu.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Carlos Rodriguez', 'instructor', 'Coaching Methodology', 'org-002',
 '{"phone": "+1-979-555-0102", "bio": "Former professional soccer coach, UEFA A License", "credentials": ["UEFA_A", "MS_Kinesiology"]}'),

('user-004', 'prof.johnson@smu.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Dr. Michael Johnson', 'instructor', 'Sports Marketing', 'org-003',
 '{"phone": "+1-214-555-0103", "bio": "Sports Marketing specialist with MBA and 20 years industry experience", "credentials": ["PhD_Marketing", "MBA"]}'),

('user-005', 'dr.garcia@uh.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Dr. Maria Garcia', 'instructor', 'Exercise Science', 'org-004',
 '{"phone": "+1-713-555-0104", "bio": "Exercise Physiologist and Athletic Trainer", "credentials": ["PhD_Exercise_Science", "CSCS", "ATC"]}'),

('user-006', 'dr.kim@stmarytx.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Dr. Jennifer Kim', 'instructor', 'Sports Nutrition', 'org-005',
 '{"phone": "+1-210-555-0105", "bio": "Registered Dietitian specializing in sports nutrition", "credentials": ["PhD_Nutrition", "RD", "CSSD"]}');

-- Academy Coaches
INSERT INTO users (id, email, password_hash, full_name, role, specialization, organization_id, profile_data) VALUES
('user-007', 'coach.martinez@soccercentral.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Roberto Martinez', 'coach', 'Youth Development', 'org-006',
 '{"phone": "+1-210-555-0106", "bio": "Head coach with USSF A License, 12 years youth soccer", "credentials": ["USSF_A", "UEFA_B"]}'),

('user-008', 'coach.thompson@fcdallas.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'David Thompson', 'coach', 'Tactical Training', 'org-007',
 '{"phone": "+1-469-555-0107", "bio": "Former MLS player, now coaching academy teams", "credentials": ["USSF_A", "MS_Sport_Management"]}');

-- Students (Academy staff and players)
INSERT INTO users (id, email, password_hash, full_name, role, specialization, organization_id, profile_data) VALUES
('user-009', 'alex.student@soccercentral.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Alex Turner', 'student', NULL, 'org-006',
 '{"phone": "+1-210-555-0108", "bio": "Assistant coach pursuing coaching certification", "position": "assistant_coach"}'),

('user-010', 'emma.player@soccercentral.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Emma Wilson', 'student', NULL, 'org-006',
 '{"phone": "+1-210-555-0109", "bio": "U17 player interested in sports medicine", "position": "player", "age": 16}'),

('user-011', 'james.medical@soccercentral.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'James Cooper', 'student', NULL, 'org-006',
 '{"phone": "+1-210-555-0110", "bio": "Athletic trainer seeking advanced certifications", "position": "medical_staff"}'),

('user-012', 'lisa.marketing@soccercentral.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lshE3hL', 'Lisa Chen', 'student', NULL, 'org-006',
 '{"phone": "+1-210-555-0111", "bio": "Marketing coordinator learning sports marketing", "position": "marketing_staff"}');

-- =============================================
-- Courses
-- =============================================

-- Coaching Courses
INSERT INTO courses (id, title, description, category, difficulty_level, duration_hours, language, organization_id, instructor_id, metadata, is_published, is_featured) VALUES
('course-001', 'Fundamentals of Youth Soccer Coaching', 
 'Comprehensive introduction to coaching youth soccer players, covering technical skills, tactical awareness, and age-appropriate training methods.',
 'coaching', 'beginner', 40, 'en', 'org-002', 'user-003',
 '{"prerequisites": [], "recognition": "Texas A&M University Certificate", "external_program": "NCAA Coaching Education", "learning_outcomes": ["Understand youth development stages", "Design age-appropriate training sessions", "Implement effective coaching communication"]}',
 TRUE, TRUE),

('course-002', 'Advanced Tactical Analysis in Soccer',
 'Deep dive into tactical systems, game analysis, and strategic planning for competitive soccer teams.',
 'coaching', 'advanced', 60, 'en', 'org-002', 'user-003',
 '{"prerequisites": ["Coaching License"], "recognition": "Texas A&M Advanced Certificate", "tools": ["Video analysis software", "Tactical boards"], "learning_outcomes": ["Analyze game formations", "Develop tactical game plans", "Adapt strategies in real-time"]}',
 TRUE, TRUE);

-- Management Courses
INSERT INTO courses (id, title, description, category, difficulty_level, duration_hours, language, organization_id, instructor_id, metadata, is_published, is_featured) VALUES
('course-003', 'Sports Organization Management',
 'Learn to manage soccer academies, clubs, and sports organizations effectively, covering operations, budgeting, and staff management.',
 'management', 'intermediate', 50, 'en', 'org-001', 'user-002',
 '{"prerequisites": [], "recognition": "UTSA Sport Management Certificate", "topics": ["Operations Management", "Financial Planning", "Human Resources"], "learning_outcomes": ["Develop operational plans", "Create budgets", "Manage teams effectively"]}',
 TRUE, FALSE);

-- Marketing Courses
INSERT INTO courses (id, title, description, category, difficulty_level, duration_hours, language, organization_id, instructor_id, metadata, is_published, is_featured) VALUES
('course-004', 'Digital Marketing for Sports Organizations',
 'Master digital marketing strategies specific to sports organizations, including social media, content creation, and fan engagement.',
 'marketing', 'intermediate', 35, 'en', 'org-003', 'user-004',
 '{"prerequisites": [], "recognition": "SMU Sports Marketing Certificate", "tools": ["Social media platforms", "Analytics tools", "Content management systems"], "learning_outcomes": ["Create digital marketing campaigns", "Analyze engagement metrics", "Build brand awareness"]}',
 TRUE, TRUE);

-- Medical/Athletic Training Courses
INSERT INTO courses (id, title, description, category, difficulty_level, duration_hours, language, organization_id, instructor_id, metadata, is_published, is_featured) VALUES
('course-005', 'Sports Injury Prevention and Management',
 'Comprehensive course on preventing, identifying, and managing common soccer injuries for athletic trainers and medical staff.',
 'medical', 'intermediate', 45, 'en', 'org-004', 'user-005',
 '{"prerequisites": ["Basic anatomy knowledge"], "recognition": "University of Houston Athletic Training Certificate", "certification_prep": "BOC_AT", "learning_outcomes": ["Identify injury risks", "Implement prevention protocols", "Manage acute injuries"]}',
 TRUE, FALSE);

-- Nutrition Courses
INSERT INTO courses (id, title, description, category, difficulty_level, duration_hours, language, organization_id, instructor_id, metadata, is_published, is_featured) VALUES
('course-006', 'Performance Nutrition for Soccer Athletes',
 'Evidence-based nutrition strategies to optimize performance, recovery, and health for soccer players of all levels.',
 'nutrition', 'beginner', 30, 'en', 'org-005', 'user-006',
 '{"prerequisites": [], "recognition": "St. Mary''s Sports Nutrition Certificate", "topics": ["Macronutrient timing", "Hydration strategies", "Supplementation"], "learning_outcomes": ["Design nutrition plans", "Time nutrient intake", "Support recovery"]}',
 TRUE, FALSE);

-- Physical Training Courses
INSERT INTO courses (id, title, description, category, difficulty_level, duration_hours, language, organization_id, instructor_id, metadata, is_published, is_featured) VALUES
('course-007', 'Strength and Conditioning for Soccer',
 'Develop comprehensive strength and conditioning programs specifically designed for soccer players to enhance performance and reduce injuries.',
 'physical_training', 'intermediate', 55, 'en', 'org-004', 'user-005',
 '{"prerequisites": [], "recognition": "University of Houston Performance Training Certificate", "certification_prep": "CSCS", "learning_outcomes": ["Design periodized programs", "Assess athletic performance", "Prevent overtraining"]}',
 TRUE, TRUE);

-- =============================================
-- Modules for Course 001 (Youth Soccer Coaching)
-- =============================================

INSERT INTO modules (id, course_id, title, description, order_index, duration_hours) VALUES
('mod-001-01', 'course-001', 'Introduction to Youth Development', 
 'Understanding the physical, cognitive, and emotional development of youth soccer players.',
 1, 8),

('mod-001-02', 'course-001', 'Technical Skills Training',
 'Teaching fundamental technical skills: dribbling, passing, shooting, and ball control.',
 2, 12),

('mod-001-03', 'course-001', 'Age-Appropriate Training Methods',
 'Designing training sessions that match developmental stages and maintain engagement.',
 3, 10),

('mod-001-04', 'course-001', 'Communication and Leadership',
 'Effective communication strategies and building positive coach-player relationships.',
 4, 10);

-- =============================================
-- Lessons for Module 001-01 (Introduction to Youth Development)
-- =============================================

INSERT INTO lessons (id, module_id, title, content_type, order_index, duration_minutes, content, resources) VALUES
('lesson-001-01-01', 'mod-001-01', 'Physical Development Stages', 'video', 1, 30,
 '{"en": {"video_url": "https://example.com/videos/physical-development", "transcript": "Understanding how children''s bodies develop...", "key_points": ["Growth spurts", "Motor skill development", "Coordination progression"]}}',
 '{"downloads": ["Physical Development Chart PDF"], "external_links": [{"title": "CDC Growth Charts", "url": "https://cdc.gov/growthcharts"}]}'),

('lesson-001-01-02', 'mod-001-01', 'Cognitive Development in Youth', 'text', 2, 25,
 '{"en": {"html_content": "<h2>Cognitive Development</h2><p>Young players progress through distinct cognitive stages...</p>", "key_concepts": ["Piaget''s stages", "Decision-making ability", "Understanding tactics"]}}',
 '{"downloads": ["Cognitive Development Guide PDF"]}'),

('lesson-001-01-03', 'mod-001-01', 'Emotional and Social Development', 'video', 3, 35,
 '{"en": {"video_url": "https://example.com/videos/emotional-development", "transcript": "The emotional needs of youth athletes...", "key_points": ["Team dynamics", "Handling pressure", "Building confidence"]}}',
 '{"downloads": ["Social-Emotional Learning Checklist PDF"]}'),

('lesson-001-01-04', 'mod-001-01', 'Module 1 Assessment', 'quiz', 4, 20,
 '{"en": {"questions": [{"id": 1, "question": "At what age do most children develop the coordination for complex soccer skills?", "type": "multiple_choice", "options": ["6-8 years", "9-11 years", "12-14 years", "15-17 years"], "correct_answer": "9-11 years"}, {"id": 2, "question": "Why is understanding cognitive development important for coaching?", "type": "essay", "word_limit": 200}]}}',
 '{}');

-- =============================================
-- Enrollments
-- =============================================

INSERT INTO enrollments (id, user_id, course_id, status, progress_percentage, lessons_completed, total_lessons, enrolled_at) VALUES
-- Alex (Assistant Coach) enrolled in Youth Coaching
('enroll-001', 'user-009', 'course-001', 'in_progress', 45.5, 18, 40, DATE_SUB(NOW(), INTERVAL 30 DAY)),

-- Emma (Player) enrolled in Sports Injury Prevention
('enroll-002', 'user-010', 'course-005', 'in_progress', 20.0, 8, 35, DATE_SUB(NOW(), INTERVAL 15 DAY)),

-- James (Medical Staff) enrolled in Sports Injury Prevention - Completed
('enroll-003', 'user-011', 'course-005', 'completed', 100.0, 35, 35, DATE_SUB(NOW(), INTERVAL 60 DAY)),

-- Lisa (Marketing) enrolled in Digital Marketing
('enroll-004', 'user-012', 'course-004', 'in_progress', 65.0, 23, 30, DATE_SUB(NOW(), INTERVAL 45 DAY)),

-- Roberto (Coach) enrolled in Advanced Tactics - Completed
('enroll-005', 'user-007', 'course-002', 'completed', 100.0, 50, 50, DATE_SUB(NOW(), INTERVAL 90 DAY));

-- =============================================
-- Certificates
-- =============================================

-- Certificate for James (completed Sports Injury Prevention)
INSERT INTO certificates (id, enrollment_id, certificate_number, issued_date, verification_url, metadata) VALUES
('cert-001', 'enroll-003', 'CERT-2025-123456', DATE_SUB(NOW(), INTERVAL 30 DAY), 
 'https://soccercentral.edu/verify/CERT-2025-123456',
 '{"final_score": 92.5, "hours_completed": 45, "grade": "A", "competencies": ["Injury assessment", "Prevention protocols", "Emergency response"]}');

-- Certificate for Roberto (completed Advanced Tactics)
INSERT INTO certificates (id, enrollment_id, certificate_number, issued_date, verification_url, metadata) VALUES
('cert-002', 'enroll-005', 'CERT-2025-123457', DATE_SUB(NOW(), INTERVAL 60 DAY),
 'https://soccercentral.edu/verify/CERT-2025-123457',
 '{"final_score": 95.0, "hours_completed": 60, "grade": "A", "competencies": ["Tactical analysis", "Game planning", "Formation strategy"]}');

-- =============================================
-- Reviews
-- =============================================

INSERT INTO reviews (course_id, user_id, rating, comment, is_verified, created_at) VALUES
-- Alex's review of Youth Coaching course
('course-001', 'user-009', 4.5, 'Excellent foundation for anyone starting in youth coaching. The age-appropriate training methods module was particularly helpful.', TRUE, DATE_SUB(NOW(), INTERVAL 5 DAY)),

-- James's review of Sports Injury Prevention (completed course)
('course-005', 'user-011', 5.0, 'Outstanding course! The practical demonstrations and case studies were invaluable. I feel much more confident in injury assessment now.', TRUE, DATE_SUB(NOW(), INTERVAL 30 DAY)),

-- Roberto's review of Advanced Tactics (completed course)
('course-002', 'user-007', 4.8, 'Comprehensive tactical training. The video analysis sections really helped me understand different formations and strategies.', TRUE, DATE_SUB(NOW(), INTERVAL 60 DAY)),

-- Lisa's review of Digital Marketing
('course-004', 'user-012', 4.7, 'Great practical tips for sports marketing. The social media strategy module was exactly what I needed.', TRUE, DATE_SUB(NOW(), INTERVAL 10 DAY));

-- =============================================
-- Notifications
-- =============================================

INSERT INTO notifications (user_id, type, title, message, related_id, is_read, created_at) VALUES
-- Recent notifications for various users
('user-009', 'course_update', 'New Module Released', 'Module 4: Communication and Leadership is now available in your Youth Soccer Coaching course.', 'course-001', FALSE, DATE_SUB(NOW(), INTERVAL 2 DAY)),

('user-010', 'reminder', 'Continue Your Learning', 'You haven''t accessed your Sports Injury Prevention course in 5 days. Keep up the momentum!', 'course-005', FALSE, DATE_SUB(NOW(), INTERVAL 1 DAY)),

('user-011', 'certificate', 'Certificate Issued', 'Congratulations! Your certificate for Sports Injury Prevention and Management has been issued.', 'cert-001', TRUE, DATE_SUB(NOW(), INTERVAL 30 DAY)),

('user-012', 'course_update', 'Live Q&A Session', 'Join Dr. Johnson for a live Q&A about digital marketing strategies this Friday at 2 PM.', 'course-004', FALSE, DATE_SUB(NOW(), INTERVAL 3 DAY)),

('user-007', 'announcement', 'New Course Available', 'Check out our new course: Leadership in Sports Coaching. Early enrollment discount available!', NULL, FALSE, DATE_SUB(NOW(), INTERVAL 1 DAY));

-- =============================================
-- Summary
-- =============================================
-- This sample data includes:
-- - 8 organizations (5 universities + 3 academies)
-- - 12 users (1 admin, 5 instructors, 2 coaches, 4 students)
-- - 7 courses across different categories
-- - 4 modules with sample lessons for Course 001
-- - 5 enrollments with varied progress
-- - 2 certificates for completed courses
-- - 4 course reviews
-- - 5 notifications

-- Note: In production, password hashes should be properly generated using bcrypt
-- and sensitive data should be handled securely.
