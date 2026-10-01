# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import os
from models import db, User, Incident, Resource, ActivityLog

app = Flask(__name__)
app.config['SECRET_KEY'] = 'disaster_management_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# ===== DECORATORS FOR ROLE-BASED ACCESS =====
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def responder_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'responder']:
            flash('Responder or Admin access required!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(action, description):
    """Log user activity"""
    if current_user.is_authenticated:
        log = ActivityLog(user_id=current_user.id, action=action, description=description)
        db.session.add(log)
        db.session.commit()

# ===== PUBLIC ROUTES =====
@app.route('/')
def index():
    total_incidents = Incident.query.count()
    active_incidents = Incident.query.filter_by(status='Active').count()
    return render_template('index.html', 
                         total_incidents=total_incidents,
                         active_incidents=active_incidents)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']
        role = request.form.get('role', 'public')
        
        # Restrict admin registration - only public and responder can self-register
        if role == 'admin':
            flash('Admin registration is restricted. Contact system administrator.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if email and User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(
            username=username, 
            email=email,
            password=generate_password_hash(password), 
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        
        log_activity('REGISTER', f'User registered as {role}')
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            if not user.is_active:
                flash('Your account has been deactivated!', 'danger')
                return redirect(url_for('login'))
            
            login_user(user)
            log_activity('LOGIN', 'User logged in')
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_activity('LOGOUT', 'User logged out')
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# ===== USER DASHBOARD =====
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    page = request.args.get('page', 1, type=int)
    incidents = Incident.query.order_by(Incident.timestamp.desc()).paginate(page=page, per_page=10)
    
    total = Incident.query.count()
    active = Incident.query.filter_by(status='Active').count()
    resolved = Incident.query.filter_by(status='Resolved').count()
    
    # Get user's reported incidents if public user
    my_incidents = []
    if current_user.role == 'public':
        my_incidents = Incident.query.filter_by(reported_by=current_user.id).all()
    
    return render_template('dashboard.html', 
                         incidents=incidents.items,
                         page=page,
                         total=total, 
                         active=active, 
                         resolved=resolved,
                         my_incidents=my_incidents,
                         role=current_user.role)

# ===== INCIDENT MANAGEMENT =====
@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if request.method == 'POST':
        title = request.form.get('title')
        disaster_type = request.form.get('disaster_type', 'General')
        severity = request.form.get('severity', 'Medium')
        description = request.form.get('description')
        lat = float(request.form.get('lat', 28.61))
        lon = float(request.form.get('lon', 77.20))
        
        incident = Incident(
            title=title,
            disaster_type=disaster_type,
            severity=severity,
            latitude=lat,
            longitude=lon,
            description=description,
            reported_by=current_user.id
        )
        db.session.add(incident)
        db.session.commit()
        
        log_activity('REPORT_INCIDENT', f'Reported incident: {title}')
        flash('Incident Reported Successfully!', 'success')
        return redirect(url_for('map_view'))
    
    disaster_types = ['General', 'Flood', 'Earthquake', 'Fire', 'Storm', 'Landslide', 'Tsunami']
    return render_template('report.html', disaster_types=disaster_types)

@app.route('/map')
def map_view():
    incidents = Incident.query.all()
    return render_template('map.html', incidents=incidents)

@app.route('/incident/<int:incident_id>')
def incident_detail(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    return render_template('incident_detail.html', incident=incident)

@app.route('/incident/<int:incident_id>/update', methods=['POST'])
@responder_required
def update_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    
    incident.status = request.form.get('status', incident.status)
    incident.severity = request.form.get('severity', incident.severity)
    incident.priority = request.form.get('priority', incident.priority)
    incident.updated_at = datetime.utcnow()
    
    if request.form.get('assigned_to'):
        incident.assigned_to = int(request.form.get('assigned_to'))
    
    db.session.commit()
    
    log_activity('UPDATE_INCIDENT', f'Updated incident #{incident_id}')
    flash('Incident Updated!', 'success')
    return redirect(url_for('dashboard'))

# ===== RESOURCE MANAGEMENT =====
@app.route('/resources')
@responder_required
def resources():
    resources = Resource.query.all()
    incidents = Incident.query.filter_by(status='Active').all()
    return render_template('resources.html', resources=resources, incidents=incidents)

@app.route('/resource/add', methods=['POST'])
@responder_required
def add_resource():
    resource = Resource(
        name=request.form.get('name'),
        resource_type=request.form.get('resource_type'),
        quantity=int(request.form.get('quantity', 0)),
        unit=request.form.get('unit'),
        location=request.form.get('location'),
        available=True
    )
    db.session.add(resource)
    db.session.commit()
    
    log_activity('ADD_RESOURCE', f'Added resource: {resource.name}')
    flash('Resource Added!', 'success')
    return redirect(url_for('resources'))

@app.route('/resource/<int:resource_id>/allocate', methods=['POST'])
@responder_required
def allocate_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    incident_id = request.form.get('incident_id')
    
    resource.allocated_to = int(incident_id) if incident_id else None
    resource.available = not incident_id
    db.session.commit()
    
    log_activity('ALLOCATE_RESOURCE', f'Allocated resource #{resource_id}')
    flash('Resource Allocated!', 'success')
    return redirect(url_for('resources'))

# ===== ADMIN PANEL =====
@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_incidents = Incident.query.count()
    total_resources = Resource.query.count()
    active_incidents = Incident.query.filter_by(status='Active').count()
    
    # Get incidents by severity
    severity_distribution = {}
    for severity in ['Low', 'Medium', 'High', 'Critical']:
        severity_distribution[severity] = Incident.query.filter_by(severity=severity).count()
    
    # Get incidents by status
    status_distribution = {}
    for status in ['Active', 'In Progress', 'Resolved', 'Closed']:
        status_distribution[status] = Incident.query.filter_by(status=status).count()
    
    # Get recent activity
    recent_activity = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    # Get unassigned incidents
    unassigned_incidents = Incident.query.filter_by(assigned_to=None, status='Active').all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_incidents=total_incidents,
                         total_resources=total_resources,
                         active_incidents=active_incidents,
                         severity_distribution=severity_distribution,
                         status_distribution=status_distribution,
                         recent_activity=recent_activity,
                         unassigned_incidents=unassigned_incidents)

@app.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot deactivate yourself!', 'danger')
        return redirect(url_for('manage_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    log_activity('TOGGLE_USER', f'User #{user_id} status toggled')
    flash(f'User {user.username} has been {"activated" if user.is_active else "deactivated"}!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot change your own role!', 'danger')
        return redirect(url_for('manage_users'))
    
    new_role = request.form.get('role')
    old_role = user.role
    user.role = new_role
    db.session.commit()
    
    log_activity('CHANGE_ROLE', f'Changed user #{user_id} role from {old_role} to {new_role}')
    flash(f'{user.username} role changed to {new_role}!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/incidents')
@admin_required
def manage_incidents():
    filter_status = request.args.get('status')
    filter_severity = request.args.get('severity')
    
    query = Incident.query
    
    if filter_status:
        query = query.filter_by(status=filter_status)
    if filter_severity:
        query = query.filter_by(severity=filter_severity)
    
    incidents = query.order_by(Incident.timestamp.desc()).all()
    responders = User.query.filter_by(role='responder').all()
    
    return render_template('admin_incidents.html', 
                         incidents=incidents,
                         responders=responders)

@app.route('/admin/analytics')
@admin_required
def analytics():
    # Get data for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    incidents_trend = {}
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=30-i)
        count = Incident.query.filter(
            Incident.timestamp >= date.replace(hour=0, minute=0, second=0),
            Incident.timestamp < (date + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        ).count()
        incidents_trend[date.strftime('%d %b')] = count
    
    # Severity distribution
    severity_counts = {}
    for severity in ['Low', 'Medium', 'High', 'Critical']:
        severity_counts[severity] = Incident.query.filter_by(severity=severity).count()
    
    # Type distribution
    all_incidents = Incident.query.all()
    type_counts = {}
    for incident in all_incidents:
        type_counts[incident.disaster_type] = type_counts.get(incident.disaster_type, 0) + 1
    
    # Response stats
    total_resolved = Incident.query.filter_by(status='Resolved').count()
    total_incidents = Incident.query.count()
    resolution_rate = (total_resolved / total_incidents * 100) if total_incidents > 0 else 0
    
    return render_template('admin_analytics.html',
                         incidents_trend=incidents_trend,
                         severity_counts=severity_counts,
                         type_counts=type_counts,
                         resolution_rate=round(resolution_rate, 2),
                         total_incidents=total_incidents)

@app.route('/admin/activity-log')
@admin_required
def activity_log():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=20)
    return render_template('admin_activity_log.html', logs=logs.items, page=page)

# ===== API ENDPOINTS =====
@app.route('/api/incidents/stats')
def get_incident_stats():
    total = Incident.query.count()
    active = Incident.query.filter_by(status='Active').count()
    resolved = Incident.query.filter_by(status='Resolved').count()
    
    return jsonify({
        'total': total,
        'active': active,
        'resolved': resolved
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)