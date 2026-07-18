# cr_voting_system
A secure web-based voting system for class representative elections. Built with Flask, MySQL, and responsive frontend. Features USN authentication, real-time vote counting, duplicate vote prevention, CSV export, and PWA mobile support. Shareable links allow voting from anywhere.


# 🗳️ Class Representative Voting Management System

A secure, transparent, and efficient web-based voting platform for conducting class representative elections in educational institutions.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0.3+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-5.7+-orange.svg)
![PWA](https://img.shields.io/badge/PWA-Supported-purple.svg)

---

## 📱 Live Demo

> **Admin Login:** `http://localhost:8080/admin`  
> **Student Vote:** `http://localhost:8080/vote`

---

## ✨ Features

### 👑 Admin Panel
- Secure registration and login with SHA-256 password hashing
- Add, edit, and delete candidates with photos and slogans
- Start/stop election at any time
- Generate shareable voting links
- Real-time result monitoring
- Export voter list as CSV for audit

### 🗳️ Student Voting
- USN-based authentication (one vote per student)
- Browse candidates with photos and slogans
- Cast a single vote with duplicate prevention
- View live election results

### 📱 Mobile Support
- Fully responsive design
- PWA (Progressive Web App) for installable mobile app
- Share voting links via WhatsApp
- Works on all devices (phone, tablet, desktop)

### 🔒 Security
- SHA-256 password hashing
- Session management
- Database-level uniqueness constraints
- Input validation to prevent SQL injection

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, Flask |
| **Database** | MySQL |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Icons** | Font Awesome |
| **Security** | SHA-256, Session Management |
| **PWA** | Manifest.json, Service Worker |

---

## 📁 Folder Structure
cr_voting_system/
│
├── app.py
├── database.sql
├── requirements.txt
├── create_icons.py
├── README.md
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── admin.html
│   └── vote.html
│
└── static/
    ├── uploads/
    │   └── (candidate photos stored here)
    │
    ├── icons/
    │   ├── icon-72.png
    │   ├── icon-96.png
    │   ├── icon-128.png
    │   ├── icon-144.png
    │   ├── icon-152.png
    │   ├── icon-192.png
    │   ├── icon-384.png
    │   └── icon-512.png
    │
    ├── manifest.json
    └── sw.js



---

## 🗄️ Database Schema

| Table | Fields |
|-------|--------|
| **admins** | id, full_name, email, password, created_at |
| **candidates** | id, name, usn, slogan, photo, votes, created_at |
| **votes** | id, student_name, student_usn, candidate_id, voted_at |
| **election_status** | id, is_active, share_code, election_name |

---

## Admin Flow
Register → Login → Add Candidates → Start Election → Share Link → Monitor Results → Stop Election → Export CSV

## Student Flow
Receive Link → Enter Name & USN → View Candidates → Select Candidate → Confirm Vote → View Results

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL (XAMPP/WAMP/MAMP)
- Git (optional)


