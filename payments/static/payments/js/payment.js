document.addEventListener("DOMContentLoaded", function () {
  // 1. Get Data from Bridge
  const dataElement = document.getElementById("payment-data");
  if (!dataElement) return;
  const config = JSON.parse(dataElement.textContent);

  let customerName = "";
  let customerEmail = "";

  // पेमेंट डेटा सबमिट करण्यासाठी फंक्शन
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
    payButton.addEventListener("click", async function (e) {
      e.preventDefault();

      // पायरी १: नाव आणि ईमेल मिळवणे
      const { value: formValues } = await Swal.fire({
        title: "CONFIRM DETAILS 🚀",
        html: `
            <div style="text-align: left; padding: 0 5px;">
                <label for="swal-input-name" style="font-weight: 600; font-size: 13px; color: #475569;">Full Name</label>
                <input id="swal-input-name" class="swal2-input" style="width: 100%; box-sizing: border-box; margin: 5px 0 15px 0;" placeholder="Enter Name">
                
                <label for="swal-input-email" style="font-weight: 600; font-size: 13px; color: #475569; margin-top: 15px; display: block;">Email Address</label>
                <input id="swal-input-email" class="swal2-input" style="width: 100%; box-sizing: border-box; margin: 5px 0;" placeholder="Enter Email">
            </div>
        `,
        confirmButtonText: "Send OTP",
        confirmButtonColor: "#1e3c72",
        showCancelButton: true,
        preConfirm: () => {
          const name = document.getElementById("swal-input-name").value.trim();
          const email = document.getElementById("swal-input-email").value.trim();
          if (!name || !email || !email.includes("@")) {
            Swal.showValidationMessage(`Please enter a valid name and email`);
            return false;
          }
          return { name, email };
        },
      });

      if (!formValues) return;

      customerName = formValues.name;
      customerEmail = formValues.email;

      // पायरी २: OTP पाठवणे
      Swal.fire({ title: "Sending OTP...", allowOutsideClick: false, didOpen: () => Swal.showLoading() });

      try {
        const response = await fetch("/payments/send-otp/", {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": config.csrfToken },
          body: JSON.stringify({ email: customerEmail }),
        });
        const data = await response.json();

        if (data.status !== "success") throw new Error(data.message);

        // पायरी ३: OTP विचारणे
        const { value: otp } = await Swal.fire({
          title: "Verify Email",
          text: `Enter the OTP sent to ${customerEmail}`,
          input: "text",
          inputAttributes: { maxlength: 6, autofocus: "autofocus" },
          confirmButtonText: "Verify & Proceed",
          showCancelButton: true,
          preConfirm: async (enteredOtp) => {
            if (!enteredOtp) {
                Swal.showValidationMessage("Please enter OTP");
                return false;
            }
            const verifyRes = await fetch("/payments/verify-otp/", {
              method: "POST",
              headers: { "Content-Type": "application/json", "X-CSRFToken": config.csrfToken },
              body: JSON.stringify({ email: customerEmail, otp: enteredOtp }),
            });
            const verifyData = await verifyRes.json();
            if (verifyData.status !== "success") {
              Swal.showValidationMessage("Invalid or Expired OTP");
              return false;
            }
            return true;
          },
        });

        // पायरी ४: व्हेरिफिकेशन यशस्वी झाले तर पेमेंट सुरु करा
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
      } catch (error) {
        Swal.fire("Error", error.message || "Failed to send OTP", "error");
      }
    });
  }
});