document.querySelectorAll('.vault-content').forEach(content => {
    let paused = false;

    function autoScroll() {
        if (!paused) {
            content.scrollTop += 0.5;
            if (content.scrollTop + content.clientHeight >= content.scrollHeight) {
                content.scrollTop = 0;
            }
        }
        requestAnimationFrame(autoScroll);
    }

    if (content.scrollHeight > content.clientHeight) {
        autoScroll();
        content.addEventListener("mouseenter", () => paused = true);
        content.addEventListener("mouseleave", () => paused = false);
    }
});
