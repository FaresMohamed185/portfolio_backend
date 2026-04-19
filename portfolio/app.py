from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# ========== التعديل هنا ==========
app = Flask(__name__)
# =================================

app.config['SECRET_KEY'] = 'your-secret-key-here-change-it'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tools = db.Column(db.String(200), nullable=False)  # تخزين كـ "Power BI,Python,SQL"
    pdf_file = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(200), nullable=False)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== CREATE DATABASE ====================

with app.app_context():
    db.create_all()
    # إنشاء مستخدم admin افتراضي (username: admin, password: admin123)
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# ==================== ROUTES ====================

@app.route('/')
def index():
    # تحديث عدد المشاهدات
    home_view = PageView.query.filter_by(page='home').first()
    if home_view:
        home_view.views += 1
    else:
        home_view = PageView(page='home', views=1)
        db.session.add(home_view)
    db.session.commit()
    
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/project/<int:project_id>/view', methods=['POST'])
def increment_project_view(project_id):
    project = Project.query.get_or_404(project_id)
    project.views += 1
    db.session.commit()
    return jsonify({'views': project.views})

@app.route('/send-message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if not name or not email or not message:
        flash('جميع الحقول مطلوبة', 'error')
        return redirect(url_for('index') + '#contact')
    
    new_message = Message(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()
    
    flash('تم إرسال رسالتك بنجاح! سأتصل بك قريباً', 'success')
    return redirect(url_for('index') + '#contact')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    messages = Message.query.order_by(Message.date.desc()).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    stats = PageView.query.all()
    
    # إحصائيات المشاهدات
    stats_dict = {s.page: s.views for s in stats}
    
    return render_template('admin.html', messages=messages, projects=projects, stats=stats_dict)

@app.route('/admin/add-project', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    description = request.form.get('description')
    tools = request.form.get('tools')
    pdf_file = request.form.get('pdf_file')
    image_file = request.form.get('image_file')
    
    new_project = Project(
        title=title,
        description=description,
        tools=tools,
        pdf_file=pdf_file,
        image_file=image_file
    )
    db.session.add(new_project)
    db.session.commit()
    
    flash('تم إضافة المشروع بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-project/<int:project_id>')
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('تم حذف المشروع بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/mark-read/<int:message_id>')
@login_required
def mark_read(message_id):
    message = Message.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/api/stats')
def get_stats():
    stats = PageView.query.all()
    projects = Project.query.all()
    return jsonify({
        'page_views': {s.page: s.views for s in stats},
        'project_views': {p.id: p.views for p in projects}
    })

if __name__ == '__main__':
    app.run(debug=True)