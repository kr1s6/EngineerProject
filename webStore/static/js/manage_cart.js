$(document).ready(function () {
    // Usuwanie z koszyka
    $('.remove-from-cart').click(function (event) {
        event.preventDefault();
        var productId = $(this).data('product-id');
        var card = $(this).closest('.card');

        $.ajax({
            url: '{% url "remove_from_cart" 0 %}'.slice(0, -2) + productId + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.success) {
                    card.remove();
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
        var button = $(this);
        var productId = button.data('product-id');
        var action = button.data('action');

        // Pobieranie inputa ilości
        var quantityInput = button.siblings('.item-quantity');
        var currentQuantity = parseInt(quantityInput.val());

        // Aktualizacja ilości na podstawie akcji
        var newQuantity = (action === 'increase') ? currentQuantity + 1 : Math.max(1, currentQuantity - 1);
        quantityInput.val(newQuantity);

        // Wysłanie AJAX
        $.ajax({
            url: '{% url "update_cart_item" 0 %}'.slice(0, -2) + productId + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': '{{ csrf_token }}',
                'quantity': newQuantity
            },
            success: function (response) {
                if (response.success) {
                    // Aktualizacja sumy dla tego produktu
                    var price = parseFloat(button.closest('.row').find('.item-price').data('price'));
                    button.closest('.row').find('.item-price').text((price * newQuantity).toFixed(2) + ' zł');
                } else {
                    alert("Błąd: Nie udało się zaktualizować ilości.");
                }
            },
            error: function () {
                alert("Błąd: Wystąpił problem z serwerem.");
            }
        });
    });

    // Obsługa ręcznej zmiany ilości w polu input
    $('.item-quantity').change(function () {
        var quantityInput = $(this);
        var productId = quantityInput.data('product-id');
        var newQuantity = Math.max(1, parseInt(quantityInput.val()));

        quantityInput.val(newQuantity); // Zapobiega wpisaniu ilości < 1

        $.ajax({
            url: '{% url "update_cart_item" 0 %}'.slice(0, -2) + productId + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': '{{ csrf_token }}',
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