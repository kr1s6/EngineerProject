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
