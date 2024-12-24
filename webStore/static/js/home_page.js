const productContainers = [...document.querySelectorAll('.product-container')];
const nxtBtn = [...document.querySelectorAll('.nxt-btn')];
const preBtn = [...document.querySelectorAll('.pre-btn')];



productContainers.forEach((item, i) => {
    const screenWidth = item.clientWidth;

    function toggleBtnVisibility() {
        if (item.scrollLeft <= 0) {
            preBtn[i].style.display = 'none';
        } else {
            preBtn[i].style.display = 'block';
        }
        if (item.scrollLeft + screenWidth >= item.scrollWidth) {
            nxtBtn[i].style.display = 'none';
        } else {
            nxtBtn[i].style.display = 'block';
        }
    }

    toggleBtnVisibility();

    nxtBtn[i].addEventListener('click', () => {
        item.scrollLeft += screenWidth;
        toggleBtnVisibility();
    })

    preBtn[i].addEventListener('click', () => {
        item.scrollLeft -= screenWidth;
        toggleBtnVisibility();
    })

    item.addEventListener('scroll', toggleBtnVisibility);
})