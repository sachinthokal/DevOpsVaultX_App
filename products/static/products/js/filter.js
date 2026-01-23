document.addEventListener("DOMContentLoaded", function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');
    const noDataMsg = document.getElementById('js-no-data');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 1. Active button color chanage
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // 2. Filttered value
            const filterValue = button.getAttribute('data-filter');

            // 3. Cards show / hide
            productCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');

                if (filterValue === 'all' || filterValue === cardCategory) {
                    card.style.display = 'flex'; // show
                } else {
                    card.style.display = 'none'; // hide
                }
            });

            // 4. "No Data" Message
            const visibleCardsCount = Array.from(productCards).filter(card => card.style.display !== 'none').length;

            if (visibleCardsCount === 0) {
                noDataMsg.style.display = 'block'; // Message show
            } else {
                noDataMsg.style.display = 'none';  // Message hide
            }
        });
    });
});