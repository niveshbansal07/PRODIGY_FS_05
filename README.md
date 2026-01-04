# 🌐 SocialBuddy – Basic Social / Media Sharing Web Application

**SocialBuddy** is a **fully functional social media web application** built using **Flask, MySQL, HTML, and CSS**, designed to demonstrate **core social networking features** such as user authentication, media sharing, likes, and comments.

This project focuses on **backend fundamentals, database design, authentication, and server-side rendering**, making it ideal for **college projects, internships, and beginner-to-intermediate portfolios**.

---

## 📸 Project Preview

![Preview](https://github.com/niveshbansal07/PRODIGY_FS_05/blob/main/Login%20-%20SocialBuddy%20-%20Brave%201_4_2026%207_10_20%20AM.png)
![Preview](https://github.com/niveshbansal07/PRODIGY_FS_05/blob/main/Login%20-%20SocialBuddy%20-%20Brave%201_4_2026%207_09_29%20AM.png)

```
/static/screenshots/
```

---

## 🚀 Features

### ✅ Core Features

* User Signup & Login system
* Secure authentication using **JWT (JSON Web Tokens)**
* Password hashing for security
* User profiles with personal posts
* Create posts with **image/video uploads**
* Media stored securely in **local server storage**
* Public feed showing posts from **all users**
* Like & unlike posts
* Comment on posts
* Persistent data stored in **MySQL**
* Protected routes for authenticated users
* Clean, simple, and intuitive UI (HTML + CSS)

---

### ⭐ Optional / Extendable Features

* Follow / unfollow users
* Notification system (non real-time)
* Trending posts (based on likes)
* Profile enhancements
* Media validation & optimization

---

## 🛠 Tech Stack

### **Frontend**

* HTML5 (Server-side rendered)
* CSS3 (Clean & responsive layout)
* ❌ No JavaScript (pure Flask + HTML forms)

### **Backend**

* Python (Flask)
* JWT Authentication
* RESTful routes
* File handling & validation

### **Database**

* MySQL (Relational database)

---

## 📁 Project Structure

```
SocialBuddy/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── uploads/
│       ├── images/
│       └── videos/
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── feed.html
│   ├── profile.html
│
├── config.py
├── app.py
├── requirements.txt
└── venv/
```

---

## 🗄 Database Structure (MySQL)

```sql
-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts Table
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    caption TEXT,
    media_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Likes Table
CREATE TABLE likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    post_id INT NOT NULL
);

-- Comments Table
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📂 Media Storage (Local Storage)

* All uploaded images/videos are stored in:

  ```
  /static/uploads/
  ```
* Only the **relative file path** is saved in MySQL
* Media served using Flask’s static file handling
* Supported formats:

  * Images: `jpg`, `jpeg`, `png`
  * Videos: `mp4`

---

## ⚙ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/socialbuddy.git
cd socialbuddy
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Database

Update MySQL credentials in `config.py`:

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_DB = "socialbuddy"
```

---

### ▶ Run the Application

```bash
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## 🔐 Security Features

* Password hashing
* JWT-based authentication
* Protected routes
* File type & size validation
* One-like-per-user-per-post restriction

---

## 🧠 What I Learned

* Flask backend architecture
* JWT authentication & authorization
* MySQL relational database design
* File upload & static media handling
* Building social media features from scratch
* RESTful route design
* Server-side rendering with Flask
* Secure user authentication workflows
* Structuring real-world backend projects

---

## 🎯 Project Purpose

This project was built to:

* Practice **backend fundamentals**
* Understand **social media system design**
* Implement authentication & authorization
* Build a **real-world CRUD-based application**
* Strengthen Flask & MySQL skills
* Create a solid **portfolio-ready project**

---

## 📬 Contact

**Nivesh Bansal**
Aspiring Full Stack Developer

📧 Email: **[niveshbansal52@gmail.com](mailto:niveshbansal52@gmail.com)**
🌐 Portfolio: **[https://nivesh-bansal.vercel.app](https://nivesh-bansal.vercel.app)**
🔗 GitHub: **[https://github.com/niveshbansal07](https://github.com/niveshbansal07)**

---

### ⭐ If you like this project, give it a star on GitHub!

---
