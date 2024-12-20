const productContainers = [...document.querySelectorAll('.product-container')];
const nxtBtn = [...document.querySelectorAll('.nxt-btn')];
const preBtn = [...document.querySelectorAll('.pre-btn')];

productContainers.forEach((item, i) => {
    nxtBtn[i].addEventListener('click', () => {
        item.scrollLeft += 350;
    })

    preBtn[i].addEventListener('click', () => {
        item.scrollLeft -= 350;
    })
})