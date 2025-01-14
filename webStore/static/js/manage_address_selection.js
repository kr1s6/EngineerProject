document.addEventListener('DOMContentLoaded', function () {
    const addressCards = document.querySelectorAll('.address-card');
    const form = document.getElementById('address-form');

    addressCards.forEach(card => {
        card.addEventListener('click', () => {
            addressCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
        });
    });

    form.addEventListener('submit', function (event) {
        const selectedAddress = document.querySelector('input[name="selected_address"]:checked');
        if (!selectedAddress) {
            event.preventDefault();
            alert('Proszę wybrać adres dostawy.');
        }
    });
});
