// Prevent Back Button Loop
history.pushState(null, null, location.href);
window.onpopstate = function () {
  location.href = "{% url 'products:list' %}";
};

function showHistory(
  orderId,
  purchaseDate,
  lastDownload,
  used,
  count,
  userName,
  userEmail,
) {
  const receiptUrl = `/vaultx/receipt/${orderId}/`;

  Swal.fire({
    customClass: { popup: "vault-gradient-popup" },
    color: "#ffffff",
    width: "400px",
    showConfirmButton: false,
    background: "#050811",
    html: `
    <div style="text-align: left; font-family: 'Plus Jakarta Sans', sans-serif; padding: 5px;">
        
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
            <div>
                <h2 style="font-size: 18px; font-weight: 900; color: #fff; margin: 0; letter-spacing: -0.5px;">PURCHASE <span style="color: #bf03ed;">INFO</span></h2>
                <div style="font-size: 10px; color: #64748b; margin-top: 4px; font-family: monospace;">ID: ${orderId.substring(0, 14).toUpperCase()}</div>
            </div>
            <div style="background: rgba(191, 3, 237, 0.1); border: 1px solid rgba(191, 3, 237, 0.3); color: #bf03ed; padding: 4px 10px; border-radius: 6px; font-size: 9px; font-weight: 900; letter-spacing: 1px;">
                VERIFIED
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 12px; border-radius: 12px; text-align: center;">
                <div style="font-size: 9px; color: #64748b; font-weight: 700; text-transform: uppercase;">Payments</div>
                <div style="font-size: 18px; font-weight: 800; color: #fff; margin-top: 5px;">${count} <span style="font-size: 10px; color: #bf03ed;">Times</span></div>
            </div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 12px; border-radius: 12px; text-align: center;">
                <div style="font-size: 9px; color: #64748b; font-weight: 700; text-transform: uppercase;">Status</div>
                <div style="font-size: 13px; font-weight: 800; color: #10b981; margin-top: 8px;">ACTIVE</div>
            </div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.02); border-radius: 14px; padding: 15px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                <span style="font-size: 11px; color: #64748b; font-weight: 600;">OWNER</span>
                <span style="font-size: 11px; color: #fff; font-weight: 700;">${userName.toUpperCase()}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                <span style="font-size: 11px; color: #64748b; font-weight: 600;">BOUGHT ON</span>
                <span style="font-size: 11px; color: #fff; font-weight: 700;">${purchaseDate}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 11px; color: #64748b; font-weight: 600;">LAST USED</span>
                <span style="font-size: 11px; color: #fff; font-weight: 700;">${lastDownload}</span>
            </div>
        </div>

        <div style="display: flex; gap: 10px;">
           <a href="${receiptUrl}" 
            target="_blank"
            style="flex: 1.2; background: #bf03ed; color: #fff; border: none; padding: 12px; border-radius: 10px; font-size: 11px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; box-shadow: 0 4px 15px rgba(191, 3, 237, 0.3);">
                <i class="fas fa-eye"></i> VIEW BILL
            </a>
            
            <button onclick="Swal.close()" 
                    style="flex: 1; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 12px; border-radius: 10px; font-size: 11px; font-weight: 700; cursor: pointer; transition: 0.3s;">
                CLOSE
            </button>
        </div>
    </div>`,
    showClass: { popup: "animate__animated animate__zoomIn animate__faster" },
  });
}

function removeItem(paymentId) {
  Swal.fire({
    title: "REMOVE ASSET?",
    text: "Are you sure you want to delete this from your vault?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#ff4757",
    cancelButtonColor: "#64748b",
    confirmButtonText: "YES, DELETE",
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

            // 1. Card la delete animation dya
            card.style.transition = "all 0.5s ease";
            card.style.transform = "scale(0)";
            card.style.opacity = "0";

            // 2. Animation nantar card DOM madhun purna kadha
            setTimeout(() => {
              card.remove(); // Ha card purna delete karto

              // 3. Jar vault purna rikama zala asel tar reload kara (Empty state dakhvnyasathi)
              const remainingCards = document.querySelectorAll(".asset-card");
              if (remainingCards.length === 0) {
                location.reload();
              }
            }, 500);
          } else {
            Swal.fire("Error", "Could not remove item.", "error");
          }
        })
        .catch(() => {
          Swal.fire("Error", "Server connection failed.", "error");
        });
    }
  });
}

// 3. Download Logic
function handleDownload(productId, paymentId) {
  const btn = document.getElementById(`btn-${paymentId}`);
  const originalText = btn.innerText;
  btn.innerText = "WAIT...";
  btn.disabled = true;

  fetch(`/products/${productId}/download/`, {
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        window.location.href = data.download_url;
        setTimeout(() => location.reload(), 2000);
      } else {
        Swal.fire("Error", data.message, "error");
        btn.innerText = originalText;
        btn.disabled = false;
      }
    })
    .catch(() => {
      btn.innerText = originalText;
      btn.disabled = false;
    });
}

// 4. Django Messages Handler
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".django-message").forEach((msg) => {
    const type = msg.getAttribute("data-type");
    const text = msg.getAttribute("data-text");

    Swal.fire({
      title: type === "error" ? "ACCESS DENIED" : "SUCCESSFUL",
      text: text,
      icon: type === "error" ? "error" : "success",
      background: "#050811",
      color: "#fff",
      timer: type === "success" ? 3000 : null,
      confirmButtonText: "ACKNOWLEDGE",
      customClass: { popup: "vault-gradient-popup" },
    });
  });
});
