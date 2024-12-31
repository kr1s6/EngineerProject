document.addEventListener("DOMContentLoaded", function () {
    const openModalButton = document.getElementById("open-reviews-modal");
    const closeModalButton = document.getElementById("close-reviews-modal");
    const reviewsModal = document.getElementById("reviews-modal");

    // Open modal
    openModalButton.addEventListener("click", function () {
        reviewsModal.style.display = "flex";
    });

    // Close modal
    closeModalButton.addEventListener("click", function () {
        reviewsModal.style.display = "none";
    });

    // Close modal on outside click
    window.addEventListener("click", function (event) {
        if (event.target === reviewsModal) {
            reviewsModal.style.display = "none";
        }
    });
});