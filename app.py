
: 18px; font-weight: 800; margin-bottom: 
        /* Actions */
        .action-bar { display: flex; justify-content: space-around; padding: 10px 0; ; border-radius: 8px; font-weight: bold; cursor: pointer; }

        input, textarea { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; }
        .btn-main { background: #00B4D8; color: #fff; border: none; padding: 12px; border-radius: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 10px; }
        .btn-close { background: #eee; color: #333; border: none; padding: 10px; border-radius: 10px; font-weight: bold; width: 100%; margin-top: 12px; cursor: pointer; }
    </style>
</head>
<body>

    <header>
        <div class="header-left">
            <div class="logo" onclick="location.href='/'">BK</div>
            <div class="nav-links">
                <button class="nav-tab" onclick="openProfileModal()">👤 Perfil</button>
                <button class="nav-tab" onclick="openSubsModal()">🔔 Suscripciones</button>
                <a href="/logout" class="nav-tab btn-logout">Salir</a>
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

    <!-- Modal Perfil Privado del Usuario Actual -->
    <div id="profileModal" class="modal">
        <div class="modal-content" style="text-align: center;">
            <div style="font-size: 50px; margin-bottom: 5px;">👤</div>
            <h3 style="font-size: 16px;">@{{ current_user.username }}</h3>
            <p style="color: #666; font-size: 12px; margin: 4px 0 12px 0;">{{ current_user.bio }}</p>
            
            <hr style="border: 0; border-top: 1px solid #eee; margin: 12px 0;">
            
            <form action="/update_profile" method="POST" style="text-align: left;">
                <div style="font-size: 12px; font-weight: bold; color: #444; margin-bottom: 4px;">Editar mi Perfil:</div>
                <input type="text" name="new_username" placeholder="Nuevo @usuario" value="{{ current_user.username }}" required>
                <textarea name="new_bio" placeholder="Escribe tu nueva descripción..." rows="2" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 8px; font-size: 13px; resize: none;">{{ current_user.bio }}</textarea>
                <button type="submit" class="btn-main">Guardar Cambios</button>
            </form>
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