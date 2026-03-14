# ============================================================
#  BloodLink - Blood Donation Camp Management System
#  Flask Backend - app.py
#  Technologies: Python, Flask, MySQL, XAMPP
# ============================================================

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import functools

# ============================================================
# APP SETUP
# ============================================================
app = Flask(__name__)

# Secret key for session encryption (change this in production!)
app.secret_key = 'bloodlink_secret_key_2025'

# ============================================================
# MYSQL CONFIGURATION
# Make sure XAMPP MySQL is running on port 3306
# ============================================================
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = ''          # Default XAMPP MySQL has no password
app.config['MYSQL_DB']       = 'blood_donation_system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Returns rows as dicts

mysql = MySQL(app)

# ============================================================
# DECORATORS - Login Required Guards
# ============================================================

def login_required(f):
    """Protects donor routes. Redirects to login if not logged in."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'donor_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Protects admin routes. Redirects to admin login if not logged in."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# PUBLIC ROUTES
# ============================================================

@app.route('/')
def index():
    """Home page - shows stats and upcoming camps."""
    cur = mysql.connection.cursor()

    # Get total counts for stats display
    cur.execute("SELECT COUNT(*) AS total FROM camps")
    total_camps = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM donors")
    total_donors = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM registrations")
    total_registrations = cur.fetchone()['total']

    # Get 3 upcoming camps for homepage preview
    cur.execute("""
        SELECT * FROM camps
        WHERE date >= CURDATE()
        ORDER BY date ASC
        LIMIT 3
    """)
    upcoming_camps = cur.fetchall()
    cur.close()

    return render_template('index.html',
        total_camps=total_camps,
        total_donors=total_donors,
        total_registrations=total_registrations,
        upcoming_camps=upcoming_camps
    )


@app.route('/camps')
def camps():
    """Camps page - shows all upcoming camps with optional filter."""
    camp_type = request.args.get('type', 'all')  # filter parameter

    cur = mysql.connection.cursor()

    if camp_type == 'all':
        cur.execute("SELECT * FROM camps ORDER BY date ASC")
    else:
        cur.execute(
            "SELECT * FROM camps WHERE camp_type = %s ORDER BY date ASC",
            (camp_type,)
        )

    all_camps = cur.fetchall()
    cur.close()

    return render_template('camps.html', camps=all_camps, active_filter=camp_type)


# ============================================================
# DONOR REGISTRATION & AUTH
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Donor registration page."""
    if request.method == 'POST':
        # Collect form data
        name         = request.form.get('name', '').strip()
        age          = request.form.get('age', '')
        gender       = request.form.get('gender', '')
        blood_group  = request.form.get('blood_group', '')
        phone        = request.form.get('phone', '').strip()
        email        = request.form.get('email', '').strip().lower()
        city         = request.form.get('city', '').strip()
        password     = request.form.get('password', '')
        confirm_pass = request.form.get('confirm_password', '')

        # --- Server-side validation ---
        errors = []

        if not name or len(name) < 2:
            errors.append('Full name must be at least 2 characters.')
        if not age or not age.isdigit() or not (18 <= int(age) <= 60):
            errors.append('Age must be between 18 and 60.')
        if not gender:
            errors.append('Please select your gender.')
        if not blood_group:
            errors.append('Please select your blood group.')
        if not phone or len(phone) != 10 or not phone.isdigit():
            errors.append('Phone must be a valid 10-digit number.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if not city:
            errors.append('City is required.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_pass:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')

        # --- Check if email already exists ---
        cur = mysql.connection.cursor()
        cur.execute("SELECT donor_id FROM donors WHERE email = %s", (email,))
        existing = cur.fetchone()

        if existing:
            flash('An account with this email already exists. Please login.', 'error')
            cur.close()
            return render_template('register.html')

        # --- Hash password and insert donor ---
        hashed_password = generate_password_hash(password)
        cur.execute("""
            INSERT INTO donors (name, age, gender, blood_group, phone, email, city, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, int(age), gender, blood_group, phone, email, city, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please login to continue.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Donor login page."""
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM donors WHERE email = %s", (email,))
        donor = cur.fetchone()
        cur.close()

        if donor and check_password_hash(donor['password'], password):
            # Set session variables
            session['donor_id']   = donor['donor_id']
            session['donor_name'] = donor['name']
            session['blood_group'] = donor['blood_group']
            flash(f"Welcome back, {donor['name']}!", 'success')
            return redirect(url_for('donor_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logs out the donor and clears their session."""
    session.pop('donor_id', None)
    session.pop('donor_name', None)
    session.pop('blood_group', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))


# ============================================================
# DONOR DASHBOARD & PROFILE
# ============================================================

@app.route('/dashboard')
@login_required
def donor_dashboard():
    """Donor dashboard - shows stats, camps, and registrations."""
    donor_id = session['donor_id']
    cur = mysql.connection.cursor()

    # Get donor info
    cur.execute("SELECT * FROM donors WHERE donor_id = %s", (donor_id,))
    donor = cur.fetchone()

    # Count how many times this donor has donated (confirmed registrations)
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM registrations
        WHERE donor_id = %s AND status = 'confirmed'
    """, (donor_id,))
    total_donations = cur.fetchone()['total']

    # Count registered camps
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM registrations
        WHERE donor_id = %s
    """, (donor_id,))
    registered_camps = cur.fetchone()['total']

    # Get upcoming camps (not yet registered)
    cur.execute("""
        SELECT c.* FROM camps c
        WHERE c.date >= CURDATE()
        AND c.camp_id NOT IN (
            SELECT camp_id FROM registrations WHERE donor_id = %s
        )
        ORDER BY c.date ASC
        LIMIT 5
    """, (donor_id,))
    upcoming_camps = cur.fetchall()

    # Get this donor's registrations with camp details
    cur.execute("""
        SELECT c.camp_name, c.date, c.location, r.registration_date, r.status, r.registration_id
        FROM registrations r
        JOIN camps c ON r.camp_id = c.camp_id
        WHERE r.donor_id = %s
        ORDER BY c.date DESC
    """, (donor_id,))
    my_registrations = cur.fetchall()

    cur.close()

    return render_template('donor_dashboard.html',
        donor=donor,
        total_donations=total_donations,
        registered_camps=registered_camps,
        lives_saved=total_donations * 3,   # 1 donation = up to 3 lives
        upcoming_camps=upcoming_camps,
        my_registrations=my_registrations
    )


@app.route('/profile')
@login_required
def donor_profile():
    """Donor profile page."""
    donor_id = session['donor_id']
    cur = mysql.connection.cursor()

    # Get donor details
    cur.execute("SELECT * FROM donors WHERE donor_id = %s", (donor_id,))
    donor = cur.fetchone()

    # Get donation history (confirmed registrations in the past)
    cur.execute("""
        SELECT c.camp_name, c.date, c.location, r.status
        FROM registrations r
        JOIN camps c ON r.camp_id = c.camp_id
        WHERE r.donor_id = %s AND r.status = 'confirmed' AND c.date < CURDATE()
        ORDER BY c.date DESC
    """, (donor_id,))
    donation_history = cur.fetchall()

    # Get upcoming registered camps
    cur.execute("""
        SELECT c.camp_name, c.date, c.location, r.status, r.registration_date
        FROM registrations r
        JOIN camps c ON r.camp_id = c.camp_id
        WHERE r.donor_id = %s AND c.date >= CURDATE()
        ORDER BY c.date ASC
    """, (donor_id,))
    registered_camps = cur.fetchall()

    cur.close()

    return render_template('donor_profile.html',
        donor=donor,
        donation_history=donation_history,
        registered_camps=registered_camps
    )


# ============================================================
# CAMP REGISTRATION (Donor registers for a camp)
# ============================================================

@app.route('/register_camp/<int:camp_id>', methods=['POST'])
@login_required
def register_camp(camp_id):
    """Registers the logged-in donor for a specific camp."""
    donor_id = session['donor_id']
    cur = mysql.connection.cursor()

    # Check if already registered
    cur.execute("""
        SELECT registration_id FROM registrations
        WHERE donor_id = %s AND camp_id = %s
    """, (donor_id, camp_id))
    already = cur.fetchone()

    if already:
        flash('You are already registered for this camp.', 'error')
    else:
        cur.execute("""
            INSERT INTO registrations (donor_id, camp_id, status)
            VALUES (%s, %s, 'confirmed')
        """, (donor_id, camp_id))
        mysql.connection.commit()
        flash('Successfully registered for the camp! See you there.', 'success')

    cur.close()
    return redirect(url_for('donor_dashboard'))


@app.route('/cancel_registration/<int:registration_id>', methods=['POST'])
@login_required
def cancel_registration(registration_id):
    """Allows a donor to cancel their camp registration."""
    donor_id = session['donor_id']
    cur = mysql.connection.cursor()

    # Make sure the registration belongs to this donor
    cur.execute("""
        DELETE FROM registrations
        WHERE registration_id = %s AND donor_id = %s
    """, (registration_id, donor_id))
    mysql.connection.commit()
    cur.close()

    flash('Your registration has been cancelled.', 'success')
    return redirect(url_for('donor_dashboard'))


# ============================================================
# ADMIN LOGIN & AUTH
# ============================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('admin_login.html')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cur.fetchone()
        cur.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin_id']   = admin['admin_id']
            session['admin_name'] = admin['username']
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Logs out the admin."""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Admin logged out.', 'success')
    return redirect(url_for('admin_login'))


# ============================================================
# ADMIN DASHBOARD & MANAGEMENT
# ============================================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with overview statistics."""
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM camps")
    total_camps = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM donors")
    total_donors = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM registrations")
    total_registrations = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM registrations WHERE status='confirmed'")
    total_confirmed = cur.fetchone()['total']

    # Recent camps
    cur.execute("SELECT * FROM camps ORDER BY created_at DESC LIMIT 10")
    camps = cur.fetchall()

    # All donors
    cur.execute("SELECT * FROM donors ORDER BY created_at DESC")
    donors = cur.fetchall()

    # All registrations with donor and camp info
    cur.execute("""
        SELECT r.registration_id, d.name AS donor_name, d.blood_group,
               c.camp_name, c.date AS camp_date, c.location,
               r.registration_date, r.status
        FROM registrations r
        JOIN donors d ON r.donor_id = d.donor_id
        JOIN camps c  ON r.camp_id  = c.camp_id
        ORDER BY r.registration_date DESC
    """)
    registrations = cur.fetchall()
    cur.close()

    return render_template('admin_dashboard.html',
        total_camps=total_camps,
        total_donors=total_donors,
        total_registrations=total_registrations,
        total_confirmed=total_confirmed,
        camps=camps,
        donors=donors,
        registrations=registrations
    )


# ============================================================
# ADMIN - CAMP CRUD OPERATIONS
# ============================================================

@app.route('/admin/camp/add', methods=['POST'])
@admin_required
def admin_add_camp():
    """Adds a new blood donation camp."""
    camp_name   = request.form.get('camp_name', '').strip()
    location    = request.form.get('location', '').strip()
    date        = request.form.get('date', '')
    organizer   = request.form.get('organizer', '').strip()
    description = request.form.get('description', '').strip()
    camp_type   = request.form.get('camp_type', 'general')

    if not camp_name or not location or not date or not organizer:
        flash('All required fields must be filled.', 'error')
        return redirect(url_for('admin_dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO camps (camp_name, location, date, organizer, description, camp_type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (camp_name, location, date, organizer, description, camp_type))
    mysql.connection.commit()
    cur.close()

    flash(f'Camp "{camp_name}" added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/camp/edit/<int:camp_id>', methods=['POST'])
@admin_required
def admin_edit_camp(camp_id):
    """Updates an existing camp's details."""
    camp_name   = request.form.get('camp_name', '').strip()
    location    = request.form.get('location', '').strip()
    date        = request.form.get('date', '')
    organizer   = request.form.get('organizer', '').strip()
    description = request.form.get('description', '').strip()
    camp_type   = request.form.get('camp_type', 'general')

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE camps
        SET camp_name=%s, location=%s, date=%s, organizer=%s,
            description=%s, camp_type=%s
        WHERE camp_id=%s
    """, (camp_name, location, date, organizer, description, camp_type, camp_id))
    mysql.connection.commit()
    cur.close()

    flash('Camp updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/camp/delete/<int:camp_id>', methods=['POST'])
@admin_required
def admin_delete_camp(camp_id):
    """Deletes a camp and all its registrations (CASCADE handles this via FK)."""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM camps WHERE camp_id = %s", (camp_id,))
    mysql.connection.commit()
    cur.close()

    flash('Camp deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


# ============================================================
# ADMIN - GET SINGLE CAMP (for edit modal pre-fill via AJAX)
# ============================================================

@app.route('/admin/camp/get/<int:camp_id>')
@admin_required
def admin_get_camp(camp_id):
    """Returns camp data as JSON for edit modal pre-filling."""
    from flask import jsonify
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM camps WHERE camp_id = %s", (camp_id,))
    camp = cur.fetchone()
    cur.close()

    if camp:
        # Convert date to string for JSON
        camp['date'] = str(camp['date'])
        camp['created_at'] = str(camp['created_at'])
        return jsonify(camp)
    return jsonify({'error': 'Camp not found'}), 404


# ============================================================
# RUN THE APP
# ============================================================
if __name__ == '__main__':
    # debug=True shows errors in browser during development
    # Turn off debug=True before submitting or deploying
    app.run(debug=True, port=5000)
