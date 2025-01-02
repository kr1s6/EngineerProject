
document.addEventListener('DOMContentLoaded', () => {
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

    //  edit rate
    const editButtons = document.querySelectorAll('.edit-rating-btn');
    const editModal = document.getElementById('edit-rating-modal');
    const editForm = document.getElementById('edit-rating-form');
    const editRatingId = document.getElementById('edit-rating-id');
    const editRatingValue = document.getElementById('edit-rating-value');
    const editRatingComment = document.getElementById('edit-rating-comment');
    const reviewsSection = document.getElementById('modal-reviews-section');

    // Otwieranie modala i wypełnianie danymi
    editButtons.forEach(button => {
        button.addEventListener('click', function () {
            const ratingId = this.dataset.ratingId;
            const ratingValue = this.parentElement.querySelectorAll('.bi-star-fill').length;
            const ratingComment = this.parentElement.querySelector('.review-comment').innerText;

            editRatingId.value = ratingId;
            editRatingValue.value = ratingValue;
            editRatingComment.value = ratingComment;
            editModal.style.display = 'block';
        });
    });

    // Zamknięcie modala po kliknięciu na zewnątrz
    window.addEventListener('click', function (event) {
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
    });

    editForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(editForm);

        fetch(editForm.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.message === 'Rating updated' || data.message === 'Rating submitted') {
                    // Pobieranie zaktualizowanej listy opinii
                    fetch(`/product/${editForm.dataset.productId}/ratings/`)
                        .then(response => response.json())
                        .then(data => {
                            reviewsSection.innerHTML = data.html; // Aktualizuj sekcję z opiniami
                            editModal.style.display = 'none'; // Zamknij modal
                        });
                } else {
                    alert('Wystąpił problem: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Błąd:', error);
                alert('Wystąpił problem z zapisem opinii.');
            });
    });
});