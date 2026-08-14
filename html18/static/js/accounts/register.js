document.addEventListener('DOMContentLoaded', function() {
    const roleRadios = document.querySelectorAll('input[name="role"]');
    const roleCards = document.querySelectorAll('.role-card');
    const adminKeyDiv = document.getElementById('admin-key-div');

    roleCards.forEach((card, index) => {
        card.addEventListener('click', function() {
            const radio = roleRadios[index];
            radio.checked = true;
            updateRoleCards();
            toggleAdminKey();
        });
    });

    function updateRoleCards() {
        roleCards.forEach((card, index) => {
            if (roleRadios[index].checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }

    function toggleAdminKey() {
        const selectedRole = document.querySelector('input[name="role"]:checked').value;
        if (selectedRole === 'admin' || selectedRole === 'expert') {
            adminKeyDiv.style.display = 'block';
            document.getElementById('id_admin_key').required = true;
        } else {
            adminKeyDiv.style.display = 'none';
            document.getElementById('id_admin_key').required = false;
        }
    }

    roleRadios.forEach(radio => {
        radio.addEventListener('change', toggleAdminKey);
    });

    updateRoleCards();
    toggleAdminKey();

    const sliderVerification = document.getElementById('slider-verification');
    const sliderThumb = document.getElementById('slider-thumb');
    const sliderTrack = document.getElementById('slider-track');
    const sliderText = document.getElementById('slider-text');
    const sendCodeBtn = document.getElementById('send-verification-code');
    const emailInput = document.getElementById('id_email');
    const countdownDisplay = document.getElementById('countdown-display');
    let countdownTimer = null;
    let isSliderVerified = false;
    let isDragging = false;
    let startX = 0;
    let thumbLeft = 0;

    function initSlider() {
        const trackWidth = sliderTrack.offsetWidth;
        const thumbWidth = sliderThumb.offsetWidth;
        const maxLeft = trackWidth - thumbWidth - 2;

        function onMouseDown(e) {
            if (isSliderVerified) return;
            isDragging = true;
            startX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
            thumbLeft = sliderThumb.offsetLeft;
            sliderThumb.style.cursor = 'grabbing';
        }

        function onMouseMove(e) {
            if (!isDragging || isSliderVerified) return;
            e.preventDefault();
            const currentX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
            let newLeft = thumbLeft + (currentX - startX);
            newLeft = Math.max(0, Math.min(newLeft, maxLeft));
            sliderThumb.style.left = newLeft + 'px';
            sliderTrack.querySelector('.slider-track-inner').style.width = (newLeft / maxLeft * 100) + '%';
        }

        function onMouseUp() {
            if (!isDragging || isSliderVerified) return;
            isDragging = false;
            sliderThumb.style.cursor = 'grab';

            const currentLeft = sliderThumb.offsetLeft;
            if (currentLeft >= maxLeft * 0.95) {
                isSliderVerified = true;
                sliderVerification.classList.add('slider-verified');
                sliderText.innerHTML = '<i class="fas fa-check-circle"></i> 验证通过';
                sliderThumb.innerHTML = '<i class="fas fa-check"></i>';
                sliderThumb.style.left = maxLeft + 'px';
                sliderThumb.style.cursor = 'not-allowed';
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                document.removeEventListener('touchmove', onMouseMove);
                document.removeEventListener('touchend', onMouseUp);
            } else {
                sliderThumb.style.left = '0px';
                sliderTrack.querySelector('.slider-track-inner').style.width = '0%';
            }
        }

        sliderThumb.addEventListener('mousedown', onMouseDown);
        sliderThumb.addEventListener('touchstart', onMouseDown, { passive: true });
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        document.addEventListener('touchmove', onMouseMove, { passive: false });
        document.addEventListener('touchend', onMouseUp);
    }

    if (sliderVerification) {
        initSlider();
    }

    if (sendCodeBtn) {
        sendCodeBtn.addEventListener('click', function() {
            if (!isSliderVerified) {
                alert('请先完成滑块验证');
                return;
            }

            const email = emailInput.value.trim();

            if (!email) {
                alert('请先输入邮箱地址');
                emailInput.focus();
                return;
            }

            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(email)) {
                alert('邮箱格式不正确');
                emailInput.focus();
                return;
            }

            sendCodeBtn.disabled = true;
            sendCodeBtn.textContent = '发送中...';

            fetch('/accounts/send-verification-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: 'email=' + encodeURIComponent(email)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    let seconds = 60;
                    countdownDisplay.textContent = seconds + '秒后可重新发送';
                    countdownTimer = setInterval(function() {
                        seconds--;
                        if (seconds <= 0) {
                            clearInterval(countdownTimer);
                            countdownDisplay.textContent = '';
                            sendCodeBtn.disabled = false;
                            sendCodeBtn.textContent = '发送验证码';
                        } else {
                            countdownDisplay.textContent = seconds + '秒后可重新发送';
                        }
                    }, 1000);
                } else {
                    sendCodeBtn.disabled = false;
                    sendCodeBtn.textContent = '发送验证码';
                }
            })
            .catch(error => {
                alert('发送失败，请稍后重试');
                sendCodeBtn.disabled = false;
                sendCodeBtn.textContent = '发送验证码';
            });
        });
    }

    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    // ========== 密码实时验证 ==========
    const password1Input = document.getElementById('id_password1');
    const password2Input = document.getElementById('id_password2');
    const password1Errors = document.getElementById('password1-errors');
    const password2Errors = document.getElementById('password2-errors');

    const passwordRules = [
        { id: 'pw-length', test: function(pw) { return pw.length >= 8; }, message: '至少 8 个字符' },
        { id: 'pw-upper', test: function(pw) { return /[A-Z]/.test(pw); }, message: '包含大写字母' },
        { id: 'pw-lower', test: function(pw) { return /[a-z]/.test(pw); }, message: '包含小写字母' },
        { id: 'pw-digit', test: function(pw) { return /[0-9]/.test(pw); }, message: '包含数字' },
        { id: 'pw-special', test: function(pw) { return /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(pw); }, message: '包含特殊字符' }
    ];

    function validatePassword1() {
        const pw = password1Input.value;
        if (!pw) {
            password1Errors.innerHTML = '';
            password1Input.classList.remove('is-invalid', 'is-valid');
            return;
        }

        var html = '';
        var allPassed = true;
        passwordRules.forEach(function(rule) {
            var passed = rule.test(pw);
            if (!passed) allPassed = false;
            var icon = passed ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-times-circle"></i>';
            var cls = passed ? 'pw-rule-pass' : 'pw-rule-fail';
            html += '<div class="pw-rule-item ' + cls + '">' + icon + ' ' + rule.message + '</div>';
        });

        password1Errors.innerHTML = html;
        password1Input.classList.toggle('is-invalid', !allPassed);
        password1Input.classList.toggle('is-valid', allPassed);

        // 同时校验确认密码
        if (password2Input.value) {
            validatePassword2();
        }
    }

    function validatePassword2() {
        var pw2 = password2Input.value;
        if (!pw2) {
            password2Errors.innerHTML = '';
            password2Input.classList.remove('is-invalid', 'is-valid');
            return;
        }

        if (pw2 !== password1Input.value) {
            password2Errors.innerHTML = '<div class="pw-rule-item pw-rule-fail"><i class="fas fa-times-circle"></i> 两次输入的密码不一致</div>';
            password2Input.classList.add('is-invalid');
            password2Input.classList.remove('is-valid');
        } else {
            password2Errors.innerHTML = '<div class="pw-rule-item pw-rule-pass"><i class="fas fa-check-circle"></i> 密码一致</div>';
            password2Input.classList.remove('is-invalid');
            password2Input.classList.add('is-valid');
        }
    }

    if (password1Input) {
        password1Input.addEventListener('input', validatePassword1);
    }
    if (password2Input) {
        password2Input.addEventListener('input', validatePassword2);
    }
});