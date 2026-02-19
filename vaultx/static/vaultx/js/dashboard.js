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
    html: `
<div class="vault-modal-container" style="text-align: left; font-family: 'Plus Jakarta Sans', sans-serif; color: #fff; max-width: 400px; margin: 0 auto;">
    
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px;">
        <div style="border-left: 4px solid #38bdf8; padding-left: 15px;">
            <div style="color: #38bdf8; font-size: 10px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px;">
                <i class="fas fa-shield-alt"></i> Access Verified
            </div>
            <div style="font-size: 20px; font-weight: 800; letter-spacing: -0.5px;">VAULT SUMMARY</div>
        </div>
        <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); padding: 5px 10px; border-radius: 6px; color: #38bdf8; font-size: 9px; font-weight: 800;">
            ID: ${orderId.substring(0, 8)}
        </div>
    </div>

    <div style="background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 15px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 35px; height: 35px; background: #38bdf8; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #000; font-weight: 800;">
                ${userName.charAt(0).toUpperCase()}
            </div>
            <div>
                <div style="font-size: 13px; font-weight: 800; color: #fff;">${userName.toUpperCase()}</div>
                <div style="font-size: 11px; color: #64748b; font-weight: 600;">${userEmail}</div>
            </div>
        </div>
    </div>

    <div style="background: #000; border-radius: 12px; padding: 18px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 20px;">
        <div style="font-size: 10px; color: #38bdf8; font-weight: 800; margin-bottom: 15px; border-bottom: 1px solid rgba(56, 189, 248, 0.1); padding-bottom: 8px;">
            <i class="fas fa-database"></i> TRANSACTION LOGS
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 12px; font-family: 'Courier New', monospace; font-size: 11px;">
            <div style="display: flex; justify-content: space-between; color: #94a3b8;">
                <span>PURCHASED:</span>
                <span style="color: #fff;">${purchaseDate}</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #94a3b8;">
                <span>LAST SYNC:</span>
                <span style="color: #fff;">${lastDownload}</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #94a3b8;">
                <span>CYCLES:</span>
                <span style="color: #38bdf8; font-weight: bold;">x${count}</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #94a3b8;">
                <span>STATUS:</span>
                <span style="color: #10b981;">AUTHORIZED</span>
            </div>
        </div>
    </div>

    <div style="margin-bottom: 25px; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 800; margin-bottom: 10px;">
            <span style="color: #94a3b8;">STORAGE CAPACITY</span>
            <span style="color: #fff;">${used} <span style="color: #38bdf8;">/ 5 Units</span></span>
        </div>
        <div style="height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
            <div style="width: ${(used / 5) * 100}%; background: linear-gradient(90deg, #38bdf8, #818cf8); height: 100%; box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);"></div>
        </div>
    </div>

    <button onclick="Swal.close()" style="width: 100%; background: #fff; color: #000; border: none; padding: 15px; border-radius: 12px; font-weight: 800; font-size: 13px; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s;">
        Return to Vault
    </button>
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

document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.django-message');
    messages.forEach(msg => {
        const type = msg.getAttribute('data-type'); // error, success, etc.
        const text = msg.getAttribute('data-text');

        if (type === 'error') {
            Swal.fire({
                title: 'ACCESS DENIED',
                text: text,
                icon: 'error',
                background: '#050811',
                color: '#fff',
                iconColor: '#ff4757',
                showClass: { popup: 'animate__animated animate__shakeX' }, // Error sathi shake effect
                buttonsStyling: false,
                customClass: {
                    confirmButton: 'vault-btn-ack',
                    popup: 'vault-gradient-popup'
                },
                confirmButtonText: 'ACKNOWLEDGE',
                footer: '<span style="color: #ff4757; font-size: 10px; font-weight: 800; letter-spacing: 2px;">SYSTEM SECURITY ALERT</span>'
            });
        } else if (type === 'success') {
            // Success sathi pan dakhvu shakto
            Swal.fire({
                title: 'SUCCESSFUL',
                text: text,
                icon: 'success',
                background: '#050811',
                color: '#fff',
                timer: 3000,
                timerProgressBar: true,
                showConfirmButton: false,
                customClass: { popup: 'vault-gradient-popup' }
            });
        }
    });
});