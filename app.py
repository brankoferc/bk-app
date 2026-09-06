import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bk_secret_key_super_segura_2026'

database_url = os.environ.get('DATABASE_URL', 'sqlite:///bk_database.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), default="Creador de contenido en BK.")
    videos = db.relationship('Video', backref='author_user', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    is_live = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='oficial_bk').first():
        demo_user = User(username='oficial_bk', password=generate_password_hash('1234', method='scrypt'), bio='Cuenta oficial del equipo de BK 🚀')
        db.session.add(demo_user)
        db.session.commit()
        v1 = Video(title='Lanzamiento oficial de BK 🚀', url='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', is_live=False, user_id=demo_user.id)
        v2 = Video(title='🔴 DJ Set Space en vivo', url='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4', is_live=True, user_id=demo_user.id)
        db.session.add_all([v1, v2])
        db.session.commit()

@app.route("/")
@login_required
def home():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Usuario o contraseña incorrectos.')
    return render_template('auth.html', title="Iniciar Sesión", btn_text="Entrar", is_login=True)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.')
        else:
            hashed_password = generate_password_hash(password, method='scrypt')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('auth.html', title="Regístrate", btn_text="Crear Cuenta", is_login=False)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/update_profile", methods=['POST'])
@login_required
def update_profile():
    new_username = request.form.get('new_username')
    new_bio = request.form.get('new_bio')
    if new_username:
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != current_user.id:
            flash('Ese nombre de usuario ya está ocupado.')
        else:
            current_user.username = new_username
    if new_bio:
        current_user.bio = new_bio
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/api/videos")
@login_required
def get_videos():
    videos = Video.query.all()
    result = []
    for v in videos:
        author = User.query.get(v.user_id)
        result.append({
            'id': v.id,
            'title': v.title,
            'url': v.url,
            'is_live': v.is_live,
            'author': author.username if author else 'desconocido'
        })
    return jsonify(result)

@app.route("/api/add_video", methods=['POST'])
@login_required
def add_video():
    title = request.form.get('title')
    url = request.form.get('url')
    if title and url:
        new_video = Video(title=title, url=url, user_id=current_user.id)
        db.session.add(new_video)
        db.session.commit()
    return redirect(url_for('home'))

@app.route("/api/search_users")
@login_required
def search_users():
    query = request.args.get('query', '')
    users = User.query.filter(User.username.ilike(f'%{query}%')).limit(5).all()
    return jsonify([{'username': u.username} for u in users])

@app.route("/api/user_profile/<username>")
@login_required
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Not found'}), 404
    
    videos = [{'id': v.id, 'title': v.title, 'url': v.url} for v in user.videos]
    return jsonify({
        'username': user.username,
        'bio': user.bio,
        'videos': videos
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
