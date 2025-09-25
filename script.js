function createHeart() {
    const heart = document.createElement('div');
    heart.className = 'floating-heart';
    heart.style.left = Math.random() * window.innerWidth + 'px';
    document.body.appendChild(heart);
    setTimeout(() => heart.remove(), 10000);
}

setInterval(createHeart, 500);
