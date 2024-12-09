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

document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('categories-toggle');
    const categoriesContainer = document.getElementById('header_categories');
    const categoryItems = document.querySelectorAll('.category-item');
    const subcategoryDisplay = document.querySelector('.subcategory-display');
    let selectedIndex = 0; // Index of the currently selected category

     // Funkcja do aktualizacji wyświetlania podkategorii
    const updateSubcategories = (subcategories) => {
        subcategoryDisplay.innerHTML = ''; // Czyścimy poprzednie podkategorie

        subcategories.forEach(subcategory => {
            const li = document.createElement('li');
            li.classList.add('list-unstyled', 'my-1');
            const link = document.createElement('a');
            link.href = `?category=${subcategory.id}`;
            link.textContent = subcategory.name;
            link.classList.add('subcategory-item-txt');
            li.appendChild(link);
            subcategoryDisplay.appendChild(li);
        });
    };

    const updateSelectedCategory = (newIndex) => {
        if (categoryItems[selectedIndex]) {
            categoryItems[selectedIndex].classList.remove('selected');
            const subcategoryList = categoryItems[selectedIndex].querySelector('.subcategory-list');
            if (subcategoryList) {
                subcategoryList.style.display = 'none'; // Hide previous subcategories
            }
        }
        selectedIndex = newIndex;
        if (categoryItems[selectedIndex]) {
            categoryItems[selectedIndex].classList.add('selected');
            const subcategoryList = categoryItems[selectedIndex].querySelector('.subcategory-list');
            if (subcategoryList) {
                subcategoryList.style.display = 'block'; // Show current subcategories
            }
        }
    };

    // Show categories and select the first one on toggle
    toggleButton.addEventListener('click', () => {
        const isExpanded = categoriesContainer.classList.toggle('show');
        toggleButton.setAttribute('aria-expanded', isExpanded);
        if (isExpanded) {
            updateSelectedCategory(0); // Select the first category
        }
    });

//     Add hover effect to the categories
    categoryItems.forEach((item, index) => {
        item.addEventListener('mouseenter', () => {
            updateSelectedCategory(index);
        });

    // W przypadku kliknięcia na kategorię, podkategorie wyświetlają się po prawej stronie
        item.addEventListener('click', () => {
            const subcategoryList = item.querySelector('.subcategory-list');
            if (subcategoryList) {
                subcategoryList.style.display = subcategoryList.style.display === 'block' ? 'none' : 'block';
                updateSubcategories(subcategoryList.querySelectorAll('li'));
            }
        });
    });
});