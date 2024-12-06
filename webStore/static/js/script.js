function phoneMask() {
    var num = $(this).val().replace(/\D/g, '');
    if (num.length <= 3) {
        $(this).val(num);
    } else if (num.length <= 6) {
        $(this).val(num.slice(0, 3) + '-' + num.slice(3));
    } else {
        $(this).val(num.slice(0, 3) + '-' + num.slice(3, 6) + '-' + num.slice(6, 9));
    }
}
$('[name="phone_number"]').keyup(phoneMask);


function setMaxDate() {
    const today = new Date().toISOString().split('T')[0];
    const date100YearsAgo = new Date();
    date100YearsAgo.setFullYear(date100YearsAgo.getFullYear() - 100);
    const minDate = date100YearsAgo.toISOString().split('T')[0];
    document.getElementById('id_birthday').setAttribute('max', today);
    document.getElementById('id_birthday').setAttribute('min', minDate);
}
window.onload = setMaxDate;


document.addEventListener('DOMContentLoaded', function () {
    const messagePopUp = document.getElementById('messagePopUp');
    if (messagePopUp) {
        setTimeout(function () {
            messagePopUp.classList.add('fade');
            setTimeout(function () {
                messagePopUp.style.display = 'none';
            }, 2000);
        }, 4000);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;

            fetch(`/product-like/${productId}/`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                this.textContent = data.liked ? 'Unlike' : 'Like';
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

