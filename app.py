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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), default="Hola, soy nuevo en BK.")
    videos = db.relationship('Video', backref='author_user', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    vtype = db.Column(db.String(20), default='video')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='video', lazy=True, cascade="all, delete-orphan")
    saves = db.relationship('Save', backref='video', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='video', lazy=True, cascade="all, delete-orphan")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

class Save(db.Model):
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

# --- PLANTILLAS HTML MODERNAS ---

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>BK App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; -webkit-tap-highlight-color: transparent;}
        .hide-scroll::-webkit-scrollbar { display: none; }
        .glass { background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); }
        .player-glass { background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.1) 100%); }
    </style>
</head>
<body class="max-w-md mx-auto relative min-h-screen pb-24 text-slate-900 bg-slate-50 hide-scroll">

    <!-- Header Glassmorphism -->
    <div class="sticky top-0 z-40 glass px-4 py-3 flex justify-between items-center border-b border-slate-200 shadow-sm">
        <div class="font-extrabold text-2xl tracking-tighter cursor-pointer" onclick="location.href='/'">BK.</div>
        <div class="flex gap-4 items-center">
            <button onclick="toggleSearch()" class="text-xl text-slate-700"><i class="fas fa-search"></i></button>
            <button onclick="toggleModal('profileModal')" class="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 text-white flex justify-center items-center font-bold shadow-md cursor-pointer hover:scale-105 transition">{{ current_user.username[0]|upper }}</button>
        </div>
    </div>

    <div class="p-4">
        {% if profile_user %}
            <!-- Cabecera de Perfil de Usuario Visitado -->
            <div class="mb-6 bg-white p-6 rounded-3xl shadow-sm border border-slate-100 text-center">
                <div class="w-20 h-20 bg-gradient-to-tr from-cyan-500 to-blue-600 text-white text-3xl mx-auto rounded-full flex items-center justify-center font-bold mb-3 shadow-md">{{ profile_user.username[0]|upper }}</div>
                <h1 class="text-2xl font-extrabold">@{{ profile_user.username }}</h1>
                <p class="text-slate-500 mt-2 text-sm">{{ profile_user.bio }}</p>
                {% if profile_user.id == current_user.id %}
                    <button onclick="toggleModal('profileModal')" class="mt-4 px-6 py-2 bg-slate-100 rounded-full text-sm font-bold text-slate-700 border">Editar Perfil</button>
                {% endif %}
            </div>
            <h2 class="font-bold text-lg mb-4">Videos publicados</h2>
        {% else %}
            <!-- Cabecera Feed General -->
            <h2 class="font-bold text-xl mb-4 text-slate-800">Para ti ✨</h2>
        {% endif %}

        <!-- Grid de Videos con Portadas Reales -->
        <div class="grid grid-cols-2 gap-3 mb-6">
            {% for video in videos %}
                {% set liked = current_user.id in video.likes|map(attribute='user_id')|list %}
                {% set saved = current_user.id in video.saves|map(attribute='user_id')|list %}
                <div onclick="playVideo({{ video.id }}, '{{ video.url }}', '{{ video.title }}', '{{ video.author_user.username }}', {{ 'true' if liked else 'false' }}, {{ 'true' if saved else 'false' }}, {{ video.likes|length }})" 
                     class="relative rounded-2xl overflow-hidden aspect-[3/4] bg-slate-900 shadow-sm cursor-pointer group">
                    
                    <!-- Portada de video usando el primer cuadro -->
                    <video src="{{ video.url }}#t=0.1" preload="metadata" class="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-300"></video>
                    
                    <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent flex flex-col justify-end p-3">
                        {% if video.vtype == 'live' %}
                            <span class="absolute top-2 left-2 bg-red-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1"><span class="w-1.5 h-1.5 bg-white rounded-full animate-ping"></span>LIVE</span>
                        {% endif %}
                        <p class="font-bold text-white text-sm leading-tight drop-shadow-md truncate">{{ video.title }}</p>
                        <p class="text-[11px] text-slate-300 mt-0.5">@{{ video.author_user.username }}</p>
                        <div class="flex gap-2 text-white/90 text-xs mt-2 font-bold">
                            <span><i class="fas fa-heart text-red-500"></i> {{ video.likes|length }}</span>
                        </div>
                    </div>
                </div>
            {% else %}
                <p class="text-slate-400 text-sm col-span-2 text-center mt-10">No hay videos aún.</p>
            {% endfor %}
        </div>
    </div>

    <!-- Botón flotante Subir -->
    <button onclick="toggleModal('uploadModal')" class="fixed bottom-6 right-6 w-14 h-14 bg-black rounded-full flex items-center justify-center text-white text-2xl shadow-xl font-bold z-40 hover:scale-110 transition"><i class="fas fa-plus"></i></button>

    <!-- Modal: Búsqueda en Tiempo Real -->
    <div id="searchContainer" class="fixed inset-0 bg-slate-50 hidden z-50 flex-col">
        <div class="glass p-4 flex gap-3 items-center border-b">
            <button onclick="toggleSearch()" class="text-xl text-slate-700 p-2"><i class="fas fa-arrow-left"></i></button>
            <input type="text" id="searchInput" oninput="doSearch()" placeholder="Buscar usuarios o videos..." class="flex-1 bg-white border shadow-sm rounded-full px-4 py-2 outline-none text-sm focus:border-cyan-500">
        </div>
        <div id="searchResults" class="p-4 overflow-y-auto flex flex-col gap-2 pb-20">
            <p class="text-slate-400 text-sm text-center mt-10 font-medium">Escribe algo para empezar a buscar...</p>
        </div>
    </div>

    <!-- Modal: Reproductor de Video a Pantalla Completa (Estilo Reels/TikTok) -->
    <div id="playerModal" class="fixed inset-0 bg-black hidden z-50 flex-col justify-center items-center">
        <!-- Video -->
        <video id="videoPlayer" class="absolute inset-0 w-full h-full object-cover" autoplay loop playsinline></video>
        
        <!-- Controles Flotantes sobre el video -->
        <div class="absolute inset-0 flex flex-col justify-between pointer-events-none player-glass">
            
            <!-- Barra Superior (Volver) -->
            <div class="p-4 pt-8 flex justify-between pointer-events-auto">
                <button onclick="closePlayer()" class="text-white text-2xl drop-shadow-lg"><i class="fas fa-chevron-left"></i></button>
            </div>
            
            <!-- Zona Inferior (Info y Botones) -->
            <div class="p-4 pb-8 flex items-end justify-between pointer-events-auto">
                <!-- Info Izquierda -->
                <div class="text-white w-3/4 pr-4">
                    <h3 id="videoAuthor" class="font-bold text-lg drop-shadow-md cursor-pointer hover:underline mb-1"></h3>
                    <p id="videoTitle" class="text-sm drop-shadow-md mb-2"></p>
                </div>
                
                <!-- Botones Derecha -->
                <div class="flex flex-col items-center gap-5 text-white">
                    <button onclick="toggleAction('like')" class="flex flex-col items-center group">
                        <i id="likeIcon" class="fas fa-heart text-3xl drop-shadow-md transition transform group-hover:scale-110"></i>
                        <span id="likeCount" class="text-xs font-bold mt-1 drop-shadow-md">0</span>
                    </button>
                    
                    <button onclick="openComments()" class="flex flex-col items-center group">
                        <i class="fas fa-comment-dots text-3xl drop-shadow-md transition transform group-hover:scale-110"></i>
                        <span class="text-xs font-bold mt-1 drop-shadow-md">Chat</span>
                    </button>
                    
                    <button onclick="toggleAction('save')" class="flex flex-col items-center group">
                        <i id="saveIcon" class="fas fa-bookmark text-3xl drop-shadow-md transition transform group-hover:scale-110"></i>
                        <span class="text-xs font-bold mt-1 drop-shadow-md">Guardar</span>
                    </button>

                    <button onclick="shareVideo()" class="flex flex-col items-center group">
                        <i class="fas fa-share text-3xl drop-shadow-md transition transform group-hover:scale-110"></i>
                        <span class="text-xs font-bold mt-1 drop-shadow-md">Compartir</span>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Panel de Comentarios (Se desliza hacia arriba) -->
        <div id="commentsPanel" class="absolute bottom-0 w-full h-3/4 bg-white rounded-t-3xl hidden flex-col z-50 transition-transform shadow-[0_-10px_40px_rgba(0,0,0,0.3)]">
            <div class="flex justify-between items-center p-4 border-b">
                <h4 class="font-bold text-lg">Comentarios</h4>
                <button onclick="closeComments()" class="text-slate-500 p-2"><i class="fas fa-times text-xl"></i></button>
            </div>
            <div id="commentsList" class="flex-1 overflow-y-auto p-4 flex flex-col gap-4 text-sm bg-slate-50 hide-scroll">
                <!-- Se inyectan con JS -->
            </div>
            <div class="p-3 bg-white border-t flex gap-2 items-center">
                <input type="text" id="newComment" class="flex-1 bg-slate-100 border-none rounded-full px-4 py-3 outline-none text-sm" placeholder="Añade un comentario lindo...">
                <button onclick="postComment()" class="bg-black text-white rounded-full w-12 h-12 flex justify-center items-center font-bold hover:bg-slate-800"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>

    <!-- Modal: Editar Perfil / Opciones -->
    <div id="profileModal" class="fixed inset-0 bg-black/60 hidden z-50 flex-col justify-end">
        <div class="bg-white rounded-t-3xl p-6 w-full max-w-md mx-auto flex flex-col relative shadow-2xl">
            <button onclick="toggleModal('profileModal')" class="absolute top-5 right-5 text-slate-400 text-xl"><i class="fas fa-times"></i></button>
            <h2 class="font-bold text-xl mb-5">Configuración de Perfil</h2>
            
            {% if get_flashed_messages() %}
                <p class="text-red-500 text-xs font-bold mb-3">{{ get_flashed_messages()[0] }}</p>
            {% endif %}

            <form action="/profile/edit" method="POST" class="flex flex-col gap-4 mb-4">
                <div>
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Nombre de Usuario</label>
                    <input type="text" name="username" value="{{ current_user.username }}" class="w-full bg-slate-50 border p-3 rounded-xl outline-none mt-1 font-medium focus:border-cyan-500 focus:bg-white" required>
                </div>
                <div>
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Presentación / Bio</label>
                    <textarea name="bio" class="w-full bg-slate-50 border p-3 rounded-xl outline-none mt-1 text-sm font-medium focus:border-cyan-500 focus:bg-white resize-none h-24" required>{{ current_user.bio }}</textarea>
                </div>
                <button type="submit" class="bg-black text-white font-bold py-3 rounded-xl w-full shadow-md">Guardar Cambios</button>
            </form>
            
            <a href="/logout" class="w-full py-3 bg-red-50 text-red-600 rounded-xl text-sm font-bold text-center border border-red-100">Cerrar Sesión</a>
        </div>
    </div>

    <!-- Modal: Subir Video -->
    <div id="uploadModal" class="fixed inset-0 bg-black/60 hidden z-50 flex-col justify-end">
        <div class="bg-white rounded-t-3xl p-6 w-full max-w-md mx-auto shadow-2xl relative">
            <button onclick="toggleModal('uploadModal')" class="absolute top-5 right-5 text-slate-400 text-xl"><i class="fas fa-times"></i></button>
            <h3 class="font-bold text-xl mb-5">Nuevo Video</h3>
            <form action="/add" method="POST" enctype="multipart/form-data" class="flex flex-col gap-4">
                <input type="text" name="title" placeholder="Añade un título llamativo..." class="bg-slate-50 border p-3 rounded-xl text-sm outline-none font-medium focus:border-cyan-500 focus:bg-white" required>
                <div class="flex flex-col text-left">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Selecciona archivo (MP4):</label>
                    <input type="file" name="video_file" accept="video/*" class="border p-2 rounded-xl text-sm outline-none bg-slate-50 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100" required>
                </div>
                <select name="type" class="bg-slate-50 border p-3 rounded-xl text-sm outline-none font-medium focus:border-cyan-500 focus:bg-white">
                    <option value="video">Clip Normal</option>
                    <option value="live">Grabación en Vivo</option>
                </select>
                <button type="submit" class="w-full py-3 mt-2 bg-gradient-to-r from-cyan-500 to-blue-600 shadow-md shadow-blue-500/30 text-white rounded-xl text-sm font-bold">Publicar Ahora</button>
            </form>
        </div>
    </div>

    <script>
        let currentVideoId = null;

        function toggleModal(id) {
            const modal = document.getElementById(id);
            if (modal.classList.contains('hidden')) {
                modal.classList.remove('hidden');
                modal.classList.add('flex');
            } else {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        }
        
        function toggleSearch() {
            toggleModal('searchContainer');
            document.getElementById('searchInput').focus();
        }

        // Lógica de buscador en tiempo real
        async function doSearch() {
            const q = document.getElementById('searchInput').value;
            const box = document.getElementById('searchResults');
            
            if(q.trim().length < 1) { 
                box.innerHTML = '<p class="text-slate-400 text-sm text-center mt-10 font-medium">Escribe algo para empezar a buscar...</p>'; 
                return; 
            }
            
            const res = await fetch('/api/search?q=' + encodeURIComponent(q));
            const data = await res.json();
            
            let html = '';
            if(data.users.length > 0) {
                html += '<h4 class="font-bold text-xs text-slate-400 uppercase tracking-wider mb-2">Usuarios</h4>';
                data.users.forEach(u => {
                    const initial = u.username.charAt(0).toUpperCase();
                    html += `
                        <div onclick="location.href='/u/${u.username}'" class="flex items-center gap-3 p-3 bg-white rounded-2xl shadow-sm border border-slate-100 cursor-pointer hover:border-cyan-300 transition">
                            <div class="w-12 h-12 bg-gradient-to-tr from-cyan-400 to-blue-500 rounded-full flex items-center justify-center text-white font-bold shadow-sm">${initial}</div>
                            <div class="flex-1 overflow-hidden">
                                <p class="font-bold text-slate-800">@${u.username}</p>
                                <p class="text-xs text-slate-500 truncate">${u.bio}</p>
                            </div>
                        </div>`;
                });
            }
            
            if(data.videos.length > 0) {
                html += '<h4 class="font-bold text-xs text-slate-400 uppercase tracking-wider mt-4 mb-2">Videos</h4>';
                data.videos.forEach(v => {
                    html += `
                        <div onclick="playVideo(${v.id}, '${v.url}', '${v.title}', '${v.author}', false, false, 0)" class="flex items-center gap-3 p-2 bg-white rounded-2xl shadow-sm border border-slate-100 cursor-pointer hover:border-cyan-300 transition">
                            <video src="${v.url}#t=0.1" class="w-16 h-20 rounded-xl bg-black object-cover"></video>
                            <div class="flex-1 overflow-hidden">
                                <p class="font-bold text-sm text-slate-800 truncate">${v.title}</p>
                                <p class="text-xs text-slate-500">@${v.author}</p>
                            </div>
                        </div>`;
                });
            }
            
            if(html === '') html = '<p class="text-slate-400 text-sm text-center mt-10 font-medium">No se encontraron resultados 😢</p>';
            box.innerHTML = html;
        }

        // Lógica de Reproductor de Video
        function playVideo(id, url, title, author, isLiked, isSaved, likesCount) {
            currentVideoId = id;
            document.getElementById('videoTitle').innerText = title;
            document.getElementById('videoAuthor').innerText = '@' + author;
            document.getElementById('videoAuthor').onclick = () => location.href = '/u/' + author;
            
            const player = document.getElementById('videoPlayer');
            player.src = url;
            player.play();
            
            // Actualizar botones según estado
            document.getElementById('likeIcon').className = isLiked ? 'fas fa-heart text-4xl drop-shadow-md text-red-500' : 'fas fa-heart text-4xl drop-shadow-md text-white';
            document.getElementById('likeCount').innerText = likesCount;
            document.getElementById('saveIcon').className = isSaved ? 'fas fa-bookmark text-3xl drop-shadow-md text-yellow-400' : 'fas fa-bookmark text-3xl drop-shadow-md text-white';
            
            document.getElementById('commentsPanel').classList.add('hidden');
            document.getElementById('commentsPanel').classList.remove('flex');
            toggleModal('playerModal');
        }

        function closePlayer() {
            const player = document.getElementById('videoPlayer');
            player.pause();
            player.src = '';
            toggleModal('playerModal');
        }

        // Interacciones Reales (Likes y Guardados)
        async function toggleAction(action) {
            if(!currentVideoId) return;
            const res = await fetch('/api/action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action, video_id: currentVideoId})
            });
            const data = await res.json();
            
            if(data.status === 'success') {
                if(action === 'like') {
                    const icon = document.getElementById('likeIcon');
                    icon.className = data.active ? 'fas fa-heart text-4xl drop-shadow-md text-red-500 scale-125 transition-transform' : 'fas fa-heart text-4xl drop-shadow-md text-white transition-transform';
                    setTimeout(() => icon.classList.remove('scale-125'), 200);
                    document.getElementById('likeCount').innerText = data.count;
                } else if(action === 'save') {
                    const icon = document.getElementById('saveIcon');
                    icon.className = data.active ? 'fas fa-bookmark text-3xl drop-shadow-md text-yellow-400 scale-125 transition-transform' : 'fas fa-bookmark text-3xl drop-shadow-md text-white transition-transform';
                    setTimeout(() => icon.classList.remove('scale-125'), 200);
                }
            }
        }

        // Sistema de Comentarios
        async function openComments() {
            const panel = document.getElementById('commentsPanel');
            panel.classList.remove('hidden');
            panel.classList.add('flex');
            
            const list = document.getElementById('commentsList');
            list.innerHTML = '<p class="text-center text-slate-400 mt-5">Cargando...</p>';
            
            const res = await fetch('/api/comments/' + currentVideoId);
            const comments = await res.json();
            
            if(comments.length === 0) {
                list.innerHTML = '<p class="text-center text-slate-400 mt-5 text-sm">Sé el primero en comentar.</p>';
            } else {
                list.innerHTML = comments.map(c => `
                    <div class="bg-white p-3 rounded-2xl shadow-sm border border-slate-100 flex gap-3 items-start">
                        <div class="w-8 h-8 rounded-full bg-slate-200 flex-shrink-0 flex items-center justify-center font-bold text-xs cursor-pointer" onclick="location.href='/u/${c.username}'">${c.username.charAt(0).toUpperCase()}</div>
                        <div>
                            <p class="font-bold text-xs text-slate-500 cursor-pointer" onclick="location.href='/u/${c.username}'">@${c.username}</p>
                            <p class="text-sm mt-0.5 text-slate-800 font-medium">${c.text}</p>
                        </div>
                    </div>
                `).join('');
            }
        }

        function closeComments() {
            document.getElementById('commentsPanel').classList.add('hidden');
            document.getElementById('commentsPanel').classList.remove('flex');
        }

        async function postComment() {
            const input = document.getElementById('newComment');
            const text = input.value.trim();
            if(!text || !currentVideoId) return;
            
            const res = await fetch('/api/comment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({video_id: currentVideoId, text: text})
            });
            const data = await res.json();
            if(data.status === 'success') {
                input.value = '';
                openComments(); // Recargar lista automáticamente
            }
        }

        // Función Compartir
        function shareVideo() {
            const url = window.location.origin;
            if (navigator.share) {
                navigator.share({ title: 'Video en BK', text: '¡Mira este increíble video en BK!', url: url });
            } else {
                navigator.clipboard.writeText(url);
                alert('¡Enlace de la app copiado al portapapeles!');
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
        <h3 class="font-bold text-slate-500 text-sm mb-6 uppercase tracking-wider">{{ title }}</h3>
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="bg-red-50 text-red-600 p-3 rounded-xl text-xs font-bold mb-5 border border-red-100">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}

        <form method="POST" class="flex flex-col gap-4">
            <input type="text" name="username" placeholder="Nombre de usuario" class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none font-medium focus:border-cyan-500 focus:bg-white transition" required>
            <input type="password" name="password" placeholder="Contraseña" class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none font-medium focus:border-cyan-500 focus:bg-white transition" required>
            <button type="submit" class="bg-black hover:bg-slate-800 transition text-white py-3.5 mt-2 rounded-xl font-bold text-sm shadow-md">{{ 'Entrar' if is_login else 'Crear Cuenta' }}</button>
        </form>

        <div class="mt-8 text-xs text-slate-500 font-medium">
            {% if is_login %}
                ¿No tienes cuenta? <a href="/register" class="text-cyan-600 font-bold hover:underline">Regístrate</a>
            {% else %}
                ¿Ya tienes cuenta? <a href="/login" class="text-cyan-600 font-bold hover:underline">Inicia sesión</a>
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

@app.route("/u/<username>")
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).order_by(Video.id.desc()).all()
    return render_template_string(INDEX_TEMPLATE, videos=videos, current_user=current_user, profile_user=user)

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
    vtype = request.form.get('type')
    file = request.files.get('video_file')
    
    if title and file and file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        new_vid = Video(title=title, url=f'/{filepath}', vtype=vtype, user_id=current_user.id)
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
    db.session.commit()
    return redirect(url_for('index'))

# --- API PARA INTERACCIONES EN TIEMPO REAL ---

@app.route("/api/search")
@login_required
def api_search():
    q = request.args.get('q', '')
    if len(q) < 1: return jsonify({'users': [], 'videos': []})
    users = User.query.filter(User.username.ilike(f'%{q}%')).limit(6).all()
    videos = Video.query.filter(Video.title.ilike(f'%{q}%')).limit(6).all()
    return jsonify({
        'users': [{'username': u.username, 'bio': u.bio} for u in users],
        'videos': [{'id': v.id, 'title': v.title, 'url': v.url, 'author': v.author_user.username} for v in videos]
    })

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
        
    elif action == 'save':
        existing = Save.query.filter_by(user_id=current_user.id, video_id=video_id).first()
        active = False
        if existing:
            db.session.delete(existing)
        else:
            db.session.add(Save(user_id=current_user.id, video_id=video_id))
            active = True
        db.session.commit()
        return jsonify({'status': 'success', 'active': active})

@app.route("/api/comment", methods=['POST'])
@login_required
def api_comment():
    data = request.json
    c = Comment(text=data['text'], user_id=current_user.id, video_id=data['video_id'])
    db.session.add(c)
    db.session.commit()
    return jsonify({'status': 'success