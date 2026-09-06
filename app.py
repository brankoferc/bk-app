import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bk_secret_key_super_segura_2026'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    vtype = db.Column(db.String(20), default='video')
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
        v1 = Video(title='Lanzamiento oficial de BK 🚀', url='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', vtype='video', user_id=demo_user.id)
        v2 = Video(title='🔴 DJ Set Space en vivo', url='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4', vtype='live', user_id=demo_user.id)
        db.session.add_all([v1, v2])
        db.session.commit()

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BK Videos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f8fafc; color: #0f172a; font-family: sans-serif; }
        .card-border-blue { border: 2px solid #06b6d4; }
        .card-border-red { border: 2px solid #ef4444; }
        .video-card { background-color: #000; border-radius: 1rem; position: relative; overflow: hidden; aspect-ratio: 3/4; display: flex; flex-direction: column; justify-content: space-between; padding: 0.75rem; color: white; cursor: pointer; }
    </style>
</head>
<body class="p-4 max-w-md mx-auto relative min-h-screen pb-24">

    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-2">
            <div class="border-2 border-black font-extrabold text-xl px-3 py-1 rounded-xl cursor-pointer" onclick="location.href='/'">BK</div>
            <button onclick="toggleModal('profileModal')" class="text-slate-600 text-xs font-bold bg-slate-200 px-2 py-1.5 rounded-lg border border-slate-300">👤 @{{ current_user.username }}</button>
        </div>
        <button onclick="toggleSearch()" class="text-slate-700 text-xl p-2"><i class="fas fa-search"></i></button>
    </div>

    <!-- Buscador Oculto -->
    <div id="searchContainer" class="hidden mb-6 bg-white p-2 rounded-xl border-2 border-cyan-500 shadow-sm">
        <form action="/" method="GET" class="flex gap-2 w-full">
            <input type="text" name="q" placeholder="Buscar videos..." class="w-full outline-none text-sm px-2" value="{{ request.args.get('q', '') }}">
            <button type="submit" class="text-cyan-500 font-bold px-2"><i class="fas fa-search"></i></button>
        </form>
    </div>

    <!-- Sección Videos -->
    <h2 class="text-2xl font-bold mb-3">videos -</h2>
    <div class="grid grid-cols-2 gap-3 mb-6">
        {% for video in videos %}
            {% if video.vtype == 'video' %}
            <div onclick="playVideo('{{ video.url }}', '{{ video.title }}', '{{ video.author_user.username }}')" class="video-card card-border-blue">
                <div>
                    <span class="bg-cyan-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-md uppercase">VIDEO</span>
                </div>
                <div>
                    <p class="font-bold text-sm leading-tight mb-1">{{ video.title }}</p>
                    <p class="text-[11px] text-gray-400">@{{ video.author_user.username }}</p>
                </div>
            </div>
            {% endif %}
        {% endfor %}
    </div>

    <!-- Sección Lives -->
    <h2 class="text-2xl font-bold mb-3">Lives -</h2>
    <div class="grid grid-cols-2 gap-3">
        {% for video in videos %}
            {% if video.vtype == 'live' %}
            <div onclick="playVideo('{{ video.url }}', '{{ video.title }}', '{{ video.author_user.username }}')" class="video-card card-border-red">
                <div>
                    <span class="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-md uppercase flex items-center gap-1 w-max">
                        <span class="w-1.5 h-1.5 bg-white rounded-full animate-ping"></span> LIVE
                    </span>
                </div>
                <div>
                    <p class="font-bold text-sm leading-tight mb-1">🔴 {{ video.title }}</p>
                    <p class="text-[11px] text-gray-400">@{{ video.author_user.username }}</p>
                </div>
            </div>
            {% endif %}
        {% endfor %}
    </div>

    <!-- Botón flotante -->
    <button onclick="toggleModal('uploadModal')" class="fixed bottom-6 right-6 w-14 h-14 bg-cyan-400 rounded-full flex items-center justify-center text-white text-2xl shadow-lg font-bold z-40">+</button>

    <!-- Modal Perfil -->
    <div id="profileModal" class="fixed inset-0 bg-black/60 hidden z-50 flex justify-center items-center p-4">
        <div class="bg-white p-6 rounded-2xl w-full max-w-sm text-center shadow-xl">
            <div class="text-5xl mb-3">👤</div>
            <h3 class="font-bold text-xl">@{{ current_user.username }}</h3>
            <p class="text-sm text-slate-500 mb-5">{{ current_user.bio }}</p>
            <div class="flex flex-col gap-3">
                <button onclick="toggleModal('profileModal')" class="w-full py-2.5 bg-slate-200 rounded-lg text-sm font-bold">Volver</button>
                <a href="/logout" class="w-full py-2.5 bg-red-500 text-white rounded-lg text-sm font-bold block text-center">Cerrar Sesión</a>
            </div>
        </div>
    </div>

    <!-- Modal Reproductor -->
    <div id="playerModal" class="fixed inset-0 bg-black/90 hidden z-50 flex-col justify-center items-center p-4">
        <button onclick="closePlayer()" class="absolute top-5 right-5 text-white text-2xl"><i class="fas fa-times"></i></button>
        <h3 id="videoTitle" class="text-white font-bold mb-1 text-center"></h3>
        <p id="videoAuthor" class="text-cyan-400 text-xs font-bold mb-4 text-center"></p>
        <video id="videoPlayer" class="w-full max-w-md rounded-xl" controls autoplay playsinline></video>
    </div>

    <!-- Modal Subir -->
    <div id="uploadModal" class="fixed inset-0 bg-black/60 hidden z-50 flex justify-center items-center p-4">
        <div class="bg-white p-6 rounded-2xl w-full max-w-sm shadow-xl">
            <h3 class="font-bold text-lg mb-4">Añadir Nuevo Video</h3>
            <form action="/add" method="POST" enctype="multipart/form-data" class="flex flex-col gap-3">
                <input type="text" name="title" placeholder="Título del video" class="border p-2 rounded-lg text-sm outline-none" required>
                <div class="flex flex-col text-left">
                    <label class="text-xs text-slate-500 mb-1">Selecciona archivo de video:</label>
                    <input type="file" name="video_file" accept="video/*" class="border p-2 rounded-lg text-sm outline-none bg-slate-50" required>
                </div>
                <select name="type" class="border p-2 rounded-lg text-sm outline-none">
                    <option value="video">Video normal</option>
                    <option value="live">Live / En vivo</option>
                </select>
                <div class="flex gap-2 mt-2">
                    <button type="button" onclick="toggleModal('uploadModal')" class="w-1/2 py-2 border rounded-lg text-sm font-bold">Cancelar</button>
                    <button type="submit" class="w-1/2 py-2 bg-cyan-500 text-white rounded-lg text-sm font-bold">Subir</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function toggleModal(id) {
            const modal = document.getElementById(id);
            modal.classList.toggle('hidden');
            modal.classList.toggle('flex');
        }
        function toggleSearch() {
            const search = document.getElementById('searchContainer');
            search.classList.toggle('hidden');
        }
        function playVideo(url, title, author) {
            document.getElementById('videoTitle').innerText = title;
            document.getElementById('videoAuthor').innerText = '@' + author;
            const player = document.getElementById('videoPlayer');
            player.src = url;
            toggleModal('playerModal');
        }
        function closePlayer() {
            const player = document.getElementById('videoPlayer');
            player.pause();
            player.src = '';
            toggleModal('playerModal');
        }
    </script>
</body>
</html>
"""

AUTH_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BK - {{ title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 flex items-center justify-center h-screen p-4">
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 w-full max-w-sm text-center">
        <div class="font-extrabold text-2xl border-2 border-black inline-block px-3 py-1 rounded-lg mb-4">BK</div>
        <h3 class="font-bold text-lg mb-4">{{ title }}</h3>
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="bg-red-100 text-red-600 p-2 rounded-lg text-xs font-bold mb-3">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}

        <form method="POST" class="flex flex-col gap-3">
            <input type="text" name="username" placeholder="Nombre de usuario" class="p-2.5 border rounded-lg text-sm outline-none" required>
            <input type="password" name="password" placeholder="Contraseña" class="p-2.5 border rounded-lg text-sm outline-none" required>
            <button type="submit" class="bg-cyan-500 text-white py-2.5 rounded-lg font-bold text-sm">{{ 'Entrar' if is_login else 'Registrarse' }}</button>
        </form>

        <div class="mt-5 text-xs text-slate-500">
            {% if is_login %}
                ¿No tienes cuenta? <a href="/register" class="text-cyan-500 font-bold">Regístrate</a>
            {% else %}
                ¿Ya tienes cuenta? <a href="/login" class="text-cyan-500 font-bold">Inicia sesión</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
@login_required
def index():
    query = request.args.get('q', '')
    if query:
        videos = Video.query.filter(Video.title.ilike(f'%{query}%')).all()
    else:
        videos = Video.query.all()
    return render_template_string(INDEX_TEMPLATE, videos=videos, current_user=current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Datos incorrectos.')
    return render_template_string(AUTH_TEMPLATE, title="Iniciar Sesión", is_login=True)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.')
        else:
            new_user = User(username=username, password=generate_password_hash(request.form.get('password'), method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
    return render_template_string(AUTH_TEMPLATE, title="Registro", is_login=False)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/add", methods=['POST'])
@login_required
def add_video():
    title = request.form.get('title')
    vtype = request.form.get('type')
    file = request.files.get('video_file')
    
    if title and file and file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        url = f'/{filepath}'
        
        new_vid = Video(title=title, url=url, vtype=vtype, user_id=current_user.id)
        db.session.add(new_vid)
        db.session.commit()
        
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
