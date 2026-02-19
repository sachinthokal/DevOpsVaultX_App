/* All JavaScript Logic (showHistory, removeItem, handleDownload) remains exactly as provided */
function showHistory(
  orderId,
  purchaseDate,
  lastDownload,
  used,
  count,
  userName,
  userEmail,
) {
  const usagePercent = (used / 5) * 100;
  Swal.fire({
    customClass: { popup: "vault-gradient-popup" },
    color: "#ffffff",
    width: "480px",
    padding: "2rem",
    showConfirmButton: false,
    html: `<div class="vault-modal-container">
                <div style="border-left: 3px solid #38bdf8; padding-left: 15px; margin-bottom: 25px;">
                    <div class="vault-modal-subtitle">HISTORY</div>
                    <div class="vault-modal-title">PURCHASE SUMMARY</div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 12px; background: rgba(255,255,255,0.02); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; justify-content: space-between;"><span>OWNER</span><span>${userName.toUpperCase()}</span></div>
                    <div style="display: flex; justify-content: space-between;"><span>STATUS</span><span>${count > 1 ? "RENEWED" : "ORIGINAL"}</span></div>
                    <div style="display: flex; justify-content: space-between;"><span>CYCLES</span><span style="color:#38bdf8">x${count}</span></div>
                </div>
                <div style="margin: 25px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem;"><span>Usage</span><span>${used} / 5 Units</span></div>
                    <div class="vault-progress-bg" style="height:8px; background:rgba(255,255,255,0.05); border-radius:10px; margin-top:8px;">
                        <div style="width: ${usagePercent}%; background: #38bdf8; height: 100%;"></div>
                    </div>
                </div>
                <button onclick="Swal.close()" class="vault-btn-ack">Close Terminal</button>
            </div>`,
    showClass: { popup: "animate__animated animate__fadeInUp animate__faster" },
  });
}

function removeItem(paymentId) {
  Swal.fire({
    title: "REMOVE?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#ff4757",
    background: "#161e2e",
    color: "#fff",
  }).then((result) => {
    if (result.isConfirmed) {
      fetch(`/vaultx/delete-item/${paymentId}/`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.status === "success") {
            const card = document.getElementById(`card-${paymentId}`);
            card.classList.add("animate__animated", "animate__zoomOut");
            setTimeout(() => {
              location.reload();
            }, 500);
          }
        });
    }
  });
}

function handleDownload(productId, paymentId) {
  const btn = document.getElementById(`btn-${paymentId}`);
  btn.innerHTML = "Wait...";
  btn.disabled = true;
  fetch(`/products/${productId}/download/`, {
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        window.location.href = data.download_url;
        setTimeout(() => {
          location.reload();
        }, 2000);
      } else {
        Swal.fire("Error", data.message, "error");
        btn.innerText = "Download";
        btn.disabled = false;
      }
    })
    .catch(() => {
      btn.disabled = false;
      btn.innerText = "Download";
    });
}

// --- 1. Handle Django Redirect Messages (SweetAlert2) ---
    document.addEventListener('DOMContentLoaded', function() {
        const messages = document.querySelectorAll('.django-message');
        messages.forEach(msg => {
            const type = msg.getAttribute('data-type');
            const text = msg.getAttribute('data-text');

            if (type === 'error' || type === 'danger') {
                Swal.fire({
                    title: 'ACCESS DENIED',
                    text: text,
                    icon: 'error',
                    background: '#050811',
                    color: '#fff',
                    customClass: { popup: 'vault-gradient-popup', confirmButton: 'vault-btn-ack' },
                    showClass: { popup: 'animate__animated animate__shakeX' }
                });
            }
        });
    });