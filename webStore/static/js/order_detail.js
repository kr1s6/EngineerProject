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

    // change status after each 10 second and reload page
    function checkOrderStatus() {
        fetch(`/order-status/${orderId}/`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status && data.status !== currentStatus) {
                    currentStatus = data.status;
                    location.reload(); // Przeładuj stronę, gdy status się zmieni
                }
            })
            .catch(error => console.error('Błąd przy sprawdzaniu statusu zamówienia:', error));
    }

    // Sprawdzaj status co 5 sekund
    setInterval(checkOrderStatus, 5000);

});