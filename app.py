from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
# from flask_mysqldb import MySQL
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MySQL
# mysql = MySQL(app)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'socialbuddy'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_jwt_token(user_id, username):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    # Convert bytes to string if needed (PyJWT 2.0+ returns string by default)
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))
        payload = verify_jwt_token(token)
        if not payload:
            session.pop('token', None)
            session.pop('user_id', None)
            session.pop('username', None)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# def init_db():
#     """Initialize database tables"""
#     conn = get_db_connection()
#     cur = conn.cursor()
    
#     # Create users table
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INT PRIMARY KEY AUTO_INCREMENT,
#             username VARCHAR(100) UNIQUE NOT NULL,
#             email VARCHAR(150) UNIQUE NOT NULL,
#             password VARCHAR(255) NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
    
#     # Create posts table
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS posts (
#             id INT PRIMARY KEY AUTO_INCREMENT,
#             user_id INT NOT NULL,
#             caption TEXT,
#             media_path TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
    
#     # Create likes table
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS likes (
#             id INT PRIMARY KEY AUTO_INCREMENT,
#             user_id INT NOT NULL,
#             post_id INT NOT NULL,
#             UNIQUE KEY unique_like (user_id, post_id)
#         )
#     """)
    
#     # Create comments table
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS comments (
#             id INT PRIMARY KEY AUTO_INCREMENT,
#             user_id INT NOT NULL,
#             post_id INT NOT NULL,
#             comment TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
    
#     mysql.connection.commit()
#     cur.close()

@app.route('/')
def index():
    if session.get('token'):
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if username or email already exists
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            flash('Username or email already exists', 'error')
            cur.close()
            return render_template('signup.html')
        
        # Hash password and insert user
        hashed_password = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        user_id = cur.lastrowid
        cur.close()
        
        # Create JWT token and set session
        token = generate_jwt_token(user_id, username)
        session['token'] = token
        session['user_id'] = user_id
        session['username'] = username
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('feed'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user['password'], password):
            token = generate_jwt_token(user['id'], user['username'])
            session['token'] = token
            session['user_id'] = user['id'],
            session['username'] =user['username']
            return redirect(url_for('feed'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/feed')
# @login_required
def feed():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all posts with user info, ordered by latest first
    cur.execute("""
        SELECT p.id, p.user_id, p.caption, p.media_path, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    posts = cur.fetchall()
    
    # Get like counts for each post
    post_likes = {}
    post_user_liked = {}
    user_id = session.get('user_id')
    
    for post in posts:
        post_id = post['id']
        # Count likes
        cur.execute("SELECT COUNT(*) AS cnt FROM likes WHERE post_id = %s", (post_id,))
        like_count = cur.fetchone()['cnt']
        post_likes[post_id] = like_count
        
        # Check if current user liked this post
        cur.execute("SELECT id FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
        post_user_liked[post_id] = cur.fetchone() is not None
    
    # Get comment counts for each post
    post_comments = {}
    for post in posts:
        post_id = post['id']
        cur.execute("SELECT COUNT(*) AS cnt FROM comments WHERE post_id = %s", (post_id,))
        comment_count = cur.fetchone()['cnt']
        post_comments[post_id] = comment_count
    
    cur.close()
    
    return render_template('feed.html', posts=posts, post_likes=post_likes, 
                         post_user_liked=post_user_liked, post_comments=post_comments)

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    username = session.get('username')
    
    conn = get_db_connection()
    cur = conn.cursor() 

    # Get all posts by this user
    cur.execute("""
        SELECT id, caption, media_path, created_at
        FROM posts
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    posts = cur.fetchall()
    
    cur.close()
    
    return render_template('profile.html', username=username, posts=posts)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        caption = request.form.get('caption')
        file = request.files.get('media')
        
        if not caption and not file:
            flash('Please provide either a caption or media file', 'error')
            return render_template('create_post.html')
        
        media_path = None
        if file and file.filename and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            media_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(media_path)
            media_path = f"uploads/{unique_filename}"
        
        user_id = session.get('user_id')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO posts (user_id, caption, media_path) VALUES (%s, %s, %s)",
            (user_id, caption, media_path)
        )
        conn.commit()
        cur.close()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('feed'))
    
    return render_template('create_post.html')

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if already liked
    cur.execute("SELECT id FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
    existing_like = cur.fetchone()
    
    if existing_like:
        # Unlike
        cur.execute("DELETE FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
        conn.commit()
    else:
        # Like
        cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))
        conn.commit()
    
    cur.close()
    return redirect(url_for('feed'))

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    comment_text = request.form.get('comment')
    if not comment_text:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('feed'))
    
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (user_id, post_id, comment) VALUES (%s, %s, %s)",
        (user_id, post_id, comment_text)
    )
    conn.commit()
    cur.close()
    
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get post details
    cur.execute("""
        SELECT p.id, p.user_id, p.caption, p.media_path, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
    """, (post_id,))
    post = cur.fetchone()
    
    if not post:
        flash('Post not found', 'error')
        return redirect(url_for('feed'))
    
    # Get like count
    cur.execute("SELECT COUNT(*) AS cnt FROM likes WHERE post_id = %s", (post_id,))
    like_count = cur.fetchone()['cnt']
    
    # Check if user liked
    user_id = session.get('user_id')
    cur.execute("SELECT id FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
    user_liked = cur.fetchone() is not None
    
    # Get comments
    cur.execute("""
        SELECT c.comment, c.created_at, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = %s
        ORDER BY c.created_at ASC
    """, (post_id,))
    comments = cur.fetchall()
    
    cur.close()
    
    return render_template('post_detail.html', post=post, like_count=like_count,
                       user_liked=user_liked, comments=comments)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # with app.app_context():
        # init_db()
    app.run(debug=True)

