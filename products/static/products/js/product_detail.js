document.addEventListener("DOMContentLoaded", function() {
    const params = new URLSearchParams(window.location.search);
    
    // 1. Django user state check
    const isUserLoggedIn = "{{ user.is_authenticated|yesno:'true,false' }}" === "true";

    // 2. Jar URL madhe trigger asel tar checking suru kara
    if (params.get('login_trigger') === 'true') {
        
        /* --- FIX START: URL lagech clean kara jyamule history entry junk honar nahi --- */
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState(null, document.title, cleanUrl);
        /* --- FIX END --- */

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
            // Ata URL clean karnyachi garaj nahi karon aapan varti-ch 'replaceState' kela aahe
            
            const productId = "{{ product.id }}";
            if (productId) {
                // User login aahe tar direct payment var pathva
                setTimeout(() => {
                    window.location.href = `/payments/buy/${productId}/`;
                }, 300); // 300ms is enough
            }
        }
    }
});