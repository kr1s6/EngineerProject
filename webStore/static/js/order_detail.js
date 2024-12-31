document.addEventListener('DOMContentLoaded', function () {
    // Pobranie wszystkich formularzy ocen
    const ratingForms = document.querySelectorAll('.rating_form');

    ratingForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(form);
            const productId = form.action.split('/').pop(); // Pobranie ID produktu z URL

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        alert('Dziękujemy za wystawienie oceny!');
                        form.querySelector('[name="value"]').value = '';
                        form.querySelector('[name="comment"]').value = '';
                    }
                })
                .catch(error => console.error('Błąd:', error));
        });
    });

    // Pobranie wszystkich formularzy reakcji
    const reactionForms = document.querySelectorAll('.reaction_form');

    reactionForms.forEach((form) => {
        form.addEventListener("submit", function (event) {
            event.preventDefault(); // Zapobieganie przeładowaniu strony

            const formData = new FormData(form);
            const productId = form.action.split("/").pop(); // Pobranie ID produktu
            const reactionType = formData.get("reaction"); // Pobranie wartości reakcji

            fetch(`/react/${productId}/`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken"), // Token CSRF
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        alert(`Reakcja: ${data.reaction_type}`);
                        // Aktualizacja liczby ulubionych
                        if (data.reaction_type === "like") {
                            form.querySelector(
                                ".like"
                            ).textContent = `👍 Lubię to (${data.favorites_count})`;
                        } else if (data.reaction_type === "dislike") {
                            form.querySelector(".dislike").textContent = `👎 Nie lubię`;
                        }
                    }
                })
                .catch((error) => console.error("Błąd:", error));
        })
    });
});