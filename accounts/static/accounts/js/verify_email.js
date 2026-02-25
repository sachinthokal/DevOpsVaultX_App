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

// 4. Send OTP Logic (Combined for Initial & Resend)
async function sendOTP() {
    const registrationStep = document.getElementById('registrationStep');
    const otpStep = document.getElementById('otpStep');
    const resendLink = document.querySelector("#otpStep a");
    
    // Check if it's a Resend request
    const isResend = otpStep.style.display === 'block';
    
    const email = document.getElementById('reg_email').value;
    if (!email) {
        alert("Please enter your email first.");
        return;
    }

    // UI State Management
    if (!isResend) {
        toggleLoading("#registrationStep .auth-btn", true, "Initialize Account");
    } else {
        if(resendLink) resendLink.innerHTML = "Sending...";
    }

    const csrftoken = getCookie('csrftoken');
    const regData = {
        first_name: document.getElementById('reg_fn').value,
        last_name: document.getElementById('reg_ln').value,
        username: document.getElementById('reg_un').value,
        email: email,
        password: document.getElementById('reg_pass').value
    };

    try {
        const response = await fetch('/accounts/send-otp/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': csrftoken 
            },
            body: JSON.stringify(regData)
        });

        const result = await response.json();

        if (result.status === 'success') {
            if (isResend) {
                showToast("OTP Resent Successfully!");
            } else {
                registrationStep.style.display = 'none';
                otpStep.style.display = 'block';
                showToast("OTP sent to your email!");
            }
        } else {
            alert(result.message || "Something went wrong!");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Server error. Please check your connection.");
    } finally {
        if (!isResend) {
            toggleLoading("#registrationStep .auth-btn", false, "Initialize Account");
        } else {
            if(resendLink) resendLink.innerHTML = "Resend";
        }
    }
}

// 5. Verify OTP Logic
async function verifyOTP(event) {
    if(event) event.preventDefault(); // Form reload thambvanya-sathi
    
    const originalText = "Verify & Register";
    const btnSelector = "#otpStep .auth-btn";
    const otpCode = document.getElementById('otp_code').value;

    if (!otpCode || otpCode.length < 6) {
        alert("Please enter a valid 6-digit OTP.");
        return;
    }

    toggleLoading(btnSelector, true, originalText);
    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch('/accounts/verify-otp/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': csrftoken 
            },
            body: JSON.stringify({ otp: otpCode })
        });

        const result = await response.json();

        if (result.status === 'success') {
            showToast("Account Created Successfully!");
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            alert(result.message || "Invalid OTP!");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Verification failed. Try again.");
    } finally {
        toggleLoading(btnSelector, false, originalText);
    }
}

// Event Listener for OTP Form
document.addEventListener('DOMContentLoaded', function() {
    const otpForm = document.getElementById('otpForm');
    if (otpForm) {
        otpForm.addEventListener('submit', verifyOTP);
    }
});