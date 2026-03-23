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