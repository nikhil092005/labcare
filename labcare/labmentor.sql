DROP DATABASE IF EXISTS labmentor;
CREATE DATABASE labmentor;
use labmentor;
CREATE TABLE users (
    uid VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(20),
    course VARCHAR(50) NOT NULL,
    issues_registered INT DEFAULT 0,
    issues_solved INT DEFAULT 0,
    credits INT DEFAULT 0,
    ranke INT DEFAULT 1,
    stars INT DEFAULT 0
);

CREATE TABLE issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    building_no VARCHAR(10) NOT NULL,
    lab_no VARCHAR(10) NOT NULL,
    pc_no VARCHAR(10) NOT NULL,
    uid VARCHAR(10),
    issue_type VARCHAR(50) NOT NULL,
    issue_details TEXT NOT NULL,
    issue_image VARCHAR(255),
    status ENUM('open', 'solved') DEFAULT 'open',
    registered_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES users(uid)
);

CREATE TABLE solutions (
    solution_id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT,
    uid VARCHAR(10),
    solution_text TEXT NOT NULL,
    solution_image VARCHAR(255),
    post_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(issue_id),
    FOREIGN KEY (uid) REFERENCES users(uid)
);
CREATE TABLE credit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(10),
    action ENUM('report_issue', 'solve_issue', 'provide_solution'),
    points INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES users(uid)
);
SELECT * FROM users;