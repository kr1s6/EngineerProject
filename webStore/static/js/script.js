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
    document.getElementById('id_birthday').setAttribute('max', today);
}

window.onload = setMaxDate;
