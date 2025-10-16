create database STEI

use STEI;

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO categories (name) VALUES
('Free Webinars'),
('iACE Series'),
('Self-Growth'),
('The Strength of She'),
('Data Science');

CREATE TABLE workshops (
    workshop_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    duration_days INT NOT NULL,
    minutes_per_session INT DEFAULT 60,
    sessions_per_day INT DEFAULT 1,
    capacity INT DEFAULT 0,
    fee DECIMAL(10,2) DEFAULT 0,
    instructor VARCHAR(150),
    status ENUM('Active',  'Upcoming',  'Completed', 'Cancelled') DEFAULT 'Upcoming',
    workshop_image VARCHAR(255), -- store image path or URL
    start_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key linking workshop to category
    CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categories(category_id) 
        ON DELETE CASCADE
);


CREATE TABLE batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workshop_id INT NOT NULL,              -- linked to workshops table
    category_id INT,                       -- linked to batch_categories table
    workshop_name VARCHAR(200) NOT NULL,
    batch_name VARCHAR(100) NOT NULL,
    instructor VARCHAR(100),
    start_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    location VARCHAR(255),
    status ENUM('Upcoming', 'Ongoing', 'Completed', 'Cancelled') DEFAULT 'Upcoming',
    zoom_link VARCHAR(255),
    zoom_meeting_id VARCHAR(50),
    zoom_password VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_batches_workshop FOREIGN KEY (workshop_id) REFERENCES workshops(workshop_id) ON DELETE CASCADE
);


desc batches;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    password VARCHAR(255) NOT NULL,       -- password field added
    email_consent BOOLEAN DEFAULT FALSE,  -- TRUE if student agrees to receive emails
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE student_enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    workshop_id INT NOT NULL,
    batch_id INT NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Upcoming','Active', 'Completed', 'Cancelled') DEFAULT 'Upcoming',

    CONSTRAINT fk_enrollment_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_workshop FOREIGN KEY (workshop_id) REFERENCES workshops(workshop_id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_batch FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
);


CREATE TABLE quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quote TEXT NOT NULL,
    author VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    color VARCHAR(50),
    featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, 
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE blacklisted_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token TEXT NOT NULL,
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE students
ADD COLUMN profession ENUM('student', 'employee', 'other') DEFAULT 'student' AFTER email_consent,
ADD COLUMN designation VARCHAR(100) AFTER profession,
ADD COLUMN gender ENUM('male', 'female', 'other') AFTER designation;
