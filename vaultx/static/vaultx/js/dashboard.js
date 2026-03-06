// ==========================================
// 1. History & Logic Functions (No eval)
// ==========================================

function showHistory(orderId, purchaseDate, lastDownload, used, count, userName, userEmail) {
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
                    <h2 style="font-size: 18px; font-weight: 900; color: #fff; margin: 0;">PURCHASE <span style="color: #bf03ed;">INFO</span></h2>
                    <div style="font-size: 10px; color: #64748b; margin-top: 4px; font-family: monospace;">ID: ${orderId.substring(0, 14).toUpperCase()}</div>
                </div>
                <div style="background: rgba(191, 3, 237, 0.1); border: 1px solid rgba(191, 3, 237, 0.3); color: #bf03ed; padding: 4px 10px; border-radius: 6px; font-size: 9px; font-weight: 900;">VERIFIED</div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 12px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 9px; color: #64748b; font-weight: 700;">PAYMENTS</div>
                    <div style="font-size: 18px; font-weight: 800; color: #fff; margin-top: 5px;">${count} <span style="font-size: 10px; color: #bf03ed;">Times</span></div>
                </div>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 12px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 9px; color: #64748b; font-weight: 700;">STATUS</div>
                    <div style="font-size: 13px; font-weight: 800; color: #10b981; margin-top: 8px;">ACTIVE</div>
                </div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.02); border-radius: 14px; padding: 15px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                    <span style="font-size: 11px; color: #64748b;">OWNER</span>
                    <span style="font-size: 11px; color: #fff; font-weight: 700;">${userName.toUpperCase()}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 11px; color: #64748b;">BOUGHT ON</span>
                    <span style="font-size: 11px; color: #fff; font-weight: 700;">${purchaseDate}</span>
                </div>
            </div>

            <div style="display: flex; gap: 10px;">
                <a href="${receiptUrl}" target="_blank" style="flex: 1.2; background: #bf03ed; color: #fff; padding: 12px; border-radius: 10px; font-size: 11px; font-weight: 800; text-align: center; text-decoration: none;">VIEW BILL</a>
                <button id="swal-close-btn" style="flex: 1; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; font-size: 11px; font-weight: 700; cursor: pointer;">CLOSE</button>
            </div>
        </div>`,
        didOpen: () => {
            // SweetAlert मधल्या बटणला लिसनर लावणे (No onclick)
            document.getElementById('swal-close-btn').addEventListener('click', () => Swal.close());
        }
    });
}

function removeItem(paymentId) {
    Swal.fire({
        title: "REMOVE ASSET?",
        text: "Are you sure you want to delete this from your vault?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#ff4757",
        confirmButtonText: "YES, DELETE",
        background: "#161e2e",
        color: "#fff",
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/vaultx/delete-item/${paymentId}/`, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    const card = document.getElementById(`card-${paymentId}`);
                    card.style.transition = "all 0.5s ease";
                    card.style.transform = "scale(0)";
                    card.style.opacity = "0";
                    setTimeout(() => {
                        card.remove();
                        if (document.querySelectorAll(".asset-card").length === 0) location.reload();
                    }, 500);
                }
            });
        }
    });
}

function handleDownload(productId, token, btnElement) {

    const originalText = btnElement.innerText;
    btnElement.innerText = "WAIT...";
    btnElement.disabled = true;

    fetch(`/vaultx/download/${token}/${productId}/`, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.json())
    .then(data => {

        if (data.status === "success") {

            // actual download trigger
            const link = document.createElement("a");
            link.href = data.download_url;
            link.download = "";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setTimeout(() => {
                window.location.replace("/vaultx/");
            }, 2000);

        } else {

            Swal.fire({
                title: "Error",
                text: data.message,
                icon: "error",
                background: "#050811",
                color: "#fff"
            });

            btnElement.innerText = originalText;
            btnElement.disabled = false;
        }

    })
    .catch(() => {

        btnElement.innerText = originalText;
        btnElement.disabled = false;

    });
}

// ==========================================
// 2. Main Initialization (DOMContentLoaded)
// ==========================================

document.addEventListener("DOMContentLoaded", function () {
    
    // History Buttons
    document.querySelectorAll('.history-trigger').forEach(btn => {
        btn.addEventListener('click', function() {
            const d = this.dataset;
            showHistory(d.orderId, d.purchaseDate, d.lastDownload, d.used, d.count, d.user, d.email);
        });
    });

    // Remove Buttons
    document.querySelectorAll('.remove-trigger').forEach(btn => {
        btn.addEventListener('click', function() {
            removeItem(this.dataset.paymentId);
        });
    });

    // Download Buttons
    document.querySelectorAll('.download-trigger').forEach(btn => {
        btn.addEventListener('click', function() {
            const pId = this.dataset.productId;
            const token = this.dataset.token;
            // console.log("Product:", pId)
            // console.log("Token:", token)
            handleDownload(pId, token, this);
        });
    });

    // Login Modal (जर लागत असेल तर)
    const loginBtn = document.querySelector('.login-modal-trigger');
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            if (typeof openModal === 'function') openModal('loginModal');
        });
    }

    // Back Button Loop Prevention
    history.pushState(null, null, location.href);
    window.onpopstate = function () {
        location.href = "/products/list/"; // Direct string path for CSP safety
    };
});