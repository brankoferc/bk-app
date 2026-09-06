import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

VIDEOS = [
    {
        'id': 1,
        'title': 'Video Nuevo',
        'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
        'views': '1 vista • Reciente',
        'type': 'video'
    },
    {
        'id': 2,
        'title': 'Lanzamiento oficial de BK 🚀',
        'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
        'views': '12.4k vistas',
        'type': 'video'
    },
    {
        'id': 3,
        'title': '🔴 DJ Set Space en vivo',
        'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
        'views': '2.1k espectando',
        'type': 'live'
    }
]

HTML_TEMPLATE = """
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
        <div class="border-2 border-black font-extrabold text-xl px-4 py-1 rounded-2xl">BK</div>
        <button class="text-slate-700 text-xl"><i class="fas fa-search"></i></button>
    </div>

    <!-- Sección Videos -->
    <h2 class="text-2xl font-bold mb-3">videos -</h2>
    <div class="grid grid-cols-2 gap-3 mb-6">
        {% for video in videos %}
            {% if video.type == 'video' %}
            <div onclick="playVideo('{{ video.url }}', '{{ video.title }}')" class="video-card card-border-blue">
                <div>
                    <span class="bg-cyan-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-md uppercase">VIDEO</span>
                </div>
                <div>
                    <p class="font-bold text-sm leading-tight mb-1">{{ video.title }}</p>
                    <p class="text-[11px] text-gray-400">{{ video.views }}</p>
                </div>
            </div>
            {% endif %}
        {% endfor %}
    </div>

    <!-- Sección Lives -->
    <h2 class="text-2xl font-bold mb-3">Lives -</h2>
    <div class="grid grid-cols-2 gap-3">
        {% for video in videos %}
            {% if video.type == 'live' %}
            <div onclick="playVideo('{{ video.url }}', '{{ video.title }}')" class="video-card card-border-red">
                <div>
                    <span class="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-md uppercase flex items-center gap-1 w-max">
                        <span class="w-1.5 h-1.5 bg-white rounded-full animate-ping"></span> LIVE
                    </span>
                </div>
                <div>
                    <p class="font-bold text-sm leading-tight mb-1">🔴 {{ video.title }}</p>
                    <p class="text-[11px] text-gray-400">{{ video.views }}</p>
                </div>
            </div>
            {% endif %}
        {% endfor %}
    </div>

    <!-- Botón flotante para subir video -->
    <button onclick="toggleModal('uploadModal')" class="fixed bottom-6 right-6 w-14 h-14 bg-cyan-400 rounded-full flex items-center justify-center text-white text-2xl shadow-lg font-bold">
        +
    </button>

    <!-- Modal Reproductor de Video -->
    <div id="playerModal" class="fixed inset-0 bg-black/90 hidden z-50 flex-col justify-center items-center p-4">
        <button onclick="closePlayer()" class="absolute top-5 right-5 text-white text-2xl"><i class="fas fa-times"></i></button>
        <h3 id="videoTitle" class="text-white font-bold mb-4 text-center"></h3>
        <video id="videoPlayer" class="w-full max-w-md rounded-xl" controls autoplay></video>
    </div>

    <!-- Modal Subir Video -->
    <div id="uploadModal" class="fixed inset-0 bg-black/50 hidden z-50 flex justify-center items-center p-4">
        <div class="bg-white p-6 rounded-2xl w-full max-w-sm">
            <h3 class="font-bold text-lg mb-4">Añadir Nuevo Video</h3>
            <form action="/add" method="POST" class="flex flex-col gap-3">
                <input type="text" name="title" placeholder="Título del video" class="border p-2 rounded-lg text-sm" required>
                <input type="url" name="url" placeholder="URL del video (.mp4)" class="border p-2 rounded-lg text-sm" required>
                <select name="type" class="border p-2 rounded-lg text-sm">
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

        function playVideo(url, title) {
            document.getElementById('videoTitle').innerText = title;
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

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, videos=VIDEOS)

@app.route("/add", methods=['POST'])
def add_video():
    title = request.form.get('title')
    url = request.form.get('url')
    vtype = request.form.get('type')
    if title and url:
        VIDEOS.append({
            'id': len(VIDEOS) + 1,
            'title': title,
            'url': url,
            'views': '1 vista • Reciente' if vtype == 'video' else '1 espectando',
            'type': vtype
        })
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000