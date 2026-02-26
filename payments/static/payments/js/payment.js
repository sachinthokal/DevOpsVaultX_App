document.addEventListener("DOMContentLoaded", function () {
  const dataElement = document.getElementById("payment-data");
  if (!dataElement) return;
  const config = JSON.parse(dataElement.textContent);

  let customerName = "";
  let customerEmail = "";

  function submitPaymentData(p_id, o_id, s_id) {
    // SUCCESS: Cleanup localStorage
    localStorage.removeItem("awaitingOTP");
    localStorage.removeItem("customerEmail");
    localStorage.removeItem("customerName");

    Swal.fire({
      title: "FINALIZING ACCESS...",
      html: `<div class="spinner-border text-primary" role="status"></div><p style="margin-top:15px;">SETTING UP YOUR PRIVATE VAULT...</p>`,
      background: "#1e293b",
      color: "#ffffff",
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
    payButton.addEventListener(
      "click",
      async function (e, isAutoTrigger = false) {
        if (e) e.preventDefault();

        // Check if this is an auto-resume from localStorage
        const savedEmail = localStorage.getItem("customerEmail");
        const savedName = localStorage.getItem("customerName");

        if (isAutoTrigger && savedEmail && savedName) {
          customerName = savedName;
          customerEmail = savedEmail;
        } else {
          // Step 1: CONFIRM DETAILS WITH NEW UI
          const { value: formValues } = await Swal.fire({
            title:
              '<span style="font-size: 18px; letter-spacing: 2px;">IDENTIFICATION REQUIRED</span>',
            background: "#1e293b",
            color: "#ffffff",
            padding: "2em",
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
                          placeholder="John Doe" value="${customerName}">
                  </div>
                  
                  <div style="margin-bottom: 10px; position: relative;">
                      <i class="fas fa-envelope" style="position: absolute; top: 42px; left: 15px; color: #bf03ed; font-size: 14px;"></i>
                      <label style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase;">Email Address</label>
                      <input id="swal-input-email" type="email" class="swal2-input" 
                          style="width: 100%; height: 50px; margin: 8px 0 0 0; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; padding: 10px 10px 10px 45px; font-size: 15px; transition: 0.3s;" 
                          placeholder="john@example.com" value="${customerEmail}">
                  </div>
                  <p style="text-align: center; color: #94a3b8; font-size: 11px; margin-top: 20px;">
                      <i class="fas fa-shield-alt" style="margin-right: 5px;"></i> Secured by DevOpsVaultX Encryption
                  </p>
              </div>
          `,
            preConfirm: () => {
              const name = document
                .getElementById("swal-input-name")
                .value.trim();
              const email = document
                .getElementById("swal-input-email")
                .value.trim();
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
        }

        // Step 2: Sending OTP
        // Only show "AUTHENTICATING" if not an auto-trigger to avoid double loading
        if (!isAutoTrigger) {
          Swal.fire({
            title: "AUTHENTICATING...",
            background: "#1e293b",
            color: "#ffffff",
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

            // SAVE STATE
            localStorage.setItem("awaitingOTP", "true");
            localStorage.setItem("customerEmail", customerEmail);
            localStorage.setItem("customerName", customerName);
          } catch (error) {
            Swal.fire({
              title: "SYSTEM ERROR",
              text: error.message,
              icon: "error",
              background: "#1e293b",
              color: "#ffffff",
            });
            return;
          }
        }

        // Step 3: OTP Verification UI (FIXED RESEND)
        const { value: otp } = await Swal.fire({
          title: "VERIFY OTP",
          html: `
            <p style="color: #94a3b8; font-size: 14px;">Sent to ${customerEmail}</p>
            <div id="otp-timer-container" style="font-size: 12px; margin-top: 10px; color: #64748b;">
                Resend OTP in <span id="resend-timer">30</span>s
            </div>
            <div style="margin-top: 15px;">
                <button id="resend-btn" type="button" style="display: none; background: transparent; border: 1px solid #bf03ed; color: #bf03ed; padding: 5px 15px; border-radius: 8px; font-size: 12px; font-weight: bold; cursor: pointer; transition: 0.3s;">RESEND OTP</button>
            </div>
          `,
          background: "#1e293b",
          color: "#ffffff",
          input: "text",
          allowOutsideClick: false,
          inputAttributes: {
            maxlength: 6,
            autofocus: "autofocus",
            style:
              "text-align: center; letter-spacing: 15px; font-size: 24px; font-weight: 900; background: #0f172a; color: #bf03ed; border: 1px solid rgba(191, 3, 237, 0.5); border-radius: 12px;",
          },
          confirmButtonText: "VALIDATE",
          confirmButtonColor: "#bf03ed",
          showCancelButton: true,
          didOpen: () => {
            const timerSpan = document.getElementById("resend-timer");
            const resendBtn = document.getElementById("resend-btn");
            const timerContainer = document.getElementById(
              "otp-timer-container",
            );

            let timeLeft = 30;

            const startCountdown = () => {
              const countdown = setInterval(() => {
                timeLeft--;
                if (timerSpan) timerSpan.innerText = timeLeft;

                if (timeLeft <= 0) {
                  clearInterval(countdown);
                  if (timerContainer) timerContainer.style.display = "none";
                  if (resendBtn) resendBtn.style.display = "inline-block";
                }
              }, 1000);
            };

            startCountdown();

            // Resend Click Event
            resendBtn.addEventListener("click", async () => {
              resendBtn.style.display = "none";
              timerContainer.style.display = "block";
              timeLeft = 30;
              if (timerSpan) timerSpan.innerText = timeLeft;

              startCountdown(); // Restart timer

              try {
                const res = await fetch("/payments/send-otp/", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": config.csrfToken,
                  },
                  body: JSON.stringify({ email: customerEmail }),
                });
                const resData = await res.json();
                if (resData.status === "success") {
                  Swal.showValidationMessage("New OTP Sent!");
                  setTimeout(() => Swal.resetValidationMessage(), 2000);
                }
              } catch (err) {
                console.error("Resend error:", err);
              }
            });
          },
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
        } else {
          // If user cancels OTP modal, we should probably clear the flag so it doesn't pop up again
          localStorage.removeItem("awaitingOTP");
        }
      },
    );
  }

  // --- AUTO-RESUME LOGIC ---
  const awaitingOTP = localStorage.getItem("awaitingOTP");
  if (awaitingOTP === "true") {
    setTimeout(() => {
      if (payButton) {
        // Trigger the click event with a special flag
        payButton.dispatchEvent(new CustomEvent("click"));
        // Calling the function directly to bypass step 1
        payButton.click(null, true);
      }
    }, 500);
  }
});
