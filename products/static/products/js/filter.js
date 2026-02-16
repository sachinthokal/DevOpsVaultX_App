document.addEventListener("DOMContentLoaded", function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.p-card');
    const noDataMsg = document.getElementById('js-no-data');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Active Tab UI switch
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filterValue = button.getAttribute('data-filter').toLowerCase();
            let visibleCount = 0;

            // Filter Logic
            productCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category').toLowerCase();
                
                if (filterValue === 'all' || filterValue === cardCategory) {
                    card.style.display = 'flex'; // Important: Keep flex for card layout
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Handle "No Data" visibility
            if (noDataMsg) {
                noDataMsg.style.display = (visibleCount === 0) ? 'block' : 'none';
            }
        });
    });
});