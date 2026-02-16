document.addEventListener("DOMContentLoaded", function () {
  // 1. Get Data from Bridge
  const dataElement = document.getElementById("payment-data");
  if (!dataElement) return;
  const config = JSON.parse(dataElement.textContent);

  let customerName = "";
  let customerEmail = "";

  function submitPaymentData(p_id, o_id, s_id) {
    Swal.fire({
      title: "Finalizing Access...",
      html: "Setting up your private vault...",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    const form = document.createElement("form");
    form.method = "POST";
    form.action = config.successUrl;

    const fields = {
      razorpay_payment_id: p_id || "FREE_PAYMENT",
      razorpay_order_id: o_id || "FREE_ORDER",
      razorpay_signature: s_id || "FREE_SIGNATURE",
      csrfmiddlewaretoken: config.csrfToken,
      customer_name: customerName,
      email: customerEmail,
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
      e.preventDefault();

      Swal.fire({
        title: "CONFIRM DETAILS 🚀",
        html: `
            <div style="text-align: left; padding: 0 5px;">
                <label for="swal-input-name" style="font-weight: 600; font-size: 13px; color: #475569;">Full Name</label>
                <input id="swal-input-name" class="swal2-input" style="width: 100%; box-sizing: border-box; margin: 5px 0 15px 0;" placeholder="Enter Name">
                
                <label for="swal-input-email" style="font-weight: 600; font-size: 13px; color: #475569; margin-top: 15px; display: block;">Email Address</label>
                <input id="swal-input-email" class="swal2-input" style="width: 100%; box-sizing: border-box; margin: 5px 0;" placeholder="Enter Email">
            </div>
        `,
        confirmButtonText: config.isFree ? "Get Free Access" : "Pay Now",
        confirmButtonColor: "#1e3c72",
        showCancelButton: true,
        preConfirm: () => {
          // IDs synced with HTML above
          const nameField = document.getElementById("swal-input-name");
          const emailField = document.getElementById("swal-input-email");

          if (!nameField || !emailField) return;

          const name = nameField.value.trim();
          const email = emailField.value.trim();

          if (!name || !email || !email.includes("@")) {
            Swal.showValidationMessage(`Please enter a valid name and email`);
            return false;
          }
          return { name: name, email: email };
        },
      }).then((result) => {
        if (result.isConfirmed) {
          customerName = result.value.name;
          customerEmail = result.value.email;

          if (config.isFree) {
            submitPaymentData();
          } else {
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
              prefill: { name: customerName, email: customerEmail },
              theme: { color: "#1e3c72" },
            };
            const razorpay = new Razorpay(options);
            razorpay.open();
          }
        }
      });
    });
  }
});