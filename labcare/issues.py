from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from utils import calculate_rank_and_stars
import math

issues_bp = Blueprint('issues', __name__)

# We'll assign this later from app after initialization
mysql = None

def init_app(mysql_obj):
    global mysql
    mysql = mysql_obj

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/issues'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_user_credits(uid, credits_to_add):
    """Update user credits and recalculate rank and stars"""
    cursor = mysql.connection.cursor()
    
    # Get current credits
    cursor.execute("SELECT credits FROM users WHERE uid=%s", (uid,))
    result = cursor.fetchone()
    current_credits = result[0] if result else 0
    
    # Add new credits
    new_total_credits = current_credits + credits_to_add
    
    # Calculate new rank, stars, and remaining credits
    new_rank, new_stars, remaining_credits = calculate_rank_and_stars(new_total_credits)
    
    # Update database
    cursor.execute("""
        UPDATE users 
        SET credits = %s, ranke = %s, stars = %s 
        WHERE uid = %s
    """, (remaining_credits, new_rank, new_stars, uid))
    
    mysql.connection.commit()
    cursor.close()

@issues_bp.route('/report-issue', methods=['GET', 'POST'])
def report_issue():
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        building_number = request.form['building_number']
        lab_number = request.form['lab_number']
        pc_number = request.form['pc_number']
        uid = request.form['uid']
        issue_type = request.form['issue_type']
        issue_details = request.form['issue_details']
        
        # Handle image upload
        image_filename = None
        if 'issue_image' in request.files:
            file = request.files['issue_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{uid}_{int(time.time())}_{filename}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_filename = filename
        
        # Insert into database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO issues (uid, building_no, lab_no, pc_no, issue_type, issue_details, issue_image, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'open')
        """, (uid, building_number, lab_number, pc_number, issue_type, issue_details, image_filename))
        
        # Update user's issues_registered count
        cursor.execute("UPDATE users SET issues_registered = issues_registered + 1 WHERE uid = %s", (uid,))
        
        mysql.connection.commit()
        cursor.close()
        
        # Award 5 credits for registering an issue
        update_user_credits(uid, 5)
        
        flash('Issue reported successfully! You earned 5 credits.', 'success')
        return redirect(url_for('auth.dashboard'))
    
    return render_template('issue_reporting.html', name=session.get('name'), uid=session.get('uid'))

@issues_bp.route('/issue/<int:issue_id>')
def view_issue(issue_id):
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT issue_id, uid, building_no, lab_no, pc_no, 
               issue_type, issue_details, issue_image, registered_time
        FROM issues 
        WHERE issue_id = %s
    """, (issue_id,))
    issue_data = cursor.fetchone()
    cursor.close()
    
    if not issue_id:
        flash('Issue not found.', 'error')
        return redirect(url_for('auth.dashboard'))
    
    issue = {
        'issue_id': issue_data[0],
        'uid': issue_data[1],
        'building_number': issue_data[2],
        'lab_number': issue_data[3],
        'pc_number': issue_data[4],
        'issue_type': issue_data[5],
        'issue_details': issue_data[6],
        'issue_image': issue_data[7],
        'registered_time': issue_data[8].strftime('%Y-%m-%d, %H:%M') if issue_data[8] else 'N/A'
    }
    
    return render_template('issue_view.html', issue=issue)

@issues_bp.route('/submit-solution/<int:issue_id>', methods=['GET', 'POST'])
def submit_solution(issue_id=None):
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        issue_id_value = request.form['issue_id_value']
        uid = request.form['uid']
        solution_text = request.form['solution_text']
        
        # Handle image upload
        image_filename = None
        if 'solution_image' in request.files:
            file = request.files['solution_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{uid}_{int(time.time())}_{filename}"
                solution_upload_folder = 'static/uploads/solutions'
                os.makedirs(solution_upload_folder, exist_ok=True)
                file.save(os.path.join(solution_upload_folder, filename))
                image_filename = filename
        
        # Insert solution into database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO solutions (issue_id, uid, solution_text, solution_image)
            VALUES (%s, %s, %s, %s)
        """, (issue_id_value, uid, solution_text, image_filename))
        
        # Update issue status
        cursor.execute("UPDATE issues SET status = 'solved' WHERE issue_id = %s", (issue_id_value,))
        
        # Update user's issues_solved count
        cursor.execute("UPDATE users SET issues_solved = issues_solved + 1 WHERE uid = %s", (uid,))
        
        mysql.connection.commit()
        cursor.close()
        
        # Award 10 credits for solving an issue
        update_user_credits(uid, 10)
        
        flash('Solution submitted successfully! You earned 10 credits.', 'success')
        return redirect(url_for('auth.dashboard'))
    
    # GET request - render form
    return render_template('solution_submission.html', 
                         name=session.get('name'), 
                         uid=session.get('uid'),
                         issue_id=issue_id)

@issues_bp.route('/solved-issues')
def solved_issues():
    if 'uid' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    
    # Get page number from query parameter, default to 1
    page = request.args.get('page', 1, type=int)
    # Get search query
    q = request.args.get('q', '', type=str).strip()
    per_page = 10
    offset = (page - 1) * per_page
    
    cursor = mysql.connection.cursor()
    
    # Build WHERE clause and params for search
    where_clause = "i.status = 'solved'"
    params = []
    count_params = []
    if q:
        like_q = f"%{q}%"
        where_clause += " AND ("
        where_clause += " i.uid LIKE %s OR i.issue_type LIKE %s OR i.building_no LIKE %s OR i.lab_no LIKE %s OR i.pc_no LIKE %s OR i.issue_details LIKE %s OR s.uid LIKE %s"
        params.extend([like_q, like_q, like_q, like_q, like_q, like_q, like_q])
        count_params.extend([like_q, like_q, like_q, like_q, like_q, like_q, like_q])
        # If q is an integer, also match IDs
        if q.isdigit():
            where_clause += " OR i.issue_id = %s OR s.solution_id = %s"
            params.extend([int(q), int(q)])
            count_params.extend([int(q), int(q)])
        where_clause += ")"
    
    # Get total count of solved issues (with optional search)
    count_query = f"""
        SELECT COUNT(*)
        FROM issues i
        LEFT JOIN solutions s ON i.issue_id = s.issue_id
        WHERE {where_clause}
    """
    cursor.execute(count_query, tuple(count_params))
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / per_page)
    
    # Fetch solved issues with solutions (with pagination)
    data_query = f"""
        SELECT 
            i.issue_id, i.building_no, i.lab_no, i.pc_no, 
            i.issue_type, i.issue_details, i.issue_image, i.uid as registered_by, 
            i.registered_time,
            s.solution_id, s.uid as solved_by, s.solution_text, 
            s.solution_image, s.post_time
        FROM issues i
        LEFT JOIN solutions s ON i.issue_id = s.issue_id
        WHERE {where_clause}
        ORDER BY s.post_time DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(data_query, tuple(params + [per_page, offset]))
    
    solved_data = cursor.fetchall()
    cursor.close()
    
    # Format data for template
    solved_list = []
    for row in solved_data:
        solved_list.append({
            'issue_id': row[0],
            'building_number': row[1],
            'lab_number': row[2],
            'pc_number': row[3],
            'issue_type': row[4],
            'issue_details': row[5],
            'issue_image': row[6],
            'registered_by': row[7],
            'registered_time': row[8].strftime('%Y-%m-%d, %H:%M') if row[8] else 'N/A',
            'solution_id': row[9],
            'solved_by': row[10],
            'solution_text': row[11],
            'solution_image': row[12],
            'submitted_time': row[13].strftime('%Y-%m-%d, %H:%M') if row[13] else 'N/A'
        })
    
    return render_template('solved_issues.html',
                         name=session.get('name'),
                         solved_issues=solved_list,
                         page=page,
                         total_pages=total_pages,
                         q=q)
