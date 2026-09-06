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
