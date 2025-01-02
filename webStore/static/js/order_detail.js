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
});