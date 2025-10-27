-- =============================================
-- Soccer Central LMS - Database Initialization Script
-- =============================================
-- This script initializes the complete database structure
-- and optionally loads sample data
-- =============================================
-- Usage:
--   For fresh installation with sample data:
--     mysql -u username -p database_name < 00_init_database.sql
--   
--   Or execute scripts individually:
--     mysql -u username -p database_name < 01_schema.sql
--     mysql -u username -p database_name < 02_sample_data.sql
-- =============================================

-- Set character set and collation for the session
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Display initialization message
SELECT '========================================' AS '';
SELECT 'Soccer Central LMS Database Setup' AS '';
SELECT 'Starting initialization...' AS '';
SELECT '========================================' AS '';

-- Source the schema file
SELECT 'Step 1: Creating database schema...' AS '';
SOURCE 01_schema.sql;
SELECT 'Schema creation completed!' AS '';

-- Optionally load sample data
SELECT '========================================' AS '';
SELECT 'Step 2: Loading sample data...' AS '';
SELECT 'This includes universities, users, courses, and enrollments' AS '';
SOURCE 02_sample_data.sql;
SELECT 'Sample data loaded successfully!' AS '';

-- Display completion message
SELECT '========================================' AS '';
SELECT 'Database initialization complete!' AS '';
SELECT '========================================' AS '';

-- Display summary statistics
SELECT 'Database Summary:' AS '';
SELECT COUNT(*) AS 'Total Users' FROM users;
SELECT COUNT(*) AS 'Total Organizations' FROM organizations;
SELECT COUNT(*) AS 'Total Courses' FROM courses;
SELECT COUNT(*) AS 'Total Enrollments' FROM enrollments;
SELECT COUNT(*) AS 'Total Certificates' FROM certificates;

SELECT '========================================' AS '';
SELECT 'Setup Instructions:' AS '';
SELECT '1. Update .env file with database credentials' AS '';
SELECT '2. Run the Flask application: python app.py' AS '';
SELECT '3. Default admin login: admin@soccercentral.com' AS '';
SELECT '   (password: password123)' AS '';
SELECT '========================================' AS '';
