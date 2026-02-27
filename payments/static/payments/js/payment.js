document.addEventListener("DOMContentLoaded", function () {
    const dataElement = document.getElementById("payment-data");
    if (!dataElement) return;
    const config = JSON.parse(dataElement.textContent);

    // Backend sathi data submit karnare function
    function submitPaymentData(p_id, o_id, s_id) {
        Swal.fire({
            title: "FINALIZING ACCESS...",
            html: `<div class="spinner-border text-primary" role="status"></div><p style="margin-top:15px;">SETTING UP YOUR PRIVATE VAULT...</p>`,
            background: "#1e293b",
            color: "#ffffff",
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => Swal.showLoading(),
        });

        const form = document.createElement("form");
        form.method = "POST";
        form.action = config.successUrl;

        const fields = {
            razorpay_payment_id: p_id || "FREE_PAYMENT",
            razorpay_order_id: o_id || "FREE_ORDER",
            razorpay_signature: s_id || "FREE_SIGNATURE",
            csrfmiddlewaretoken: config.csrfToken,
            customer_name: config.customerName || "{{ user.username }}",
            email: config.customerEmail || "{{ user.email }}",
        };

        Object.entries(fields).forEach(([name, value]) => {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = name;
            input.value = value;
            form.appendChild(input);
        });

        document.body.appendChild(form);
        form.submit();
    }

    const payButton = document.getElementById("pay-button");
    if (payButton) {
        payButton.addEventListener("click", function (e) {
            if (e) e.preventDefault();

            // 1. Jar product FREE asel tar direct submit kara
            if (config.isFree) {
                submitPaymentData();
            } 
            // 2. Jar PAID asel tar Razorpay modal open kara
            else {
                const options = {
                    key: config.razorpayKeyId,
                    amount: config.amount,
                    currency: "INR",
                    name: "DevOpsVaultX",
                    description: config.productTitle,
                    order_id: config.razorpayOrderId,
                    handler: function (response) {
                        submitPaymentData(
                            response.razorpay_payment_id,
                            response.razorpay_order_id,
                            response.razorpay_signature
                        );
                    },
                    prefill: { 
                        name: config.customerName, 
                        email: config.customerEmail 
                    },
                    theme: { color: "#bf03ed" },
                };
                const razorpay = new Razorpay(options);
                razorpay.open();
            }
        });
    }
});