# Disaster Management System - Setup & Usage Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Navigate to project directory**
   ```bash
   cd Disaster_Management_System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open browser: `http://localhost:5000`
   - Application will be ready to use

---

## 👥 Default User Setup

### Creating an Admin User (First Time Setup)

Since admin registration is restricted, you need to create an admin user manually:

```bash
# Open Python interactive shell
python

# Run these commands:
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('admin123'),
        role='admin',
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")
    
# Exit Python shell
exit()
```

### Test Accounts

You can now create test users:

1. **Public User Account**
   - Go to `/register`
   - Username: `testuser`
   - Email: `testuser@example.com`
   - Password: `testpass123`
   - Role: Public User ✓

2. **Responder Account**
   - Go to `/register`
   - Username: `responder1`
   - Email: `responder@example.com`
   - Password: `responder123`
   - Role: Emergency Responder ✓

3. **Admin Account** (manually created above)
   - Username: `admin`
   - Password: `admin123`
   - Role: Administrator

---

## 🎯 Using the System

### Public User Workflow

1. **Register** → Create account as Public User
2. **Login** → Access your dashboard
3. **Report Incident** → Click "Report Incident" button
   - Fill incident details (title, type, severity, location, description)
   - Optionally upload a photo
   - Submit report
4. **View Map** → See all incidents on live map
5. **Track Reports** → Check status of your reported incidents
6. **View Details** → Click on any incident to see more info

### Responder Workflow

1. **Register/Login** → As Responder role
2. **View Dashboard** → See all active incidents
3. **Manage Incidents**:
   - Click on incident to view details
   - Update status: Active → In Progress → Resolved
   - Assign resources
4. **Resource Management**:
   - Click "Resources" in navigation
   - Add new resources (Medical, Food, Transport, etc.)
   - Allocate resources to incidents
   - Deallocate when no longer needed
5. **Monitor Status** → Check incident statuses in real-time

### Admin Workflow

1. **Login** → With admin credentials
2. **Dashboard** → Overview of all system metrics
3. **Manage Users**:
   - View all users
   - Change user roles
   - Activate/Deactivate accounts
4. **Manage Incidents**:
   - Filter by status or severity
   - Assign to responders
   - Update statuses
5. **View Analytics**:
   - Incident trends (30-day chart)
   - Severity distribution
   - Type distribution
   - Resolution rates
6. **Activity Log**:
   - Review all user actions
   - Track system usage
   - Audit trail

---

## 📊 Features by Role

### 👤 Public User Features
- [x] Report incidents
- [x] View live disaster map
- [x] Track own incident reports
- [x] View incident details
- [x] Update profile

### 👨‍🚒 Responder Features
- [x] All Public features
- [x] View all incidents
- [x] Update incident status
- [x] Manage resources
- [x] Allocate resources to incidents
- [x] Filter incidents

### 🛡️ Admin Features
- [x] All Responder features
- [x] Manage all users
- [x] Change user roles
- [x] View analytics
- [x] Access activity logs
- [x] System configuration

---

## 🗺️ Map Features

The Live Map page shows:
- **All Active Incidents** with color-coded severity:
  - 🟢 Green: Low severity
  - 🟠 Orange: Medium severity
  - 🔴 Red: High severity
  - 🔴 Dark Red: Critical severity

- **Incident Popup** with:
  - Title
  - Type
  - Severity
  - Status
  - Time reported
  - View Details button

- **Statistics**:
  - Severity distribution chart
  - Incident count by type
  - Total active incidents

---

## 📝 Database Information

### Database Location
- File: `instance/database.db` (SQLite)
- Auto-created on first run
- Updated with new schema on startup

### Tables
1. **user** - User accounts and credentials
2. **incident** - Disaster incidents
3. **resource** - Emergency resources
4. **activity_log** - User action audit trail

### Reset Database (If Needed)
```bash
# Delete the database file
rm instance/database.db

# Restart the application
python app.py

# New database will be created automatically
```

---

## 🔧 Configuration

### App Settings (app.py)
```python
app.config['SECRET_KEY'] = 'disaster_management_secret_123'  # Change for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database URL
app.config['UPLOAD_FOLDER'] = 'uploads'  # File upload directory
```

### Server Settings
```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Change port if needed
```

---

## 🐛 Troubleshooting

### Issue: Port 5000 already in use
**Solution**: Change port in `app.py`
```python
app.run(debug=True, port=5001)  # Use different port
```

### Issue: Module not found error
**Solution**: Install missing dependencies
```bash
pip install -r requirements.txt
```

### Issue: Database locked error
**Solution**: Restart the application
```bash
# Stop current process (Ctrl+C)
# Wait a few seconds
# Restart: python app.py
```

### Issue: Page not loading
**Solution**: Check browser console for errors
1. Press F12 to open Developer Tools
2. Check Console tab for JavaScript errors
3. Check Network tab for failed requests
4. Restart Flask server

---

## 📱 Responsive Design

The application works on:
- ✅ Desktop browsers (1920x1080 and up)
- ✅ Tablets (768px - 1024px width)
- ✅ Mobile phones (320px - 768px width)
- ✅ All modern browsers (Chrome, Firefox, Safari, Edge)

---

## 🔒 Security Notes

### Important for Production
1. **Change SECRET_KEY** in app.py to a random string
2. **Use strong passwords** for admin and user accounts
3. **Enable HTTPS** when deploying
4. **Regular backups** of database.db
5. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`

### Best Practices
- Never share admin credentials
- Regularly review activity logs
- Deactivate unused accounts
- Use strong passwords (8+ chars, mixed case, numbers)
- Keep the application updated

---

## 📞 Support

### Common Questions

**Q: How do I create the first admin account?**
A: Use the Python script provided in "Default User Setup" section above.

**Q: Can users change their password?**
A: Currently not implemented. Can be added as a future feature.

**Q: Can admins create users directly?**
A: Currently users must self-register. Admin can manage existing users.

**Q: Is data automatically backed up?**
A: No. Implement regular database backups for production use.

**Q: Can I export incident reports?**
A: Not in current version. Can be added in future updates.

---

## 🎨 Customization

### Change Application Name
Edit in `base.html`:
```html
<a class="navbar-brand" href="/">
    <i class="bi bi-exclamation-triangle-fill"></i> Your App Name
</a>
```

### Change Color Scheme
Edit `style.css`:
```css
:root {
    --primary-color: #2196F3;      /* Change primary color */
    --danger-color: #f44336;       /* Change danger color */
    --success-color: #4CAF50;      /* Change success color */
    /* ... etc ... */
}
```

### Add Custom Favicon
Add to `templates/base.html` in `<head>`:
```html
<link rel="icon" type="image/png" href="{{ url_for('static', filename='favicon.png') }}">
```

---

**Version**: 2.0 Enhanced
**Status**: Production Ready
**Last Updated**: 2024
