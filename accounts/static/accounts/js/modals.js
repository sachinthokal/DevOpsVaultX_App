// ================= SYNCED LOGIC =================

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// ================= GLOBAL SHOWTOAST LOGIC =================

function showToast(msg, type = "info") {
  const container = document.getElementById("toast-container");
  let icon = "fa-info-circle";
  if (type.includes("success")) icon = "fa-check-circle";
  if (type.includes("warning")) icon = "fa-exclamation-triangle";
  if (type.includes("error")) icon = "fa-times-circle";

  const toast = document.createElement("div");
  toast.className = `toast-alert ${type}`;
  toast.innerHTML = `<i class="fas ${icon}"></i> <span>${msg}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "fadeOutToast 0.5s forwards";
    setTimeout(() => toast.remove(), 500);
  }, 6000);
}

// ================= GLOBAL BUTTONS PROCESSING LOGIC =================

function toggleLoading(btnSelector, isLoading, originalText) {
  const btn = document.querySelector(btnSelector);
  if (!btn) return;
  btn.disabled = isLoading;
  btn.innerHTML = isLoading
    ? `<span class="spinner"></span> Processing...`
    : originalText;
}

// ================= GLOBAL FORM LOADING LOGIC =================

function handleFormLoading(formElement) {
  const submitBtn = formElement.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span> Processing...`;
  }
  return true;
}

// ================= GLOBAL FORM OPEN CLOSE SWITCH LOGIC =================

function openModal(id) {
  document.getElementById(id).style.display = "flex";
}
function closeModal(id) {
  document.getElementById(id).style.display = "none";
  if(id === 'registerModal') {
        localStorage.removeItem("otp_pending");
        localStorage.removeItem("otp_email");
    }
}
function switchModal(o, n) {
  closeModal(o);
  setTimeout(() => openModal(n), 300);
}

window.onclick = (e) => {
  if (e.target.classList.contains("auth-modal"))
    e.target.style.display = "none";
};

// ================= SEND OTP & VERIFY OPERATIONS =================
let otpTimer;

function startResendTimer() {
    let timeLeft = 60;
    const timerText = document.getElementById("timer_text");
    const timerCount = document.getElementById("timer_count");
    const resendLink = document.getElementById("resend_link");

    // UI Reset
    resendLink.style.display = "none";
    timerText.style.display = "inline";
    timerCount.innerText = timeLeft;

    clearInterval(otpTimer);
    otpTimer = setInterval(() => {
        timeLeft--;
        timerCount.innerText = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(otpTimer);
            timerText.style.display = "none";
            resendLink.style.display = "inline";
        }
    }, 1000);
}

async function sendOTP(isResend = false) {
    const email = document.getElementById("reg_email").value;
    const username = document.getElementById("reg_un").value;
    const password = document.getElementById("reg_pass").value;
    const fName = document.getElementById("reg_fn").value;
    const lName = document.getElementById("reg_ln").value;

    if (!email || !username || !password) {
        showToast("Required fields missing", "error");
        return;
    }

    // Show Loading by id
    const targetBtn = isResend ? "#resend_link" : "#initBtn";
    const originalText = isResend ? "Resend OTP" : "Get Started";
    
    toggleLoading(targetBtn, true, originalText);

    const formData = new FormData();
    formData.append("email", email);
    formData.append("username", username);
    formData.append("password", password);
    formData.append("first_name", fName);
    formData.append("last_name", lName);

    try {
        const resp = await fetch("/accounts/send-otp/", { 
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: formData,
        });
        
        const data = await resp.json();
        if (data.status === "success") {

            localStorage.setItem("otp_pending", "true");
            localStorage.setItem("otp_email", email); // रिझेंडसाठी इमेल पण सेव्ह करा
            showToast(isResend ? "New OTP Sent!" : "OTP Sent to Email", "success");
            
            // टायमर सुरू करा
            startResendTimer();

            if (!isResend) {
                document.getElementById("reg_details").style.display = "none";
                document.getElementById("otp_details").style.display = "block";
            }
        } else {
            showToast(data.message, "error");
        }
    } catch (e) {
        showToast("Connection error", "error");
    } finally {
        toggleLoading(targetBtn, false, originalText);
    }
}

async function verifyOTP() {
  const btn = "#verifyBtn";
  toggleLoading(btn, true, "Verify Account");

  const formData = new FormData();
  formData.append("otp", document.getElementById("reg_otp").value);

  try {
    const resp = await fetch("/accounts/register/", { 
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      body: formData,
    });

    const data = await resp.json();
    if (data.status === "success") {
      localStorage.removeItem("otp_pending");
      localStorage.removeItem("otp_email");
      showToast("Account verified! Redirecting...", "success");
      setTimeout(() => window.location.reload(), 1500);
    } else {
      showToast(data.message, "error");
      toggleLoading(btn, false, "Verify Account");
    }
  } catch (e) {
    showToast("Verification failed", "error");
    toggleLoading(btn, false, "Verify Account");
  }
}

// ================= ON PAGE REFRESHED CHECK DATA =================
window.onload = function() {
    if (localStorage.getItem("otp_pending") === "true") {
        // If OTP Pending then show OTP Box
        document.getElementById("registerModal").style.display = "flex";
        document.getElementById("reg_details").style.display = "none";
        document.getElementById("otp_details").style.display = "block";
        
        // If Email saved then used resend
        const savedEmail = localStorage.getItem("otp_email");
        if(savedEmail) document.getElementById("reg_email").value = savedEmail;

        startResendTimer(); // Timer Start again
    }
};


// ================= EYE ICON (SHOW/HIDE) & STRENGTH METER =================
function togglePass(id, icon) {
    const el = document.getElementById(id);
    if (el.type === "password") {
        el.type = "text";
        icon.className = "fas fa-eye";
    } else {
        el.type = "password";
        icon.className = "fas fa-eye-slash";
    }
}

function checkStrength(input, name) {
    // फक्त पहिल्या पासवर्ड फील्डला ट्रॅक करण्यासाठी (Confirmation ला नको)
    if (name.includes('confirm')) return;

    const bar = document.getElementById('strength-bar');
    const txt = document.getElementById('strength-text');
    let strength = 0;
    const val = input.value;

    if (val.length >= 8) strength += 25;
    if (val.match(/[A-Z]/)) strength += 25;
    if (val.match(/[0-9]/)) strength += 25;
    if (val.match(/[^A-Za-z0-9]/)) strength += 25;

    bar.style.width = strength + "%";
    
    if (strength <= 25) { bar.style.backgroundColor = "#ef4444"; txt.innerText = "Weak"; }
    else if (strength <= 50) { bar.style.backgroundColor = "#f59e0b"; txt.innerText = "Medium"; }
    else if (strength <= 75) { bar.style.backgroundColor = "#3b82f6"; txt.innerText = "Strong"; }
    else { bar.style.backgroundColor = "#22c55e"; txt.innerText = "Very Secure 🛡️"; }
}

// ==================================
