document.addEventListener("DOMContentLoaded", function() {
    const params = new URLSearchParams(window.location.search);
    
    // 1. Django user state check (True/False)
    const isUserLoggedIn = "{{ user.is_authenticated|yesno:'true,false' }}" === "true";

    // 2. Jar URL madhe trigger asel tar checking suru kara
    if (params.get('login_trigger') === 'true') {
        
        if (!isUserLoggedIn) {
            // CASE: User login nahiye -> Popup dakhva
            if (typeof openModal === 'function') {
                openModal('loginModal');
            } else {
                const modal = document.getElementById('loginModal');
                if (modal) modal.style.display = 'flex';
            }

        } 
        else {
            // CASE: User login zala aahe (Redirect houn aala aahe)
            
            // Aadhi URL clean kara (login_trigger kadhun taka)
            const cleanUrl = window.location.origin + window.location.pathname;
            window.history.replaceState({}, document.title, cleanUrl);
            
            // Direct payment page var pathva (Karan user ata login aahe)
            const productId = "{{ product.id }}";
            if (productId) {
                // Thoda delay dila aahe jyamule UI glitch yenar nahi
                setTimeout(() => {
                    window.location.href = `/payments/buy/${productId}/`;
                }, 500);
            }
        }
    }
});