import os
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bk_secret_key_123'
socketio = SocketIO(app, cors_allowed_origins="*")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BK App - Realtime</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #000; color: #fff; margin: 0; padding: 15px; }
        .container { max-width: 500px; margin: 0 auto; }
        .card { background: #121212; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        video { width: 100%; border-radius: 8px; }
        .btn { background: #e50914; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; }
        .comments { margin-top: 10px; background: #222; padding: 10px; border-radius: 5px; max-height: 150px; overflow-y: auto; }
        input[type="text"] { width: 70%; padding: 8px; border-radius: 5px; border: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>BK Videos (En Vivo)</h2>
        <div class="card">
            <video controls src="https://www.w3schools.com/html/mov_bbb.mp4"></video>
            <p><button class="btn" onclick="likeVideo()">❤️ <span id="likes">0</span> Likes</button></p>
            <div class="comments" id="commentsBox"></div>
            <br>
            <input type="text" id="commentInput" placeholder="Escribe un comentario...">
            <button class="btn" onclick="sendComment()">Enviar</button>
        </div>
    </div>

    <script>
        const socket = io();

        socket.on('update_likes', function(data) {
            document.getElementById('likes').innerText = data.likes;
        });

        socket.on('new_comment', function(data) {
            const box = document.getElementById('commentsBox');
            box.innerHTML += `<p><strong>${data.user}:</strong> ${data.text}</p>`;
            box.scrollTop = box.scrollHeight;
        });

        function likeVideo() {
            socket.emit('add_like');
        }

        function sendComment() {
            const input = document.getElementById('commentInput');
            if (input.value.trim() !== '') {
                socket.emit('add_comment', { text: input.value });
                input.value = '';
            }
        }
    </script>
</body>
</html>
"""

likes_count = 0

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('add_like')
def handle_like():
    global likes_count
    likes_count += 1
    emit('update_likes', {'likes': likes_count}, broadcast=True)

@socketio.on('add_comment')
def handle_comment(data):
    emit('new_comment', {'user': 'Usuario BK', 'text': data['text']}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
