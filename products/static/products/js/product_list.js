document.addEventListener("DOMContentLoaded", function() {
    const grid = document.getElementById('grid');
    const cards = Array.from(grid.getElementsByClassName('asset-card'));
    const btns = document.querySelectorAll('.segment-btn');
    const noData = document.getElementById('no-data');

    // Sort: Newest -> Free -> Others
    cards.sort((a, b) => {
        const aNew = a.querySelector('.new-tag') ? 1 : 0;
        const bNew = b.querySelector('.new-tag') ? 1 : 0;
        if (aNew !== bNew) return bNew - aNew;
        const aP = parseFloat(a.dataset.price);
        const bP = parseFloat(b.dataset.price);
        if (aP === 0 && bP !== 0) return -1;
        if (aP !== 0 && bP === 0) return 1;
        return 0;
    });
    cards.forEach(c => grid.appendChild(c));

    // Filter Logic with No Data show/hide
    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const f = btn.dataset.filter.toLowerCase();
            
            let visibleCount = 0;
            cards.forEach(c => {
                const cat = c.dataset.category.toLowerCase();
                if (f === 'all' || cat === f) {
                    c.style.display = 'flex';
                    visibleCount++;
                } else {
                    c.style.display = 'none';
                }
            });

            // Show "No Data" if visibleCount is 0
            if (visibleCount === 0) {
                noData.style.display = 'flex';
            } else {
                noData.style.display = 'none';
            }
        });
    });
});