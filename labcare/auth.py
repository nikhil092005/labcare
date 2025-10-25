from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import generate_hashed_password, verify_password

auth_bp = Blueprint('auth', __name__)

# We'll assign this later from app after initialization
mysql = None

def init_app(mysql_obj):
    global mysql
    mysql = mysql_obj

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    global mysql
    if request.method == 'POST':
        uid = request.form['uid']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_hashed_password(password)
        mobile_number = request.form['mobile_number']
        course = request.form['course']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT uid FROM users WHERE uid = %s OR email = %s", (uid, email))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('UID or Email already registered. Please use a different UID/Email or login.', 'error')
            cursor.close()
            return redirect(url_for('auth.register'))

        cursor.execute("INSERT INTO users (uid, name, email, password, mobile_number, course) VALUES (%s,%s,%s,%s,%s,%s)",
                       (uid, name, email, hashed_password, mobile_number, course))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('registration.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    global mysql
    if request.method == 'POST':
        email_uid = request.form['email_uid']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT uid, password, name FROM users WHERE email=%s OR uid=%s", (email_uid, email_uid))
        user = cursor.fetchone()
        cursor.close()

        if user and verify_password(user[1], password):
            session['uid'] = user[0]
            session['name'] = user[2]
            flash(f'Welcome back, {user[2]}!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid UID/Email or Password.', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/dashboard')
def dashboard():
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    uid = session['uid']
    cursor = mysql.connection.cursor()
    
    # Fetch user data including credits
    cursor.execute("SELECT name, ranke, stars, issues_registered, issues_solved, credits FROM users WHERE uid=%s", (uid,))
    user_data = cursor.fetchone()
    
    # Fetch open issues
    cursor.execute("""
        SELECT issue_id, issue_type, issue_details, registered_time, uid 
        FROM issues 
        WHERE status='open' 
        ORDER BY registered_time DESC 
        LIMIT 20
    """)
    issues = cursor.fetchall()
    cursor.close()
    
    # Format issues for template
    issues_list = []
    for issue in issues:
        issues_list.append({
            'issue_id': issue[0],
            'issue_type': issue[1],
            'issue_details': issue[2],
            'registered_time': issue[3].strftime('%Y-%m-%d %H:%M') if issue[3] else 'N/A',
            'reported_by': issue[4]
        })
    
    return render_template('dashboard.html',
                         name=user_data[0],
                         rank=user_data[1],
                         stars=user_data[2],
                         issues_registered=user_data[3],
                         issues_solved=user_data[4],
                         credits=user_data[5],
                         issues=issues_list)

@auth_bp.route('/user-profile')
def user_profile():
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    uid = session['uid']
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT uid, name, email, mobile_number, course, ranke, stars, 
               credits, issues_registered, issues_solved 
        FROM users WHERE uid=%s
    """, (uid,))
    user_data = cursor.fetchone()
    cursor.close()
    
    user = {
        'uid': user_data[0],
        'name': user_data[1],
        'email': user_data[2],
        'mobile_number': user_data[3],
        'course': user_data[4],
        'rank': user_data[5],
        'stars': user_data[6],
        'credits': user_data[7],
        'issues_registered': user_data[8],
        'issues_solved': user_data[9]
    }
    
    return render_template('user_profile.html', user=user)

@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    uid = session['uid']
    name = request.form.get('name')
    email = request.form.get('email')
    mobile_number = request.form.get('mobile_number')
    course = request.form.get('course')
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE users 
        SET name=%s, email=%s, mobile_number=%s, course=%s 
        WHERE uid=%s
    """, (name, email, mobile_number, course, uid))
    mysql.connection.commit()
    cursor.close()
    
    session['name'] = name
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.user_profile'))

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    uid = session['uid']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT password FROM users WHERE uid=%s", (uid,))
    user = cursor.fetchone()
    
    if not user or not verify_password(user[0], current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.user_profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('auth.user_profile'))
    
    hashed_password = generate_hashed_password(new_password)
    cursor.execute("UPDATE users SET password=%s WHERE uid=%s", (hashed_password, uid))
    mysql.connection.commit()
    cursor.close()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.user_profile'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
