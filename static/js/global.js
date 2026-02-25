function openModal(id) {
    document.getElementById(id).style.display = "block";
    document.body.style.overflow = "hidden";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
    document.body.style.overflow = "auto";
}

function toggleDrop(event) {
    event.stopPropagation(); // Stops navbar links from conflicting
    let m = document.getElementById("dropMenu");
    m.style.display = (m.style.display === "block") ? "none" : "block";
}

// Close dropdown when clicking anywhere else on screen
window.onclick = function(event) {
    let m = document.getElementById("dropMenu");
    if (m && !event.target.closest('.profile-nav')) {
        m.style.display = "none";
    }
}