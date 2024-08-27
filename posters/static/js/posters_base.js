window.addEventListener('scroll', function() {
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight) {
        document.body.classList.add('scrolled');   

    } else {
        document.body.classList.remove('scrolled');
    }
});