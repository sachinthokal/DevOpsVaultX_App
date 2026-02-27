// 1. CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 2. Show Alert Popup (Toast)
function showToast(msg) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = 'toast-alert';
    toast.innerHTML = `<i class="fas fa-check-circle"></i> ${msg}`;
    
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = "fadeOutToast 0.5s forwards";
        setTimeout(() => toast.remove(), 500);
    }, 3500);
}

// 3. Toggle Loading Spinner on Buttons
function toggleLoading(btnSelector, isLoading, originalText) {
    const btn = document.querySelector(btnSelector);
    if (!btn) return;

    if (isLoading) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner"></span> Processing...`;
    } else {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Universal function for all forms (Login, Profile, etc.)
function handleFormLoading(formElement) {
    const submitBtn = formElement.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner"></span> Processing...`;
    }
    return true; 
}