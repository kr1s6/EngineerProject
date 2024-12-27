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

//Like/unlike product
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

    const updateSubcategories = (subcategories) => {
        subcategoryDisplay.innerHTML = '';

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
        event.stopPropagation();
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

    // Hide categories when clicking outside of the header_categories
    document.addEventListener('click', (event) => {
        if (!categoriesContainer.contains(event.target) && event.target !== toggleButton) {
            categoriesContainer.classList.remove('show');
            toggleButton.setAttribute('aria-expanded', false);
        }
    });
});


document.addEventListener("DOMContentLoaded", function () {
    var coll = document.getElementsByClassName("collapsible");
    var verticalMenus = document.querySelectorAll(".vertical-menu");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            this.classList.toggle("active");
            var content = this.nextElementSibling;

            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
    var contents = document.querySelectorAll(".content");
    contents.forEach(function (content) {
        content.style.display = "none";
    });


    // Ukryj menu, gdy klikniesz poza nim
    document.addEventListener("click", function (event) {
        var clickedInsideMenu = Array.from(verticalMenus).some(function (menu) {
            return menu.contains(event.target);
        });

        var clickedButton = Array.from(coll).some(function (button) {
            return button.contains(event.target);
        });

        if (!clickedInsideMenu && !clickedButton) {
            verticalMenus.forEach(function (menu) {
                menu.style.display = "none";
            });
        }
    });
});

//Sticky header
$(window).scroll(function () {
    var scroll = $(window).scrollTop();
    var header = $('#entire_header').height();

    if (scroll >= header + 250) {
        $("#entire_header").addClass("background-header");
    } else {
        $("#entire_header").removeClass("background-header");
    }
});
