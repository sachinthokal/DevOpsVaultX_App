function openModal(id) {
    // Dropdown menu ughda asel tar to pahile band kar
    let m = document.getElementById("dropMenu");
    if (m) m.style.display = "none";

    // Modal open kar
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "flex"; // "block" ऐवजी "flex" वापरल्याने content center ला राहील
        document.body.style.overflow = "hidden"; // Scroll band
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "none";
        document.body.style.overflow = "auto"; // Scroll suru
    }
}

function toggleDrop(event) {
    event.stopPropagation(); 
    let m = document.getElementById("dropMenu");
    if (m) {
        m.style.display = (m.style.display === "block") ? "none" : "block";
    }
}

// Close dropdown OR modal when clicking outside
window.onclick = function(event) {
    // 1. Dropdown close logic
    let m = document.getElementById("dropMenu");
    if (m && !event.target.closest('.profile-nav')) {
        m.style.display = "none";
    }

    // 2. Modal close logic (jar modal chya baher click kela tar)
    if (event.target.classList.contains('auth-modal')) {
        event.target.style.display = "none";
        document.body.style.overflow = "auto";
    }
}