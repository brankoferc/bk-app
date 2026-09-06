import os
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
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

# --- MODELOS DE BASE DE DATOS ---

# Tabla intermedia para el sistema de seguidores
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), default="Hola, soy nuevo en BK.")
    profile_pic = db.Column(db.String(500), default='default')
    
    videos = db.relationship('Video', backref='author_user', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    vtype = db.Column(db.String(20), default='video')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='video', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='video', lazy=True, cascade="all, delete-orphan")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

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
        db.session.add(v1)
        db.session.commit()


# --- MACROS HTML (Para reutilizar la foto de perfil) ---
MACROS = """
{% macro render_pfp(user, size_classes) %}
    {% if user.profile_pic == 'default' %}
        <div class="{{ size_classes }} bg-gradient-to-tr from-cyan-500 to-blue-600 text-white rounded-full flex items-center justify-center font-bold shadow-sm uppercase">
            {{ user.username[0] }}
        </div>
    {% else %}
        <img src="{{ user.profile_pic }}" class="{{ size_classes }} rounded-full object-cover shadow-sm border border-slate-200">
    {% endif %}
{% endmacro %}
"""

# --- PLANTILLA: FEED PRINCIPAL Y PERFIL ---
INDEX_TEMPLATE = MACROS + """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>BK App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style> body { background-color: #f8fafc; font-family: sans-serif; -webkit-tap-highlight-color: transparent;} </style>
</head>
<body class="max-w-md mx-auto relative min-h-screen pb-24 text-slate-900 bg-slate-50">

    <!-- Header -->
    <div class="sticky top-0 z-40 bg-white/90 backdrop-blur-md px-4 py-3 flex justify-between items-center border-b shadow-sm">
        <div class="font-extrabold text-2xl tracking-tighter cursor-pointer" onclick="location.href='/'">BK.</div>
        <div class="flex gap-4 items-center">
            <button onclick="toggleSearch()" class="text-xl text-slate-700"><i class="fas fa-search"></i></button>
            <button onclick="toggleModal('profileSettingsModal')" class="cursor-pointer hover:scale-105 transition">
                {{ render_pfp(current_user, 'w-8 h-8 text-sm') }}
            </button>
        </div>
    </div>

    <div class="p-4">
        {% if profile_user %}
            <!-- CABECERA DE PERFIL -->
            <div class="mb-6 bg-white p-6 rounded-3xl shadow-sm border border-slate-100 text-center relative">
                <div class="flex justify-center mb-3">
                    {{ render_pfp(profile_user, 'w-24 h-24 text-4xl') }}
                </div>
                <h1 class="text-2xl font-extrabold">@{{ profile_user.username }}</h1>
                <p class="text-slate-500 mt-2 text-sm px-4">{{ profile_user.bio }}</p>
                
                <!-- ESTADÍSTICAS: Seguidores, Siguiendo, Me Gusta -->
                <div class="flex justify-center gap-6 mt-4 pt-4 border-t border-slate-100">
                    <div class="text-center">
                        <p class="font-bold text-lg">{{ profile_user.followers.count() }}</p>
                        <p class="text-xs text-slate-400 uppercase tracking-wide">Seguidores</p>
                    </div>
                    <div class="text-center">
                        <p class="font-bold text-lg">{{ profile_user.followed.count() }}</p>
                        <p class="text-xs text-slate-400 uppercase tracking-wide">Siguiendo</p>
                    </div>
                    <div class="text-center">
                        <p class="font-bold text-lg">{{ total_likes }}</p>
                        <p class="text-xs text-slate-400 uppercase tracking-wide">Me Gusta</p>
                    </div>
                </div>

                <!-- BOTÓN DE ACCIÓN -->
                <div class="mt-5">
                {% if profile_user.id == current_user.id %}
                    <button onclick="toggleModal('profileSettingsModal')" class="w-full py-2 bg-slate-100 rounded-xl text-sm font-bold text-slate-700 border">Editar Perfil</button>
                {% else %}
                    <button onclick="toggleFollow({{ profile_user.id }})" id="followBtn" class="w-full py-2 rounded-xl text-sm font-bold transition {{ 'bg-slate-200 text-slate-800' if is_following else 'bg-black text-white' }}">
                        {{ 'Siguiendo' if is_following else 'Seguir' }}
                    </button>
                {% endif %}
                </div>
            </div>
        {% else %}
            <h2 class="font-bold text-xl mb-4 text-slate-800">Descubre</h2>
        {% endif %}

        <!-- FEED DE VIDEOS (Miniaturas) -->
        <div class="grid grid-cols-2 gap-3 mb-6">
            {% for video in videos %}
                <div onclick="location.href='/watch/{{ video.id }}'" class="relative rounded-2xl overflow-hidden aspect-[3/4] bg-slate-900 shadow-sm cursor-pointer group">
                    <video src="{{ video.url }}#t=0.1" preload="metadata" class="absolute inset-0 w-full h-full object-cover opacity-80"></video>
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-end p-3">
                        <p class="font-bold text-white text-sm leading-tight truncate">{{ video.title }}</p>
                        <p class="text-[11px] text-slate-300 mt-0.5">@{{ video.author_user.username }}</p>
                    </div>
                </div>
            {% else %}
                <p class="text-slate-400 text-sm col-span-2 text-center mt-10">No hay videos aún.</p>
            {% endfor %}
        </div>
    </div>

    <!-- Botón Subir -->
    <button onclick="toggleModal('uploadModal')" class="fixed bottom-6 right-6 w-14 h-14 bg-black rounded-full flex items-center justify-center text-white text-2xl shadow-xl font-bold z-40 hover:scale-110"><i class="fas fa-plus"></i></button>

    <!-- MODAL: Búsqueda -->
    <div id="searchContainer" class="fixed inset-0 bg-slate-50 hidden z-50 flex-col">
        <div class="bg-white p-4 flex gap-3 items-center border-b">
            <button onclick="toggleSearch()" class="text-xl text-slate-700 p-2"><i class="fas fa-arrow-left"></i></button>
            <input type="text" id="searchInput" oninput="doSearch()" placeholder="Buscar usuarios..." class="flex-1 bg-slate-100 rounded-full px-4 py-2 outline-none text-sm">
        </div>
        <div id="searchResults" class="p-4 overflow-y-auto flex flex-col gap-2">
            <p class="text-slate-400 text-sm text-center mt-10">Busca a otros usuarios...</p>
        </div>
    </div>

    <!-- MODAL: Editar Perfil -->
    <div id="profileSettingsModal" class="fixed inset-0 bg-black/60 hidden z-50 flex-col justify-end">
        <div class="bg-white rounded-t-3xl p-6 w-full max-w-md mx-auto relative shadow-2xl">
            <button onclick="toggleModal('profileSettingsModal')" class="absolute top-5 right-5 text-slate-400 text-xl"><i class="fas fa-times"></i></button>
            <h2 class="font-bold text-xl mb-5">Editar Perfil</h2>
            
            <form action="/profile/edit" method="POST" enctype="multipart/form-data" class="flex flex-col gap-4">
                <div class="flex items-center gap-4 mb-2">
                    {{ render_pfp(current_user, 'w-16 h-16 text-2xl') }}
                    <div class="flex-1">
                        <label class="text-xs font-bold text-slate-500 uppercase">Cambiar Foto</label>
                        <input type="file" name="profile_pic" accept="image/*" class="w-full text-xs mt-1">
                    </div>
                </div>
                <div>
                    <label class="text-xs font-bold text-slate-500 uppercase">Usuario</label>
                    <input type="text" name="username" value="{{ current_user.username }}" class="w-full bg-slate-50 border p-3 rounded-xl mt-1 font-medium" required>
                </div>
                <div>
                    <label class="text-xs font-bold text-slate-500 uppercase">Bio</label>
                    <textarea name="bio" class="w-full bg-slate-50 border p-3 rounded-xl mt-1 text-sm font-medium h-20">{{ current_user.bio }}</textarea>
                </div>
                <button type="submit" class="bg-black text-white font-bold py-3 rounded-xl w-full">Guardar Cambios</button>
            </form>
            <a href="/logout" class="block w-full py-3 mt-4 bg-red-50 text-red-600 rounded-xl text-sm font-bold text-center border border-red-100">Cerrar Sesión</a>
        </div>
    </div>

    <!-- MODAL: Subir Video -->
    <div id="uploadModal" class="fixed inset-0 bg-black/60 hidden z-50 flex-col justify-end">
        <div class="bg-white rounded-t-3xl p-6 w-full max-w-md mx-auto shadow-2xl relative">
            <button onclick="toggleModal('uploadModal')" class="absolute top-5 right-5 text-slate-400 text-xl"><i class="fas fa-times"></i></button>
            <h3 class="font-bold text-xl mb-5">Subir Video</h3>
            <form action="/add" method="POST" enctype="multipart/form-data" class="flex flex-col gap-4">
                <input type="text" name="title" placeholder="Título del video..." class="bg-slate-50 border p-3 rounded-xl text-sm font-medium" required>
                <div>
                    <label class="text-xs font-bold text-slate-500 uppercase">Archivo de Video (MP4)</label>
                    <input type="file" name="video_file" accept="video/*" class="w-full mt-1 border p-2 rounded-xl text-sm bg-slate-50" required>
                </div>
                <button type="submit" class="w-full py-3 mt-2 bg-blue-600 text-white rounded-xl text-sm font-bold">Publicar</button>
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
            toggleModal('searchContainer');
        }
        async function doSearch() {
            const q = document.getElementById('searchInput').value;
            const box = document.getElementById('searchResults');
            if(q.trim().length < 1) { box.innerHTML = ''; return; }
            const res = await fetch('/api/search?q=' + encodeURIComponent(q));
            const data = await res.json();
            box.innerHTML = data.users.map(u => `
                <div onclick="location.href='/u/${u.username}'" class="flex items-center gap-3 p-3 bg-white rounded-xl shadow-sm border border-slate-100 cursor-pointer">
                    <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">${u.username.charAt(0).toUpperCase()}</div>
                    <div><p class="font-bold text-slate-800">@${u.username}</p><p class="text-xs text-slate-500">${u.bio}</p></div>
                </div>
            `).join('') || '<p class="text-center text-sm text-slate-400">Sin resultados</p>';
        }
        async function toggleFollow(userId) {
            const res = await fetch('/api/follow', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: userId})
            });
            const data = await res.json();
            const btn = document.getElementById('followBtn');
            if(data.following) {
                btn.innerText = 'Siguiendo';
                btn.className = 'w-full py-2 rounded-xl text-sm font-bold transition bg-slate-200 text-slate-800';
            } else {
                btn.innerText = 'Seguir';
                btn.className = 'w-full py-2 rounded-xl text-sm font-bold transition bg-black text-white';
            }
            location.reload(); // Recargar para actualizar los números
        }
    </script>
</body>
</html>
"""

# --- PLANTILLA: PANTALLA DE VER VIDEO (Igual a tu dibujo) ---
WATCH_TEMPLATE = MACROS + """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ video.title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style> body { background-color: #f8fafc; font-family: sans-serif; -webkit-tap-highlight-color: transparent;} </style>
</head>
<body class="max-w-md mx-auto relative min-h-screen bg-white">

    <!-- Barra de navegación simple -->
    <div class="flex items-center p-3 border-b">
        <button onclick="location.href='/'" class="text-xl p-2"><i class="fas fa-arrow-left"></i></button>
        <h1 class="font-bold ml-2 truncate">{{ video.title }}</h1>
    </div>

    <!-- 1. EL RECTÁNGULO DEL VIDEO -->
    <div class="w-full bg-black aspect-video relative flex items-center">
        <video id="vidPlayer" src="{{ video.url }}" controls autoplay playsinline class="w-full h-full object-contain"></video>
    </div>

    <!-- 2. PERFIL, CORAZÓN Y COMPARTIR (Como tu dibujo) -->
    <div class="px-4 py-4 flex items-center justify-between border-b border-slate-100">
        <!-- Izquierda: Círculo de perfil -->
        <div class="flex items-center gap-3 cursor-pointer" onclick="location.href='/u/{{ video.author_user.username }}'">
            {{ render_pfp(video.author_user, 'w-12 h-12 text-xl') }}
            <div>
                <p class="font-bold text-slate-900 leading-tight">@{{ video.author_user.username }}</p>
                <p class="text-xs text-slate-500">{{ video.author_user.followers.count() }} seguidores</p>
            </div>
        </div>
        
        <!-- Derecha: Corazón y Flecha -->
        <div class="flex items-center gap-5">
            <button onclick="toggleLike()" class="flex flex-col items-center">
                <i id="likeIcon" class="fas fa-heart text-2xl {{ 'text-red-500' if liked else 'text-slate-300' }}"></i>
                <span id="likeCount" class="text-xs font-bold mt-1 text-slate-600">{{ video.likes|length }}</span>
            </button>
            <button onclick="shareVideo()" class="flex flex-col items-center">
                <i class="fas fa-share text-2xl text-slate-300"></i>
                <span class="text-xs font-bold mt-1 text-slate-600">Share</span>
            </button>
        </div>
    </div>

    <!-- 3. CAJA REDONDEADA DE COMENTARIOS (Como tu dibujo) -->
    <div class="p-4">
        <div class="border border-slate-200 rounded-3xl p-4 bg-slate-50">
            <h3 class="font-bold text-sm mb-3">Comentarios (<span id="cCount">{{ video.comments|length }}</span>)</h3>
            
            <div id="commentsList" class="flex flex-col gap-3 mb-4 max-h-40 overflow-y-auto">
                {% for c in video.comments %}
                    <div class="flex gap-2">
                        <div class="font-bold text-xs cursor-pointer" onclick="location.href='/u/{{ c.author.username }}'">@{{ c.author.username }}:</div>
                        <div class="text-xs text-slate-700">{{ c.text }}</div>
                    </div>
                {% else %}
                    <p id="noComments" class="text-xs text-slate-400">No hay comentarios aún.</p>
                {% endfor %}
            </div>

            <div class="flex gap-2">
                <input type="text" id="newComment" placeholder="Añadir comentario..." class="flex-1 bg-white border border-slate-200 rounded-full px-3 py-2 text-xs outline-none focus:border-blue-500">
                <button onclick="postComment()" class="bg-slate-900 text-white px-4 rounded-full text-xs font-bold">Enviar</button>
            </div>
        </div>
    </div>

    <!-- 4. VIDEOS _ (Solo aparece si hay otros videos) -->
    {% if other_videos %}
    <div class="p-4 bg-slate-50 border-t border-slate-100 min-h-screen">
        <h2 class="font-bold text-lg mb-3">Videos _</h2>
        <div class="flex flex-col gap-3">
            {% for ov in other_videos %}
            <div onclick="location.href='/watch/{{ ov.id }}'" class="flex gap-3 bg-white p-2 rounded-xl border border-slate-100 shadow-sm cursor-pointer">
                <video src="{{ ov.url }}#t=0.1" class="w-32 h-20 rounded-lg bg-black object-cover"></video>
                <div class="flex flex-col justify-center">
                    <p class="font-bold text-sm text-slate-800 line-clamp-2">{{ ov.title }}</p>
                    <p class="text-xs text-slate-500 mt-1">@{{ ov.author_user.username }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <script>
        const videoId = {{ video.id }};
        
        async function toggleLike() {
            const res = await fetch('/api/action', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'like', video_id: videoId})
            });
            const data = await res.json();
            if(data.status === 'success') {
                document.getElementById('likeIcon').className = data.active ? 'fas fa-heart text-2xl text-red-500' : 'fas fa-heart text-2xl text-slate-300';
                document.getElementById('likeCount').innerText = data.count;
            }
        }

        async function postComment() {
            const input = document.getElementById('newComment');
            const text = input.value.trim();
            if(!text) return;
            
            const res = await fetch('/api/comment', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({video_id: videoId, text: text})
            });
            const data = await res.json();
            if(data.status === 'success') {
                input.value = '';
                location.reload(); // Recarga simple para ver el comentario al instante
            }
        }

        function shareVideo() {
            if (navigator.share) {
                navigator.share({ title: '{{ video.title }}', url: window.location.href });
            } else {
                navigator.clipboard.writeText(window.location.href);
                alert('Enlace copiado');
            }
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
<body class="bg-slate-50 flex items-center justify-center min-h-screen p-4 font-sans">
    <div class="bg-white p-8 rounded-3xl shadow-xl border border-slate-100 w-full max-w-sm text-center">
        <div class="font-extrabold text-3xl mb-2 tracking-tighter">BK.</div>
        <h3 class="font-bold text-slate-500 text-sm mb-6 uppercase">{{ title }}</h3>
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="bg-red-50 text-red-600 p-3 rounded-xl text-xs font-bold mb-5 border">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}

        <form method="POST" class="flex flex-col gap-4">
            <input type="text" name="username" placeholder="Nombre de usuario" class="p-3 bg-slate-50 border rounded-xl text-sm outline-none font-medium" required>
            <input type="password" name="password" placeholder="Contraseña" class="p-3 bg-slate-50 border rounded-xl text-sm outline-none font-medium" required>
            <button type="submit" class="bg-black text-white py-3 mt-2 rounded-xl font-bold text-sm">{{ 'Entrar' if is_login else 'Crear Cuenta' }}</button>
        </form>

        <div class="mt-8 text-xs text-slate-500 font-medium">
            {% if is_login %}
                ¿No tienes cuenta? <a href="/register" class="text-blue-600 font-bold">Regístrate</a>
            {% else %}
                ¿Ya tienes cuenta? <a href="/login" class="text-blue-600 font-bold">Inicia sesión</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# --- RUTAS DE FLASK ---

@app.route("/")
@login_required
def index():
    videos = Video.query.order_by(Video.id.desc()).all()
    return render_template_string(INDEX_TEMPLATE, videos=videos, current_user=current_user, profile_user=None)

@app.route("/watch/<int:video_id>")
@login_required
def watch_video(video_id):
    video = Video.query.get_or_404(video_id)
    # Cargar otros videos (excluyendo el actual)
    other_videos = Video.query.filter(Video.id != video_id).order_by(Video.id.desc()).limit(5).all()
    liked = Like.query.filter_by(user_id=current_user.id, video_id=video.id).first() is not None
    return render_template_string(WATCH_TEMPLATE, video=video, other_videos=other_videos, liked=liked, current_user=current_user)

@app.route("/u/<username>")
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).order_by(Video.id.desc()).all()
    is_following = current_user.is_following(user) if current_user.id != user.id else False
    
    # Calcular Me Gusta totales del usuario
    total_likes = sum([len(v.likes) for v in user.videos])
    
    return render_template_string(INDEX_TEMPLATE, videos=videos, current_user=current_user, profile_user=user, is_following=is_following, total_likes=total_likes)

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
        username = request.form.get('username').strip()
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
    file = request.files.get('video_file')
    if title and file and file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        new_vid = Video(title=title, url=f'/{filepath}', user_id=current_user.id)
        db.session.add(new_vid)
        db.session.commit()
    return redirect(url_for('index'))

@app.route("/profile/edit", methods=['POST'])
@login_required
def edit_profile():
    new_user = request.form.get('username', '').strip()
    if new_user and new_user != current_user.username:
        if User.query.filter_by(username=new_user).first():
            flash('Ese nombre de usuario ya está ocupado.')
            return redirect(url_for('index'))
        current_user.username = new_user
        
    current_user.bio = request.form.get('bio', '').strip()
    
    # Manejar subida de foto de perfil
    file = request.files.get('profile_pic')
    if file and file.filename != '':
        filename = secure_filename(f"pfp_{current_user.id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        current_user.profile_pic = f'/{filepath}'

    db.session.commit()
    return redirect(url_for('index'))

# --- API ---

@app.route("/api/search")
@login_required
def api_search():
    q = request.args.get('q', '')
    if len(q) < 1: return jsonify({'users': []})
    users = User.query.filter(User.username.ilike(f'%{q}%')).limit(6).all()
    return jsonify({'users': [{'username': u.username, 'bio': u.bio} for u in users]})

@app.route("/api/follow", methods=['POST'])
@login_required
def api_follow():
    data = request.json
    user_to_follow = User.query.get(data['user_id'])
    if not user_to_follow or user_to_follow.id == current_user.id:
        return jsonify({'error': 'Invalid user'}), 400
        
    if current_user.is_following(user_to_follow):
        current_user.unfollow(user_to_follow)
        following = False
    else:
        current_user.follow(user_to_follow)
        following = True
        
    db.session.commit()
    return jsonify({'status': 'success', 'following': following})

@app.route("/api/action", methods=['POST'])
@login_required
def api_action():
    data = request.json
    action, video_id = data.get('action'), data.get('video_id')
    
    if action == 'like':
        existing = Like.query.filter_by(user_id=current_user.id, video_id=video_id).first()
        active = False
        if existing:
            db.session.delete(existing)
        else:
            db.session.add(Like(user_id=current_user.id, video_id=video_id))
            active = True
        db.session.commit()
        count = Like.query.filter_by(video_id=video_id).count()
        return jsonify({'status': 'success', 'active': active, 'count': count})

@app.route("/api/comment", methods=['POST'])
@login_required
def api_comment():
    data = request.json
    c = Comment(text=data['text'], user_id=current_user.id, video_id=data['video_id'])
    db.session.add(c)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
