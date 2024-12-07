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
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = this.dataset.productId;

            fetch(`/product-like/${productId}/`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(response => response.json())
                .then(data => {
                    const button = document.getElementById(`like-btn-${productId}`);
                    const icon = button.querySelector('i');
                    if (data.liked) {
                        icon.classList.remove('far', 'fa-heart');
                        icon.classList.add('fas', 'fa-heart');
                        icon.style.color = 'black';
                        button.classList.add('liked')
                    } else {
                        icon.classList.remove('fas', 'fa-heart');
                        icon.classList.add('far', 'fa-heart');
                        icon.style.color = '';
                        button.classList.remove('liked')
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const likedProductIds = JSON.parse(document.getElementById('liked-product-ids').textContent);

    likedProductIds.forEach(productId => {
        const likeButton = document.getElementById(`like-btn-${productId}`);
        if (likeButton) {
            likeButton.classList.add('liked');
        }
    });
});