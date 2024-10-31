function phoneMask() {
    var num = $(this).val().replace(/\D/g,'');
    if (num.length > 0) {
        $(this).val(num.replace(/^(\d{3})(\d{3})(\d{3})$/, '$1-$2-$3'));
    }
}
$('[type="tel"]').keyup(phoneMask);