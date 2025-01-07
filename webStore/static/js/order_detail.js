document.addEventListener('DOMContentLoaded', function () {
    const ratingForms = document.querySelectorAll('.rating_form');
    let isCompleted = false; // Flaga oznaczająca, czy zamówienie jest zakończone

    // Obsługa formularzy ocen
    ratingForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(form);

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

    // Funkcja sprawdzająca status zamówienia
    function checkOrderStatus() {
        if (isCompleted) return; // Zatrzymaj sprawdzanie, jeśli zamówienie jest zakończone

        fetch(`/order-status/${orderId}/`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    if (data.status === 'completed') {
                        isCompleted = true; // Oznacz zamówienie jako zakończone
                        console.log('Zamówienie zakończone, zatrzymano sprawdzanie statusu.');
                    }
                    if (data.status !== currentStatus) {
                        currentStatus = data.status;
                        location.reload(); // Przeładuj stronę, gdy status się zmieni
                    }
                }
            })
            .catch(error => console.error('Błąd przy sprawdzaniu statusu zamówienia:', error));
    }

    // Sprawdzaj status zamówienia co 5 sekund
    const statusInterval = setInterval(checkOrderStatus, 5000);

    // Jeśli zamówienie jest już zakończone na początku, zatrzymaj sprawdzanie
    if (currentStatus === 'completed') {
        clearInterval(statusInterval);
        console.log('Zamówienie zakończone na starcie, nie sprawdzam statusu.');
    }
});
