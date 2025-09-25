document.addEventListener('DOMContentLoaded', () => {
    function createHeart() {
        const heart = document.createElement('div');
        heart.className = 'floating-heart';
        heart.style.left = Math.random() * window.innerWidth + 'px';
        document.body.appendChild(heart);
        setTimeout(() => heart.remove(), 10000);
    }

    // Spawn a new heart every 0.5s
    setInterval(createHeart, 500);
});
