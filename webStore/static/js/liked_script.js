
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
    const likedProductIds = JSON.parse(document.getElementById('liked-product-ids').textContent);

    likedProductIds.forEach(productId => {
        const likeButton = document.getElementById(`like-btn-${productId}`);
        if (likeButton) {
            likeButton.classList.add('liked');
        }
    });
});