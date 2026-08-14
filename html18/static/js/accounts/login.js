document.addEventListener('DOMContentLoaded', function() {
    const captchaImage = document.getElementById('captcha-image');
    const captchaInput = document.getElementById('id_captcha_code');
    const captchaWrapper = document.getElementById('captcha-wrapper');

    function refreshCaptcha() {
        const timestamp = new Date().getTime();
        captchaImage.src = '/accounts/captcha/?t=' + timestamp;
        captchaInput.value = '';
        captchaInput.focus();
    }

    if (captchaWrapper) {
        captchaWrapper.addEventListener('click', function(e) {
            if (e.target !== captchaImage) {
                refreshCaptcha();
            }
        });

        captchaImage.addEventListener('click', function(e) {
            e.stopPropagation();
            refreshCaptcha();
        });
    }

    if (captchaInput) {
        captchaInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
});