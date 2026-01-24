document.addEventListener("DOMContentLoaded", function () {
    const grid = document.querySelector(".products-grid");
    if (!grid) return;

    const cards = Array.from(grid.querySelectorAll(".product-card"));

    // Sort: NEW products first
    cards.sort((a, b) => {
        return b.dataset.new - a.dataset.new;
    });

    // Re-append in sorted order
    cards.forEach(card => grid.appendChild(card));
});
