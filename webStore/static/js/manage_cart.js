$(document).ready(function () {
    // Usuwanie z koszyka
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');
    $('.remove-from-cart').click(function (event) {
        event.preventDefault();
        var productId = $(this).data('product-id'); // Pobieramy ID produktu z atrybutu data-product-id
        var card = $(this).closest('.card'); // Znajdujemy najbliższy element .card, który chcemy usunąć

        $.ajax({
            url: '/remove-from-cart/' + productId + '/', // Zakładając, że URL w Django jest skonfigurowany z odpowiednim `product_id`
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken }, // Dodajemy token CSRF do nagłówka
            success: function (response) {
                if (response.success) {
                    card.remove(); // Usuwamy kartę z koszyka, jeśli operacja się powiodła
                } else {
                    alert("Błąd: Nie udało się usunąć produktu.");
                }
            },
            error: function () {
                alert("Błąd: Wystąpił problem z serwerem.");
            }
        });
    });

    // Aktualizacja ilości produktu (przyciski + i -)

    $('.update-cart-item').click(function (event) {
        event.preventDefault();
        var productId = $(this).data('product-id');
        var action = $(this).data('action');
        var button = $(this);

        $.ajax({
            url: '/update-cart-item/' + productId + '/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'action': action
            },
            success: function (response) {
                if (response.success) {
                    var quantityElement = button.closest('div').find('.item-quantity');
                    quantityElement.val(response.quantity);
                    var totalElement = button.closest('tr').find('.item-total');
                    var price = parseFloat(button.closest('tr').find('td:nth-child(3)').text().replace(' zł', ''));
                    totalElement.text((response.quantity * price).toFixed(2) + ' zł');
                } else {
                    $('#messages').html('<div class="alert alert-danger">Wystąpił błąd. Spróbuj ponownie.</div>');
                }
            },
            error: function (response) {
                $('#messages').html('<div class="alert alert-danger">Wystąpił błąd. Spróbuj ponownie.</div>');
            }
        });
    });
    // Obsługa ręcznej zmiany ilości w polu input
    $('.item-quantity').change(function () {
        var quantityInput = $(this);
        var productId = $(this).data('product-id');
        var newQuantity = Math.max(1, parseInt(quantityInput.val()));
        console.log(newQuantity);
        console.log(productId);
        quantityInput.val(newQuantity); // Zapobiega wpisaniu ilości < 1

        $.ajax({
            url: '/update-cart-item/' + productId + '/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'quantity': newQuantity
            },
            success: function (response) {
                if (response.success) {
                    var price = parseFloat(quantityInput.closest('.row').find('.item-price').data('price'));
                    quantityInput.closest('.row').find('.item-price').text((price * newQuantity).toFixed(2) + ' zł');
                } else {
                    alert("Błąd: Nie udało się zaktualizować ilości.");
                }
            },
            error: function () {
                alert("Błąd: Wystąpił problem z serwerem.");
            }
        });
    });

    // Dodawanie do koszyka
    $('.add-to-cart').click(function (event) {
        event.preventDefault();
        var productId = $(this).data('product-id');
        var quantity = $(this).data('quantity') || 1; // Domyślnie 1, jeśli brak danych
        var button = $(this);

        $.ajax({
            url: '{% url "add_to_cart" 0 %}'.slice(0, -2) + productId + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': '{{ csrf_token }}',
                'quantity': quantity
            },
            success: function (response) {
                if (response.success) {
                    alert("Produkt został dodany do koszyka!");
                    button.text("Dodano").prop('disabled', true);
                } else {
                    alert("Błąd: Nie udało się dodać produktu do koszyka.");
                }
            },
            error: function () {
                alert("Błąd: Wystąpił problem z serwerem.");
            }
        });
    });
});

function toggleName(event, counter) {
    const shortName = document.getElementById(`short-name-${counter}`);
    const fullName = document.getElementById(`full-name-${counter}`);
    const button = event.target;

    if (shortName.classList.contains('d-none')) {
        shortName.classList.remove('d-none');
        fullName.classList.add('d-none');
        button.innerText = "Pokaż więcej";
    } else {
        shortName.classList.add('d-none');
        fullName.classList.remove('d-none');
        button.innerText = "Pokaż mniej";
    }
}