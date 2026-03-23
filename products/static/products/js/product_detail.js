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


/* --- DevOpsVaultX Copy to Clipboard Logic --- */
document.addEventListener('DOMContentLoaded', function() {
    // 1. Select all code blocks inside the markdown body
    const codeBlocks = document.querySelectorAll('.markdown-body pre');

    codeBlocks.forEach(function(block) {
        // 2. Create the Copy Button element
        const button = document.createElement('button');
        button.className = 'copy-btn'; // Matches the CSS we added in Step 2
        button.type = 'button';
        button.innerText = 'Copy';

        // 3. Add button to the pre block
        // Pre tag must have 'position: relative' in CSS for this to align
        block.appendChild(button);

        // 4. Click event to handle copying
        button.addEventListener('click', function() {
            const codeElement = block.querySelector('code');
            if (!codeElement) return;

            const textToCopy = codeElement.innerText;

            // Use the Clipboard API
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Success Feedback
                button.innerText = 'Copied!';
                button.classList.add('copied');

                // Reset button text after 2 seconds
                setTimeout(function() {
                    button.innerText = 'Copy';
                    button.classList.remove('copied');
                }, 2000);
            }, function(err) {
                console.error('Failed to copy text: ', err);
                button.innerText = 'Error';
            });
        });
    });
});