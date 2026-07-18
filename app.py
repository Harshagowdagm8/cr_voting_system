# app.py - Main Flask Application
import os
import hashlib
import secrets
import socket
from functools import wraps
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flaskext.mysql import MySQL
import pymysql

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Configuration
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'voting_system'
app.config['MYSQL_DATABASE_PORT'] = 3306

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mysql = MySQL()
mysql.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    conn = mysql.connect()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            usn VARCHAR(20) UNIQUE NOT NULL,
            slogan TEXT,
            photo VARCHAR(255),
            votes INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(100) NOT NULL,
            student_usn VARCHAR(20) UNIQUE NOT NULL,
            candidate_id INT,
            voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS election_status (
            id INT AUTO_INCREMENT PRIMARY KEY,
            is_active BOOLEAN DEFAULT FALSE,
            share_code VARCHAR(50) UNIQUE,
            election_name VARCHAR(200) DEFAULT 'Class Representative Election'
        )
    ''')
    
    cursor.execute("SELECT * FROM election_status")
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO election_status (is_active, share_code, election_name) VALUES (FALSE, %s, %s)", 
                      (secrets.token_urlsafe(16), 'Class Representative Election'))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully!")

with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization error: {e}")

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/vote')
def vote():
    return render_template('vote.html')

# ==================== ADMIN AUTHENTICATION ====================

@app.route('/api/admin/register', methods=['POST'])
def admin_register():
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([full_name, email, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = mysql.connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO admins (full_name, email, password) VALUES (%s, %s, %s)",
                      (full_name, email, hashed_password))
        conn.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except pymysql.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password required'}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM admins WHERE email = %s AND password = %s", (email, hashed_password))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if admin:
        session['admin_id'] = admin['id']
        session['admin_name'] = admin['full_name']
        return jsonify({'message': 'Login successful', 'admin': {'id': admin['id'], 'name': admin['full_name']}}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/admin/check-auth', methods=['GET'])
def check_auth():
    if 'admin_id' in session:
        return jsonify({'authenticated': True, 'admin_name': session.get('admin_name')}), 200
    return jsonify({'authenticated': False}), 200

# ==================== CANDIDATE MANAGEMENT ====================

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM candidates ORDER BY id")
    candidates = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(candidates), 200

@app.route('/api/candidates', methods=['POST'])
@login_required
def add_candidate():
    name = request.form.get('name')
    usn = request.form.get('usn')
    slogan = request.form.get('slogan')
    photo = request.files.get('photo')
    
    if not all([name, usn, slogan]):
        return jsonify({'error': 'All fields are required'}), 400
    
    photo_filename = None
    if photo and allowed_file(photo.filename):
        photo_filename = secure_filename(f"{usn}_{photo.filename}")
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
    
    conn = mysql.connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO candidates (name, usn, slogan, photo) VALUES (%s, %s, %s, %s)",
                      (name, usn, slogan, photo_filename))
        conn.commit()
        return jsonify({'message': 'Candidate added successfully'}), 201
    except pymysql.IntegrityError:
        return jsonify({'error': 'USN already exists'}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/candidates/<int:candidate_id>', methods=['PUT'])
@login_required
def update_candidate(candidate_id):
    name = request.form.get('name')
    usn = request.form.get('usn')
    slogan = request.form.get('slogan')
    photo = request.files.get('photo')
    
    conn = mysql.connect()
    cursor = conn.cursor()
    
    try:
        if photo and allowed_file(photo.filename):
            photo_filename = secure_filename(f"{usn}_{photo.filename}")
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            cursor.execute("UPDATE candidates SET name=%s, usn=%s, slogan=%s, photo=%s WHERE id=%s",
                          (name, usn, slogan, photo_filename, candidate_id))
        else:
            cursor.execute("UPDATE candidates SET name=%s, usn=%s, slogan=%s WHERE id=%s",
                          (name, usn, slogan, candidate_id))
        conn.commit()
        return jsonify({'message': 'Candidate updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/candidates/<int:candidate_id>', methods=['DELETE'])
@login_required
def delete_candidate(candidate_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id=%s", (candidate_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Candidate deleted successfully'}), 200

# ==================== ELECTION MANAGEMENT ====================

@app.route('/api/election/status', methods=['GET'])
def get_election_status():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT is_active, share_code, election_name FROM election_status WHERE id=1")
    status = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(status or {'is_active': False, 'election_name': 'Class Representative Election'}), 200

@app.route('/api/election/start', methods=['POST'])
@login_required
def start_election():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE election_status SET is_active = TRUE WHERE id=1")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Election started successfully'}), 200

@app.route('/api/election/stop', methods=['POST'])
@login_required
def stop_election():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE election_status SET is_active = FALSE WHERE id=1")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Election stopped successfully'}), 200

@app.route('/api/election/share-link', methods=['GET'])
def get_share_link():
    """Generate new shareable voting link"""
    try:
        # ===== MANUALLY SET YOUR IP HERE =====
        local_ip = "192.168.1.100"  # <-- CHANGE THIS TO YOUR IP
        # ====================================
        
        port = "8080"
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        share_code = secrets.token_urlsafe(16)
        cursor.execute("UPDATE election_status SET share_code = %s WHERE id=1", (share_code,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        voting_link = f"http://{local_ip}:{port}/vote?code={share_code}"
        print(f"✅ New voting link generated: {voting_link}")
        
        return jsonify({'share_link': voting_link}), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/election/name', methods=['PUT'])
@login_required
def update_election_name():
    data = request.json
    election_name = data.get('election_name')
    
    if not election_name:
        return jsonify({'error': 'Election name is required'}), 400
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE election_status SET election_name = %s WHERE id=1", (election_name,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Election name updated successfully'}), 200

# ==================== VOTING ====================

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    data = request.json
    student_name = data.get('student_name')
    student_usn = data.get('student_usn')
    candidate_id = data.get('candidate_id')
    
    if not all([student_name, student_usn, candidate_id]):
        return jsonify({'error': 'All fields are required'}), 400
    
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT is_active FROM election_status WHERE id=1")
    status = cursor.fetchone()
    
    if not status or not status['is_active']:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Election is not active'}), 403
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO votes (student_name, student_usn, candidate_id) VALUES (%s, %s, %s)",
                      (student_name, student_usn, candidate_id))
        cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE id = %s", (candidate_id,))
        conn.commit()
        return jsonify({'message': 'Vote cast successfully'}), 201
    except pymysql.IntegrityError:
        return jsonify({'error': 'This USN has already voted'}), 400
    finally:
        cursor.close()
        conn.close()

# ==================== RESULTS ====================

@app.route('/api/results', methods=['GET'])
def get_results():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM candidates ORDER BY votes DESC")
    candidates = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as total_votes FROM votes")
    total = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({'candidates': candidates, 'total_votes': total['total_votes'] if total else 0}), 200

@app.route('/api/voters', methods=['GET'])
def get_voters():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT v.id, v.student_name, v.student_usn, v.voted_at, c.name as candidate_name
        FROM votes v
        JOIN candidates c ON v.candidate_id = c.id
        ORDER BY v.voted_at DESC
    """)
    voters = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'voters': voters, 'total': len(voters)}), 200

# ==================== RUN APP ====================

if __name__ == '__main__':
    # Get IP for display
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*50)
    print("🏆 CLASS REPRESENTATIVE VOTING SYSTEM")
    print("="*50)
    print("✅ Server starting...")
    print("📍 Access at: http://localhost:8080")
    print("📱 Mobile link: http://" + local_ip + ":8080")
    print("📋 Admin login: http://localhost:8080")
    print("🗳️  Student voting: http://localhost:8080/vote")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080)