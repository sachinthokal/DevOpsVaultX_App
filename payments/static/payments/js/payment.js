document.addEventListener("DOMContentLoaded", function () {
  const dataElement = document.getElementById("payment-data");
  if (!dataElement) return;
  const config = JSON.parse(dataElement.textContent);

  let customerName = "";
  let customerEmail = "";

  function submitPaymentData(p_id, o_id, s_id) {
    Swal.fire({
      title: "FINALIZING ACCESS...",
      html: `<div class="spinner-border text-primary" role="status"></div><p style="margin-top:15px;">SETTING UP YOUR PRIVATE VAULT...</p>`,
      background: '#1e293b',
      color: '#ffffff',
      allowOutsideClick: false,
      showConfirmButton: false,
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
    payButton.addEventListener("click", async function (e) {
      e.preventDefault();

      // Step 1: CONFIRM DETAILS WITH NEW UI
      const { value: formValues } = await Swal.fire({
        title: '<span style="font-size: 18px; letter-spacing: 2px;">IDENTIFICATION REQUIRED</span>',
        background: '#1e293b',
        color: '#ffffff',
        padding: '2em',
        confirmButtonText: "REQUEST OTP",
        confirmButtonColor: "#bf03ed",
        cancelButtonText: "CANCEL",
        cancelButtonColor: "transparent",
        showCancelButton: true,
        focusConfirm: false,
        html: `
            <div style="text-align: left; margin-top: 20px;">
                <div style="margin-bottom: 25px; position: relative;">
                    <i class="fas fa-user" style="position: absolute; top: 42px; left: 15px; color: #bf03ed; font-size: 14px;"></i>
                    <label style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase;">Full Name</label>
                    <input id="swal-input-name" class="swal2-input" 
                        style="width: 100%; height: 50px; margin: 8px 0 0 0; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; padding: 10px 10px 10px 45px; font-size: 15px; transition: 0.3s;" 
                        placeholder="John Doe">
                </div>
                
                <div style="margin-bottom: 10px; position: relative;">
                    <i class="fas fa-envelope" style="position: absolute; top: 42px; left: 15px; color: #bf03ed; font-size: 14px;"></i>
                    <label style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase;">Email Address</label>
                    <input id="swal-input-email" type="email" class="swal2-input" 
                        style="width: 100%; height: 50px; margin: 8px 0 0 0; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; padding: 10px 10px 10px 45px; font-size: 15px; transition: 0.3s;" 
                        placeholder="john@example.com">
                </div>
                <p style="text-align: center; color: #94a3b8; font-size: 11px; margin-top: 20px;">
                    <i class="fas fa-shield-alt" style="margin-right: 5px;"></i> Secured by DevOpsVaultX Encryption
                </p>
            </div>
            <style>
                .swal2-input:focus { border-color: #bf03ed !important; box-shadow: 0 0 0 3px rgba(191, 3, 237, 0.2) !important; }
                .swal2-styled.swal2-confirm { border-radius: 12px !important; font-weight: 800 !important; width: 100% !important; margin: 10px 0 0 0 !important; }
                .swal2-styled.swal2-cancel { font-size: 13px !important; text-decoration: underline !important; width: 100% !important; }
            </style>
        `,
        preConfirm: () => {
          const name = document.getElementById("swal-input-name").value.trim();
          const email = document.getElementById("swal-input-email").value.trim();
          if (!name || !email || !email.includes("@")) {
            Swal.showValidationMessage(`Details missing or invalid`);
            return false;
          }
          return { name, email };
        },
      });

      if (!formValues) return;

      customerName = formValues.name;
      customerEmail = formValues.email;

      // Step 2: Sending OTP
      Swal.fire({
        title: "AUTHENTICATING...",
        background: '#1e293b',
        color: '#ffffff',
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading(),
      });

      try {
        const response = await fetch("/payments/send-otp/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": config.csrfToken,
          },
          body: JSON.stringify({ email: customerEmail }),
        });
        const data = await response.json();

        if (data.status !== "success") throw new Error(data.message);

        // Step 3: OTP Verification UI
        const { value: otp } = await Swal.fire({
          title: "VERIFY OTP",
          html: `<p style="color: #94a3b8; font-size: 14px;">Sent to ${customerEmail}</p>`,
          background: '#1e293b',
          color: '#ffffff',
          input: "text",
          inputAttributes: { maxlength: 6, autofocus: "autofocus", style: "text-align: center; letter-spacing: 15px; font-size: 24px; font-weight: 900; background: #0f172a; color: #bf03ed; border: 1px solid rgba(191, 3, 237, 0.5); border-radius: 12px;" },
          confirmButtonText: "VALIDATE",
          confirmButtonColor: "#bf03ed",
          showCancelButton: true,
          preConfirm: async (enteredOtp) => {
            if (!enteredOtp) {
              Swal.showValidationMessage("Enter 6-digit code");
              return false;
            }
            const verifyRes = await fetch("/payments/verify-otp/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": config.csrfToken,
              },
              body: JSON.stringify({ email: customerEmail, otp: enteredOtp }),
            });
            const verifyData = await verifyRes.json();
            if (verifyData.status !== "success") {
              Swal.showValidationMessage("Access Denied: Invalid OTP");
              return false;
            }
            return true;
          },
        });

        if (otp) {
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
                  response.razorpay_signature,
                );
              },
              prefill: { name: customerName, email: customerEmail },
              theme: { color: "#bf03ed" },
            };
            const razorpay = new Razorpay(options);
            razorpay.open();
          }
        }
      } catch (error) {
        Swal.fire({
            title: "SYSTEM ERROR",
            text: error.message || "Failed to process",
            icon: "error",
            background: '#1e293b',
            color: '#ffffff',
            confirmButtonColor: "#bf03ed"
        });
      }
    });
  }
});