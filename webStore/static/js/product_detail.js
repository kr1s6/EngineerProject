
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

    editButtons.forEach(button => {
        button.addEventListener('click', function () {
            const ratingCard = this.closest('.review-card');
            const ratingId = this.dataset.ratingId;
            const productId = document.querySelector('#edit-rating-form').dataset.productId; // Pobieramy productId
            const ratingValue = ratingCard.querySelectorAll('.bi-star-fill').length;
            const ratingComment = ratingCard.querySelector('.review-comment').innerText;

            // Sprawdź, czy formularz edycji już istnieje
            if (ratingCard.querySelector('.edit-rating-form-container')) {
                alert("Formularz edycji jest już otwarty dla tej opinii.");
                return;
            }

            // Tworzenie formularza dynamicznie
            const editFormContainer = document.createElement('div');
            editFormContainer.classList.add('edit-rating-form-container');
            editFormContainer.innerHTML = `
                <form method="post" style="background-color: #f3f3f3; border: none; box-shadow: none;" class="edit-rating-form" data-product-id="${productId}">
                    <input type="hidden" name="rating_id" value="${ratingId}">
                    <div class="form-group">
                        <label for="edit-rating-value-${ratingId}">Ocena:</label>
                        <input type="number" name="value" id="edit-rating-value-${ratingId}" class="form-control" min="1" max="5" required value="${ratingValue}">
                    </div>
                    <div class="form-group">
                        <label for="edit-rating-comment-${ratingId}">Komentarz:</label>
                        <textarea name="comment" id="edit-rating-comment-${ratingId}" class="form-control">${ratingComment}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary btn-sm">Zapisz zmiany</button>
                    <button type="button" class="btn btn-secondary btn-sm cancel-edit-btn">Anuluj</button>
                </form>
            `;

            // Dodaj formularz do aktualnej opinii
            ratingCard.appendChild(editFormContainer);

            // Obsługa wysyłania formularza
            const editForm = editFormContainer.querySelector('.edit-rating-form');
            editForm.addEventListener('submit', function (event) {
                event.preventDefault();
                const formData = new FormData(editForm);

                const ratingId = formData.get('rating_id');
                const productId = editForm.dataset.productId; // Pobieranie productId

                // Sprawdzenie, czy mamy do czynienia z edycją czy nową opinią
                const actionUrl = ratingId
                    ? `/rate/${productId}/${ratingId}/` // Edycja
                    : `/rate/${productId}/`; // Nowa opinia

                fetch(actionUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                    },
                    body: formData,
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message === 'Rating updated' || data.message === 'Rating created') {
                            // Aktualizuj opinię na stronie
                            ratingCard.querySelector('.review-comment').textContent = formData.get('comment');
                            const starsContainer = ratingCard.querySelector('.bi-star-fill').parentElement;
                            starsContainer.innerHTML = ''; // Wyczyszczenie gwiazdek
                            for (let i = 1; i <= 5; i++) {
                                const star = document.createElement('i');
                                if (i <= formData.get('value')) {
                                    star.className = 'bi bi-star-fill text-warning';
                                } else {
                                    star.className = 'bi bi-star text-warning';
                                }
                                starsContainer.appendChild(star);
                            }

                            // Aktualizuj sekcję średniej oceny w tle
                            const ratingSummary = document.getElementById('product-rating-summary');
                            if (ratingSummary) {
                                ratingSummary.innerHTML = `
                                ${[...Array(5)].map((_, i) =>
                                                i < Math.floor(data.average_rate)
                                                    ? '<i class="bi bi-star-fill text-warning"></i>'
                                                    : i < data.average_rate
                                                        ? '<i class="bi bi-star-half text-warning"></i>'
                                                        : '<i class="bi bi-star text-warning"></i>'
                                            ).join('')}
                                <span class="ms-2">${data.average_rate.toFixed(2)}</span>
                                <span id="product-rating-count">(${data.rating_count})</span>
                            `;
                                        }

                            alert('Opinia została zaktualizowana!');
                            editFormContainer.remove(); // Usuń formularz edycji
                        } else {
                            alert('Wystąpił problem: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Błąd:', error);
                        alert('Nie udało się zaktualizować opinii.');
                    });
            });

            // Obsługa anulowania edycji
            const cancelEditButton = editFormContainer.querySelector('.cancel-edit-btn');
            cancelEditButton.addEventListener('click', () => {
                editFormContainer.remove();
            });
        });
    });
});