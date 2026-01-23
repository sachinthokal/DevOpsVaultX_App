// पॉप-अप उघडणे
document.querySelectorAll('.view-details-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        document.getElementById(`modal-${id}`).style.display = 'flex';
        document.body.style.overflow = 'hidden'; // मागचे स्क्रोलिंग बंद
    });
});

// 'X' वर क्लिक केल्यावर बंद करणे
document.querySelectorAll('.close-modal').forEach(span => {
    span.addEventListener('click', () => {
        const id = span.getAttribute('data-id');
        document.getElementById(`modal-${id}`).style.display = 'none';
        document.body.style.overflow = 'auto';
    });
});

// बाहेर क्लिक केल्यावर बंद करणे
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}