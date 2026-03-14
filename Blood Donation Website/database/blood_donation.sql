-- ============================================================
--  BloodLink - Blood Donation Camp Management System
--  MySQL Database Schema
--  Import this file via phpMyAdmin in XAMPP
-- ============================================================

-- Step 1: Create and select the database
CREATE DATABASE IF NOT EXISTS blood_donation_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE blood_donation_system;

-- ============================================================
-- TABLE: donors
-- Stores all registered blood donors
-- ============================================================
CREATE TABLE IF NOT EXISTS donors (
    donor_id     INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    age          INT           NOT NULL,
    gender       VARCHAR(10)   NOT NULL,
    blood_group  VARCHAR(5)    NOT NULL,
    phone        VARCHAR(15)   NOT NULL,
    email        VARCHAR(100)  NOT NULL UNIQUE,
    city         VARCHAR(100)  NOT NULL,
    password     VARCHAR(255)  NOT NULL,   -- stored as hashed value
    created_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: camps
-- Stores all blood donation camps
-- ============================================================
CREATE TABLE IF NOT EXISTS camps (
    camp_id      INT AUTO_INCREMENT PRIMARY KEY,
    camp_name    VARCHAR(200)  NOT NULL,
    location     VARCHAR(200)  NOT NULL,
    date         DATE          NOT NULL,
    organizer    VARCHAR(150)  NOT NULL,
    description  TEXT,
    camp_type    VARCHAR(50)   DEFAULT 'general',  -- emergency, hospital, city, general
    created_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: registrations
-- Links donors to camps they have registered for
-- ============================================================
CREATE TABLE IF NOT EXISTS registrations (
    registration_id   INT AUTO_INCREMENT PRIMARY KEY,
    donor_id          INT  NOT NULL,
    camp_id           INT  NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status            VARCHAR(20) DEFAULT 'confirmed',
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE,
    FOREIGN KEY (camp_id)  REFERENCES camps(camp_id)   ON DELETE CASCADE,
    UNIQUE KEY unique_registration (donor_id, camp_id)  -- prevent duplicate registrations
);

-- ============================================================
-- TABLE: admins
-- Stores admin login credentials
-- ============================================================
CREATE TABLE IF NOT EXISTS admins (
    admin_id   INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)   NOT NULL UNIQUE,
    password   VARCHAR(255)  NOT NULL,   -- hashed
    created_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SAMPLE DATA - Camps
-- ============================================================
INSERT INTO camps (camp_name, location, date, organizer, description, camp_type) VALUES
('City General Hospital Annual Blood Drive',   'City General Hospital, Pune',         '2025-04-15', 'Dr. Mehta Health Foundation', 'Annual blood drive organized by City General Hospital. Free health check-up for all donors.', 'hospital'),
('Urgent O-Negative Blood Collection Drive',   'Community Hall, Nashik',              '2025-04-20', 'Red Cross Society',           'Emergency collection drive for O-Negative blood group. Immediate need for accident victims.', 'emergency'),
('Pune City Blood Donation Festival',          'Bal Gandharva Rang Mandir, Pune',     '2025-04-25', 'Pune Municipal Corporation',  'City-wide blood donation festival. Refreshments and certificates provided to all donors.', 'city'),
('Sahyadri Hospital Quarterly Donation Camp',  'Sahyadri Hospital, Deccan, Pune',     '2025-05-02', 'Sahyadri Medical Trust',      'Quarterly blood collection camp. All blood groups accepted.', 'hospital'),
('Emergency Platelet Donation Drive',          'Ruby Hall Clinic, Pune',              '2025-05-05', 'Ruby Hall Foundation',        'Urgent need for platelets. Donors with all blood groups welcome.', 'emergency'),
('Nashik Youth Blood Donation Camp',           'Central Park, Nashik',                '2025-05-10', 'Nashik Youth Association',    'Youth-focused blood donation camp. Prizes for first-time donors.', 'city');

-- ============================================================
-- SAMPLE DATA - Default Admin
-- Username: admin  |  Password: admin123  (hashed below)
-- The app.py uses werkzeug to hash; this hash corresponds to 'admin123'
-- ============================================================
INSERT INTO admins (username, password) VALUES
('admin', 'pbkdf2:sha256:260000$placeholder$hash_will_be_set_by_app');
-- NOTE: Run this in your terminal ONCE after starting the app to set correct hash:
--   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))"
-- Then UPDATE admins SET password='<output>' WHERE username='admin';

-- ============================================================
-- SAMPLE DATA - Donors (passwords are hashed 'password123')
-- ============================================================
INSERT INTO donors (name, age, gender, blood_group, phone, email, city, password) VALUES
('Rahul Sharma',  28, 'Male',   'B+',  '9876543210', 'rahul@email.com',  'Pune',   'pbkdf2:sha256:260000$sample$hash1'),
('Priya Patel',   25, 'Female', 'O+',  '9988776655', 'priya@email.com',  'Nashik', 'pbkdf2:sha256:260000$sample$hash2'),
('Amit Singh',    32, 'Male',   'A+',  '8877665544', 'amit@email.com',   'Mumbai', 'pbkdf2:sha256:260000$sample$hash3');

-- ============================================================
-- SAMPLE DATA - Registrations
-- ============================================================
INSERT INTO registrations (donor_id, camp_id, status) VALUES
(1, 4, 'confirmed'),
(1, 6, 'pending'),
(2, 3, 'confirmed'),
(3, 1, 'confirmed');

