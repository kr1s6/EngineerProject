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
        var productId = $(this).data('product-id');
        var card = $(this).closest('.card');

        $.ajax({
            url: '/remove-from-cart/' + productId + '/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
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
        var productId = $(this).data('product-id');
        var action = $(this).data('action');
        var button = $(this);
        var quantityInput = button.siblings('.item-quantity');
        var currentQuantity = parseInt(quantityInput.val());


        if (action === 'increase') {
            currentQuantity += 1;
        } else if (action === 'decrease' && currentQuantity > 1) {
            currentQuantity -= 1;
        }
        quantityInput.val(currentQuantity);
        updateTotalPrice(productId, currentQuantity);


        $.ajax({
            url: '/update-cart-item/' + productId + '/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'action': action
            },
            success: function (response) {
                if (response.success) {
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
        quantityInput.val(newQuantity);
        updateTotalPrice(productId, newQuantity);

        $.ajax({
            url: '/update-cart-item/' + productId + '/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'quantity': newQuantity
            },
            success: function (response) {
                if (!response.success) {
                    alert("Błąd: Nie udało się zaktualizować ilości.");
                }
            },
            error: function () {
                alert("Błąd: Wystąpił problem z serwerem.");
            }
        });
    });
    function updateTotalPrice(productId, quantity) {
        var totalPriceElement = $('.item-total-price[data-product-id="' + productId + '"]');
        var unitPrice = parseFloat(totalPriceElement.data('unit-price'));
        var newTotalPrice = (unitPrice * quantity).toFixed(2);
        totalPriceElement.text(newTotalPrice + ' zł');
    }

    // Dodawanie do koszyka
    $('.add-to-cart').click(function (event) {
        event.preventDefault();
        var productId = $(this).data('product-id');
        var quantity = $(this).data('quantity') || 1;
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

function updateTotalAmount() {
    let total = 0;

    $('.item-total-price').each(function () {
        const unitPrice = parseFloat($(this).data('unit-price'));
        const quantity = parseInt($(this).closest('.row').find('.item-quantity').val());
        total += unitPrice * quantity;
    });

    $('.total-amount-box').text(`Całkowita kwota: ${total.toFixed(2)} zł`);
}

// Wywołaj funkcję po każdej zmianie ilości
$(document).on('change', '.item-quantity', updateTotalAmount);
$(document).on('click', '.update-cart-item', updateTotalAmount);

// Wywołanie na załadowanie strony
$(document).ready(updateTotalAmount);

function toggleName(event, counter) {
    const shortName = document.getElementById(`short-name-${counter}`);
    const fullName = document.getElementById(`full-name-${counter}`);
    const button = event.target;

    if (shortName.classList.contains('d-none')) {
        shortName.classList.remove('d-none');
        fullName.classList.add('d-none');
        button.innerText = "Więcej";
    } else {
        shortName.classList.add('d-none');
        fullName.classList.remove('d-none');
        button.innerText = "Mniej";
    }
}