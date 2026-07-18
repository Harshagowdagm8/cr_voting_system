-- database.sql - MySQL Database Schema for phpMyAdmin
-- Create database for Class Representative Voting Management System

CREATE DATABASE IF NOT EXISTS voting_system;
USE voting_system;

-- Table: admins (stores admin user accounts)
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: candidates (stores election candidates)
CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    usn VARCHAR(20) UNIQUE NOT NULL,
    slogan TEXT,
    photo VARCHAR(255),
    votes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: votes (tracks which students have voted)
CREATE TABLE IF NOT EXISTS votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_usn VARCHAR(20) UNIQUE NOT NULL,
    candidate_id INT,
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- Table: election_status (controls election state)
CREATE TABLE IF NOT EXISTS election_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    is_active BOOLEAN DEFAULT FALSE,
    share_code VARCHAR(50) UNIQUE
);

-- Insert initial election status
INSERT INTO election_status (is_active, share_code) 
SELECT FALSE, SUBSTRING(MD5(RAND()), 1, 32) 
WHERE NOT EXISTS (SELECT 1 FROM election_status);

-- Sample data (optional - uncomment to test)
-- INSERT INTO admins (full_name, email, password) 
-- VALUES ('Admin User', 'admin@example.com', SHA2('admin123', 256));

-- SELECT * FROM admins;
-- SELECT * FROM candidates;
-- SELECT * FROM votes;
-- SELECT * FROM election_status;