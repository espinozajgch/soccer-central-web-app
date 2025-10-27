# Soccer Central LMS - Database Scripts

This directory contains the simplified database schema for the Soccer Central Learning Management System (LMS). The platform connects universities and sports academies in the United States to provide educational courses for soccer academy personnel.

## Overview

The database supports a comprehensive LMS platform for training:
- **Coaches** - Youth development, tactics, and methodology
- **Players** - Sports education and career development
- **Medical Staff** - Injury prevention and management
- **Physical Trainers** - Strength and conditioning
- **Marketing Teams** - Sports marketing and fan engagement
- **Management** - Organization and operations

## Database Design Philosophy

The schema follows a simplified approach as recommended:

1. **Unified User Model** - Single `users` table with role-based access (student, instructor, coach, admin)
2. **No Redundant Tables** - Instructors and coaches share the same entity with role and specialization fields
3. **Organization Support** - Universities and academies as institutional instructors
4. **Flexible Metadata** - JSON fields for course recognition, multilingual content, and extensibility
5. **Progress Tracking** - Centralized enrollment system with automatic progress calculation
6. **Digital Certification** - Built-in certificate generation and verification

## Files

### `00_init_database.sql`
Master initialization script that executes all setup scripts in order. Use this for a complete fresh installation.

**Usage:**
```bash
mysql -u username -p database_name < 00_init_database.sql
```

### `01_schema.sql`
Complete database schema including:
- **9 core tables**: users, organizations, courses, modules, lessons, enrollments, certificates, reviews, notifications
- **Foreign key constraints** for referential integrity
- **Indexes** for optimized queries
- **Triggers** for automatic certificate number generation
- **Views** for common analytics queries

**Tables:**

| Table | Purpose |
|-------|---------|
| `users` | Unified user management with roles: student, instructor, coach, admin |
| `organizations` | Universities and academies offering courses |
| `courses` | Educational courses with categorization and metadata |
| `modules` | Course content organization (chapters/sections) |
| `lessons` | Individual learning units (videos, text, quizzes, etc.) |
| `enrollments` | User course registrations with progress tracking |
| `certificates` | Digital certificates for completed courses |
| `reviews` | Course ratings and feedback from students |
| `notifications` | User notification system |

**Features:**
- UTF-8 encoding for international support
- JSON support for flexible multilingual content
- Automatic timestamps on all tables
- Soft deletes where appropriate

### `02_sample_data.sql`
Sample data for testing and demonstration including:

**Organizations (8 total):**
- University of Texas at San Antonio (UTSA)
- Texas A&M University
- Southern Methodist University (SMU)
- University of Houston
- St. Mary's University
- Soccer Central Academy
- FC Dallas Youth Academy
- Houston Dynamo Youth Academy

**Users (12 total):**
- 1 Platform Administrator
- 5 University Instructors (PhD/certified professionals)
- 2 Academy Coaches
- 4 Students (various roles: assistant coach, player, medical staff, marketing)

**Courses (7 total):**
- Fundamentals of Youth Soccer Coaching (Coaching)
- Advanced Tactical Analysis in Soccer (Coaching)
- Sports Organization Management (Management)
- Digital Marketing for Sports Organizations (Marketing)
- Sports Injury Prevention and Management (Medical)
- Performance Nutrition for Soccer Athletes (Nutrition)
- Strength and Conditioning for Soccer (Physical Training)

**Additional Data:**
- 4 modules with lessons for the Youth Coaching course
- 5 enrollments with varied completion status
- 2 certificates for completed courses
- 4 course reviews with ratings
- 5 notifications

## Installation

### Prerequisites
- MySQL 5.7+ or MariaDB 10.2+
- Database user with CREATE, INSERT, and ALTER privileges

### Step 1: Create Database
```sql
CREATE DATABASE soccer_central_lms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2: Run Initialization Script

**Option A: Complete Setup (recommended for first-time setup)**
```bash
mysql -u your_username -p soccer_central_lms < 00_init_database.sql
```

**Option B: Individual Scripts (for custom setup)**
```bash
# Schema only
mysql -u your_username -p soccer_central_lms < 01_schema.sql

# Add sample data (optional)
mysql -u your_username -p soccer_central_lms < 02_sample_data.sql
```

### Step 3: Update Application Configuration
Edit your `.env` file:
```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=soccer_central_lms
```

## Database Schema Diagram

```
┌──────────────┐
│ organizations│
└──────┬───────┘
       │
       │ (1:N)
       │
┌──────▼───────┐     ┌────────────┐
│    users     │────▶│   courses  │ (instructor_id)
└──────┬───────┘     └─────┬──────┘
       │                   │
       │                   │ (1:N)
       │                   │
       │             ┌─────▼──────┐
       │             │   modules  │
       │             └─────┬──────┘
       │                   │
       │                   │ (1:N)
       │                   │
       │             ┌─────▼──────┐
       │             │   lessons  │
       │             └────────────┘
       │
       │ (N:M via enrollments)
       │
       ▼
┌──────────────┐     ┌──────────────┐
│ enrollments  │────▶│ certificates │
└──────┬───────┘     └──────────────┘
       │
       │ (user interactions)
       │
       ├────▶ reviews
       └────▶ notifications
```

## Key Features

### 1. Role-Based Access Control
Users have one of four roles:
- **student**: Enrolls in courses, tracks progress, earns certificates
- **instructor**: Creates and manages courses, monitors student progress
- **coach**: Similar to instructor, specialized for coaching content
- **admin**: Full system access, manages users and organizations

### 2. Organization Integration
Universities and academies register as organizations and can:
- Offer courses with institutional recognition
- Assign instructors from their institution
- Provide branded certificates
- Track enrollment from their organization

### 3. Multilingual Support
Courses, modules, and lessons support multilingual content via JSON:
```json
{
  "en": {
    "title": "Introduction to Coaching",
    "content": "..."
  },
  "es": {
    "title": "Introducción al Entrenamiento",
    "content": "..."
  }
}
```

### 4. Flexible Course Metadata
Courses can include:
- Prerequisites
- University recognition
- External program affiliation
- Learning outcomes
- Certification preparation (e.g., USSF, UEFA, NASM)

### 5. Progress Tracking
Automatic tracking of:
- Enrollment status (enrolled, in_progress, completed, dropped)
- Progress percentage
- Lessons completed
- Last accessed lesson
- Completion date

### 6. Digital Certificates
- Unique certificate numbers
- Verification URLs
- Detailed metadata (scores, competencies, hours)
- Automated generation on course completion

## Common Queries

### Get all courses with enrollment stats
```sql
SELECT * FROM course_statistics 
WHERE is_published = TRUE 
ORDER BY average_rating DESC;
```

### Get user learning progress
```sql
SELECT * FROM user_learning_progress 
WHERE user_id = 'user-009';
```

### Find available courses by category
```sql
SELECT c.*, o.name as organization_name, u.full_name as instructor_name
FROM courses c
JOIN organizations o ON c.organization_id = o.id
LEFT JOIN users u ON c.instructor_id = u.id
WHERE c.category = 'coaching' AND c.is_published = TRUE
ORDER BY c.created_at DESC;
```

### Check enrollment status
```sql
SELECT 
    e.*, 
    c.title as course_title, 
    u.full_name as student_name,
    cert.certificate_number
FROM enrollments e
JOIN courses c ON e.course_id = c.id
JOIN users u ON e.user_id = u.id
LEFT JOIN certificates cert ON e.id = cert.enrollment_id
WHERE e.user_id = 'user-009';
```

## Maintenance

### Clear expired data
```sql
-- Archive completed enrollments older than 2 years
-- (implement based on your retention policy)
```

### Update statistics
The `course_statistics` and `user_learning_progress` views automatically reflect current data.

### Backup
Regular backups recommended:
```bash
mysqldump -u username -p soccer_central_lms > backup_$(date +%Y%m%d).sql
```

## Security Notes

1. **Password Hashing**: Sample data uses placeholder hashes. In production, use proper bcrypt hashing with adequate rounds (12+).

2. **Sensitive Data**: The `profile_data` and `metadata` JSON fields may contain sensitive information. Ensure proper access controls.

3. **SQL Injection**: Always use parameterized queries in your application code.

4. **Access Control**: Implement row-level security based on user roles and organization membership.

## Integration with Universities

The system is designed to integrate with courses from:
- University of Texas at San Antonio (UTSA) - Sports management and kinesiology
- Texas A&M University - Sport management and coaching
- Southern Methodist University (SMU) - Sport management and business
- University of Houston - Sport administration and athletic training
- St. Mary's University - Sport management and coaching

Each university can:
1. Register as an organization
2. Add instructors with university email addresses
3. Create courses with university recognition
4. Issue certificates co-branded with their institution
5. Track student enrollment and completion

## Future Enhancements

Potential additions for future versions:
- Discussion forums (course_discussions table)
- Live sessions/webinars (live_sessions table)
- Assignments and submissions (assignments, submissions tables)
- Gamification (badges, achievements tables)
- Course prerequisites enforcement
- Payment/transaction tracking for paid courses
- Advanced analytics and reporting

## Support

For questions or issues with the database schema:
1. Check the SQL script comments for detailed documentation
2. Review the table and column descriptions
3. Consult the application documentation
4. Contact the development team

## Version History

- **v1.0** (2025) - Initial simplified schema
  - 9 core tables
  - Support for US universities
  - Multilingual content
  - Digital certification
  - Progress tracking

---

**Note**: This is a simplified schema designed for a focused LMS platform. For enterprise deployments with additional requirements, consult with the development team for custom enhancements.
