from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BK</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #f8f9fa; color: #111; padding: 15px; padding-bottom: 80px; }
        
        /* Header */
        header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; border-bottom: 1px solid #eee; margin-bottom: 15px; }
        .header-left { display: flex; align-items: center; gap: 10px; }
        .logo { font-weight: 900; font-size: 22px; border: 2.5px solid #000; padding: 2px 10px; border-radius: 8px; letter-spacing: 1px; cursor: pointer; }
        
        /* Navegación superior (Perfil y Suscripciones) */
        .nav-links { display: flex; gap: 8px; }
        .nav-tab { font-size: 13px; font-weight: 700; background: #eee; border: none; padding: 6px 10px; border-radius: 8px; cursor: pointer; color: #333; transition: background 0.2s; }
        .nav-tab:hover, .nav-tab.active { background: #00B4D8; color: #fff; }

        .search-btn { font-size: 20px; border: none; background: none; cursor: pointer; }

        /* Search Bar */
        .search-container { display: none; margin-bottom: 15px; gap: 8px; align-items: center; background: #fff; padding: 6px 10px; border-radius: 12px; border: 1.5px solid #00B4D8; }
        .search-container input { flex: 1; border: none; outline: none; font-size: 14px; background: transparent; margin: 0; }
        .mic-btn { background: none; border: none; font-size: 18px; cursor: pointer; padding: 4px; border-radius: 50%; }
        .mic-btn.recording { animation: pulse 1s infinite alternate; background: #ff4b4b; color: #fff; }

        @keyframes pulse { from { opacity: 1; } to { opacity: 0.4; } }

        /* Sections */
        .section-title { font-size: 18px; font-weight: 800; margin-bottom: 12px; display: flex; align-items: center; gap: 5px; }
        
        /* Carousel */
        .carousel { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 25px; scrollbar-width: none; }
        .carousel::-webkit-scrollbar { display: none; }

        /* Cards */
        .card { 
            min-width: 160px; width: 160px; height: 220px; 
            background-color: #000; border-radius: 16px; padding: 12px; 
            border: 2px solid #00B4D8; box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
            transition: transform 0.2s; cursor: pointer; position: relative; 
            overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; 
        }
        .card.live { border-color: #ff4b4b; }
        .card:active { transform: scale(0.97); }
        .card-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.85; z-index: 1; pointer-events: none; }
        .card-content { position: relative; z-index: 2; }
        .badge { font-size: 10px; font-weight: 800; color: #fff; background: #00B4D8; padding: 3px 8px; border-radius: 6px; display: inline-block; margin-bottom: 6px; }
        .badge.live { background: #ff4b4b; }
        .card-title { font-size: 13px; font-weight: 700; line-height: 1.3; color: #fff; text-shadow: 0 1px 4px rgba(0,0,0,0.8); }
        .card-stats { font-size: 11px; color: #ddd; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }

        /* Floating Add Button */
        .fab { position: fixed; bottom: 20px; right: 20px; width: 56px; height: 56px; background: #00B4D8; color: #fff; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 28px; font-weight: bold; box-shadow: 0 4px 15px rgba(0,180,216,0.4); border: none; cursor: pointer; z-index: 90; }

        /* Modals */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); justify-content: center; align-items: center; z-index: 100; }
        .modal-content { background: #fff; width: 92%; max-width: 360px; max-height: 90vh; overflow-y: auto; border-radius: 20px; padding: 18px; text-align: left; }
        
        video.player { width: 100%; height: 200px; background: #000; border-radius: 12px; margin: 10px 0 5px 0; object-fit: contain; }

        /* Actions */
        .action-bar { display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #eee; border-bottom: 1px solid #eee; margin: 10px 0; }
        .action-btn { background: none; border: none; font-size: 12px; font-weight: bold; color: #555; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; }
        .action-btn.active { color: #ff4b4b; }
        .action-btn.saved { color: #00B4D8; }

        /* Comments */
        .comments-section { margin-top: 10px; }
        .comments-title { font-size: 13px; font-weight: 800; margin-bottom: 8px; color: #333; }
        .comments-list { max-height: 110px; overflow-y: auto; font-size: 12px; margin-bottom: 8px; display: flex; flex-direction: column; gap: 6px; }
        .comment-item { background: #f1f3f5; padding: 6px 10px; border-radius: 8px; line-height: 1.2; }
        .comment-user { font-weight: bold; color: #00B4D8; margin-right: 4px; }

        .comment-input-box { display: flex; gap: 6px; }
        .comment-input-box input { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 8px; font-size: 12px; }
        .comment-input-box button { background: #00B4D8; color: #fff; border: none; padding: 8px 12px; border-radius: 8px; font-weight: bold; cursor: pointer; }

        input, textarea { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; }
        .btn-main { background: #00B4D8; color: #fff; border: none; padding: 12px; border-radius: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 10px; }
        .btn-close { background: #eee; color: #333; border: none; padding: 10px; border-radius: 10px; font-weight: bold; width: 100%; margin-top: 12px; cursor: pointer; }
    </style>
</head>
<body>

    <header>
        <div class="header-left">
            <div class="logo" onclick="location.reload()">BK</div>
            <div class="nav-links">
                <button class="nav-tab" onclick="openProfileModal()">👤 Perfil</button>
                <button class="nav-tab" onclick="openSubsModal()">🔔 Suscripciones</button>
            </div>
        </div>
        <button class="search-btn" onclick="toggleSearchBar()">🔍</button>
    </header>

    <div class="search-container" id="searchBar">
        <input type="text" id="searchInput" placeholder="Buscar en BK..." oninput="filterVideos()">
        <button class="mic-btn" id="micBtn" onclick="startVoiceSearch()">🎙️</button>
    </div>

    <div class="section-title">videos -</div>
    <div class="carousel" id="videoCarousel"></div>

    <div class="section-title">Lives -</div>
    <div class="carousel" id="liveCarousel"></div>

    <button class="fab" onclick="openUploadModal()">+</button>

    <!-- Modal Perfil Actualizado -->
    <div id="profileModal" class="modal">
        <div class="modal-content" style="text-align: center;">
            <div style="margin-bottom: 10px;">
                <img id="profileAvatar" src="" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; display: none; margin: 0 auto 8px auto; border: 2px solid #00B4D8;" alt="Avatar">
                <div id="profileAvatarEmoji" style="font-size: 50px; margin-bottom: 5px;">👤</div>
            </div>
            <h3 id="displayUsername" style="font-size: 16px;">@usuario_activo</h3>
            <p id="displayBio" style="color: #666; font-size: 12px; margin: 4px 0 12px 0;">Creador de contenido y amante del streaming en vivo.</p>
            
            <hr style="border: 0; border-top: 1px solid #eee; margin: 12px 0;">
            
            <div style="text-align: left; font-size: 12px; font-weight: bold; color: #444; margin-bottom: 4px;">Editar Perfil:</div>
            <input type="text" id="inputUsername" placeholder="Nuevo @usuario" value="@usuario_activo">
            <textarea id="inputBio" placeholder="Escribe tu nueva descripción..." rows="2" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 8px; font-size: 13px; resize: none;">Creador de contenido y amante del streaming en vivo.</textarea>
            
            <div style="text-align: left; font-size: 11px; color: #666; margin-top: 6px;">Foto de perfil:</div>
            <input type="file" id="inputAvatarFile" accept="image/*" style="font-size: 12px; padding: 4px;">

            <button class="btn-main" onclick="saveProfile()">Guardar Cambios</button>
            <button class="btn-close" onclick="closeProfileModal()">Cerrar</button>
        </div>
    </div>

    <!-- Modal Suscripciones -->
    <div id="subsModal" class="modal">
        <div class="modal-content">
            <h3>Suscripciones 🔔</h3>
            <p style="color: #666; font-size: 13px; margin: 8px 0;">Canales que sigues:</p>
            <div style="background: #f1f3f5; padding: 10px; border-radius: 8px; margin: 6px 0; font-size: 13px; font-weight: bold;">@oficial_bk (Activo)</div>
            <div style="background: #f1f3f5; padding: 10px; border-radius: 8px; margin: 6px 0; font-size: 13px; font-weight: bold;">@dj_space (En vivo 🔴)</div>
            <button class="btn-close" onclick="closeSubsModal()">Cerrar</button>
        </div>
    </div>

    <!-- Modal Reproductor -->
    <div id="playerModal" class="modal">
        <div class="modal-content">
            <h3 id="mTitle" style="font-size: 16px;">Título</h3>
            <p id="mAuthor" style="color: #666; font-size: 12px; margin-top: 2px;"></p>
            
            <video id="vPlayer" class="player" controls autoplay playsinline>
                <source id="vSource" src="" type="video/mp4">
            </video>

            <div class="action-bar">
                <button class="action-btn" id="likeBtn" onclick="toggleLike()">
                    <span id="likeIcon">🤍</span> <span id="likeCount">0</span>
                </button>
                <button class="action-btn" onclick="focusComment()">💬 Comentar</button>
                <button class="action-btn" onclick="shareVideo()">🔗 Compartir</button>
                <button class="action-btn" id="saveBtn" onclick="toggleSave()"><span id="saveIcon">🔖</span> Guardar</button>
            </div>

            <div class="comments-section">
                <div class="comments-title">Comentarios</div>
                <div class="comments-list" id="commentsList"></div>
                <div class="comment-input-box">
                    <input type="text" id="cInput" placeholder="Escribe un comentario...">
                    <button onclick="addComment()">Enviar</button>
                </div>
            </div>

            <button class="btn-close" onclick="closePlayer()">Cerrar</button>
        </div>
    </div>

    <!-- Modal Subir Video -->
    <div id="uploadModal" class="modal">
        <div class="modal-content">
            <h3>Subir a BK 🎬</h3>
            <input type="text" id="vInputTitle" placeholder="Título del video">
            <input type="text" id="vInputAuthor" placeholder="Tu @usuario">
            <input type="file" id="vInputFile" accept="video/*">
            <input type="text" id="vInputUrl" placeholder="O pega link MP4 https://...">
            
            <button class="btn-main" onclick="addVideo()">Publicar Ahora</button>
            <button class="btn-close" onclick="closeUploadModal()">Cancelar</button>
        </div>
    </div>

    <script>
        let videosData = [
            { id: 1, title: 'Lanzamiento oficial de BK 🚀', author: '@oficial_bk', url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', views: '12.4k vistas', likes: 124, isLiked: false, isSaved: false, comments: ['@oficial_bk: ¡Bienvenidos a todos!'] },
            { id: 2, title: '🔴 DJ Set Space en vivo', author: '@dj_space', url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4', views: '2.1k espectando', likes: 89, isLiked: false, isSaved: false, comments: ['@listener: Sonando durísimo 🎧'], isLive: true }
        ];

        let currentVideoId = null;

        function renderFeed(filterText) {
            filterText = filterText || '';
            var vCarousel = document.getElementById('videoCarousel');
            var lCarousel = document.getElementById('liveCarousel');
            vCarousel.innerHTML = '';
            lCarousel.innerHTML = '';

            for (var i = 0; i < videosData.length; i++) {
                var item = videosData[i];
                if (item.title.toLowerCase().indexOf(filterText.toLowerCase()) !== -1) {
                    var card = document.createElement('div');
                    card.className = 'card' + (item.isLive ? ' live' : '');
                    
                    (function(id) {
                        card.onclick = function() { openPlayer(id); };
                    })(item.id);
                    
                    var badgeType = item.isLive ? 'LIVE' : 'VIDEO';
                    var badgeClass = item.isLive ? 'badge live' : 'badge';
                    
                    var mediaElement = '<video class="card-bg" src="' + item.url + '#t=0.1" preload="metadata" muted playsinline></video>';

                    card.innerHTML = 
                        mediaElement +
                        '<div class="card-content"><span class="' + badgeClass + '">' + badgeType + '</span></div>' +
                        '<div class="card-content">' +
                            '<div class="card-title">' + item.title + '</div>' +
                            '<div class="card-stats">' + item.views + '</div>' +
                        '</div>';

                    if (item.isLive) {
                        lCarousel.appendChild(card);
                    } else {
                        vCarousel.appendChild(card);
                    }
                }
            }
        }

        function openPlayer(id) {
            currentVideoId = id;
            var item = getItemById(id);
            if(!item) return;

            document.getElementById('mTitle').innerText = item.title;
            document.getElementById('mAuthor').innerText = item.author;
            
            var player = document.getElementById('vPlayer');
            document.getElementById('vSource').src = item.url;
            player.load();

            document.getElementById('likeCount').innerText = item.likes;
            document.getElementById('likeIcon').innerText = item.isLiked ? '❤️' : '🤍';
            document.getElementById('likeBtn').className = 'action-btn' + (item.isLiked ? ' active' : '');
            document.getElementById('saveBtn').className = 'action-btn' + (item.isSaved ? ' saved' : '');

            renderComments();
            document.getElementById('playerModal').style.display = 'flex';
        }

        function closePlayer() {
            document.getElementById('vPlayer').pause();
            document.getElementById('playerModal').style.display = 'none';
        }

        function toggleLike() {
            var item = getItemById(currentVideoId);
            if (!item) return;
            item.isLiked = !item.isLiked;
            item.likes += item.isLiked ? 1 : -1;
            
            document.getElementById('likeCount').innerText = item.likes;
            document.getElementById('likeIcon').innerText = item.isLiked ? '❤️' : '🤍';
            document.getElementById('likeBtn').className = 'action-btn' + (item.isLiked ? ' active' : '');
        }

        function toggleSave() {
            var item = getItemById(currentVideoId);
            if (!item) return;
            item.isSaved = !item.isSaved;
            document.getElementById('saveBtn').className = 'action-btn' + (item.isSaved ? ' saved' : '');
        }

        function renderComments() {
            var item = getItemById(currentVideoId);
            if (!item) return;
            var cList = document.getElementById('commentsList');
            cList.innerHTML = '';
            
            for (var i = 0; i < item.comments.length; i++) {
                var c = item.comments[i];
                var parts = c.split(': ');
                var div = document.createElement('div');
                div.className = 'comment-item';
                div.innerHTML = '<span class="comment-user">' + parts[0] + '</span> ' + (parts[1] || '');
                cList.appendChild(div);
            }
            cList.scrollTop = cList.scrollHeight;
        }

        function addComment() {
            var input = document.getElementById('cInput');
            if (input.value.trim() !== "") {
                var item = getItemById(currentVideoId);
                if (item) {
                    item.comments.push('@tú: ' + input.value);
                    input.value = '';
                    renderComments();
                }
            }
        }

        function getItemById(id) {
            for (var i = 0; i < videosData.length; i++) {
                if (videosData[i].id === id) return videosData[i];
            }
            return null;
        }

        function toggleSearchBar() {
            var bar = document.getElementById('searchBar');
            bar.style.display = bar.style.display === 'flex' ? 'none' : 'flex';
        }

        function filterVideos() {
            var text = document.getElementById('searchInput').value;
            renderFeed(text);
        }

        function startVoiceSearch() {
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert("Tu navegador no soporta búsqueda por voz.");
                return;
            }
            
            var recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            var micBtn = document.getElementById('micBtn');

            recognition.onstart = function() { micBtn.classList.add('recording'); };
            recognition.onend = function() { micBtn.classList.remove('recording'); };
            
            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript;
                document.getElementById('searchInput').value = transcript;
                filterVideos();
            };

            recognition.start();
        }

        function shareVideo() { alert("¡Enlace copiado!"); }
        function focusComment() { document.getElementById('cInput').focus(); }
        
        /* Funciones de Modales Perfil y Suscripciones */
        function openProfileModal() { document.getElementById('profileModal').style.display = 'flex'; }
        function closeProfileModal() { document.getElementById('profileModal').style.display = 'none'; }
        
        function saveProfile() {
            var newU = document.getElementById('inputUsername').value;
            var newB = document.getElementById('inputBio').value;
            var fileInput = document.getElementById('inputAvatarFile');

            if(newU.trim() !== "") {
                document.getElementById('displayUsername').innerText = newU;
            }
            if(newB.trim() !== "") {
                document.getElementById('displayBio').innerText = newB;
            }

            if(fileInput.files && fileInput.files[0]) {
                var imageUrl = URL.createObjectURL(fileInput.files[0]);
                var avatarImg = document.getElementById('profileAvatar');
                avatarImg.src = imageUrl;
                avatarImg.style.display = 'block';
                document.getElementById('profileAvatarEmoji').style.display = 'none';
            }

            alert("¡Perfil actualizado con éxito!");
            closeProfileModal();
        }

        function openSubsModal() { document.getElementById('subsModal').style.display = 'flex'; }
        function closeSubsModal() { document.getElementById('subsModal').style.display = 'none'; }

        function openUploadModal() { document.getElementById('uploadModal').style.display = 'flex'; }
        function closeUploadModal() { document.getElementById('uploadModal').style.display = 'none'; }

        function addVideo() {
            var titleVal = document.getElementById('vInputTitle').value || "Video Nuevo";
            var authorVal = document.getElementById('vInputAuthor').value || "@usuario";
            var fileInput = document.getElementById('vInputFile');
            var urlInput = document.getElementById('vInputUrl').value;
            
            var videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4";

            if (fileInput.files && fileInput.files[0]) {
                videoUrl = URL.createObjectURL(fileInput.files[0]);
            } else if (urlInput.trim() !== "") {
                videoUrl = urlInput;
            }

            var newId = Date.now();
            videosData.unshift({
                id: newId,
                title: titleVal,
                author: authorVal,
                url: videoUrl,
                views: '1 vista • Reciente',
                likes: 0,
                isLiked: false,
                isSaved: false,
                comments: []
            });

            renderFeed();
            closeUploadModal();
            openPlayer(newId);
        }

        renderFeed();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_CODE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
