document.addEventListener('DOMContentLoaded', function() {
    // ========== 状态变量 ==========
    var currentStep = 1;
    var userEmail = '';
    var verifiedCode = '';
    var isSliderVerified = false;
    var countdownTimer = null;

    // ========== DOM 元素 ==========
    var emailInput = document.getElementById('reset-email');
    var emailError = document.getElementById('email-error');
    var sendCodeBtn = document.getElementById('send-code-btn');
    var countdownDisplay = document.getElementById('send-code-countdown');
    var codeInput = document.getElementById('reset-code');
    var codeError = document.getElementById('code-error');
    var verifyCodeBtn = document.getElementById('verify-code-btn');
    var resendCodeBtn = document.getElementById('resend-code-btn');
    var password1Input = document.getElementById('new-password1');
    var password2Input = document.getElementById('new-password2');
    var password1Errors = document.getElementById('password1-errors');
    var password2Errors = document.getElementById('password2-errors');
    var resetPasswordBtn = document.getElementById('reset-password-btn');
    var displayEmail = document.getElementById('display-email');
    var backToLogin = document.getElementById('back-to-login');

    // ========== 步骤切换 ==========
    function goToStep(step) {
        // 隐藏所有步骤内容
        document.querySelectorAll('.step-content').forEach(function(el) {
            el.classList.remove('active');
        });

        // 显示目标步骤
        var targetContent = document.getElementById('step-' + step);
        if (targetContent) {
            targetContent.classList.add('active');
        }

        // 更新步骤指示器
        for (var i = 1; i <= 3; i++) {
            var indicator = document.getElementById('step-indicator-' + i);
            if (indicator) {
                indicator.classList.remove('active', 'completed');
                if (i < step) {
                    indicator.classList.add('completed');
                } else if (i === step) {
                    indicator.classList.add('active');
                }
            }
        }

        // 更新连接线
        for (var j = 1; j <= 2; j++) {
            var line = document.getElementById('step-line-' + j);
            if (line) {
                line.classList.toggle('active', j < step);
            }
        }

        // 成功页面特殊处理
        if (step === 'success') {
            document.querySelectorAll('.step-content').forEach(function(el) {
                el.classList.remove('active');
            });
            document.getElementById('step-success').classList.add('active');
            document.querySelectorAll('.step').forEach(function(el) {
                el.classList.add('completed');
            });
            document.querySelectorAll('.step-line').forEach(function(el) {
                el.classList.add('active');
            });
            if (backToLogin) backToLogin.style.display = 'none';
        } else {
            if (backToLogin) backToLogin.style.display = '';
        }

        currentStep = step;
    }

    // ========== 滑块验证 ==========
    var sliderVerification = document.getElementById('slider-verification');
    var sliderThumb = document.getElementById('slider-thumb');
    var sliderTrack = document.getElementById('slider-track');
    var sliderText = document.getElementById('slider-text');
    var isDragging = false;
    var startX = 0;
    var thumbLeft = 0;

    function initSlider() {
        var trackWidth = sliderTrack.offsetWidth;
        var thumbWidth = sliderThumb.offsetWidth;
        var maxLeft = trackWidth - thumbWidth - 2;

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
            var currentX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
            var newLeft = thumbLeft + (currentX - startX);
            newLeft = Math.max(0, Math.min(newLeft, maxLeft));
            sliderThumb.style.left = newLeft + 'px';
            sliderTrack.querySelector('.slider-track-inner').style.width = (newLeft / maxLeft * 100) + '%';
        }

        function onMouseUp() {
            if (!isDragging || isSliderVerified) return;
            isDragging = false;
            sliderThumb.style.cursor = 'grab';

            var currentLeft = sliderThumb.offsetLeft;
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
                checkStep1Ready();
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

    // ========== 步骤1：邮箱验证 ==========
    function validateEmail() {
        var email = emailInput.value.trim();
        if (!email) {
            emailError.textContent = '';
            emailInput.classList.remove('is-valid', 'is-invalid');
            return false;
        }
        var emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(email)) {
            emailError.textContent = '邮箱格式不正确';
            emailInput.classList.add('is-invalid');
            emailInput.classList.remove('is-valid');
            return false;
        }
        emailError.textContent = '';
        emailInput.classList.remove('is-invalid');
        emailInput.classList.add('is-valid');
        return true;
    }

    function checkStep1Ready() {
        var emailValid = validateEmail();
        sendCodeBtn.disabled = !(emailValid && isSliderVerified);
    }

    if (emailInput) {
        emailInput.addEventListener('input', function() {
            validateEmail();
            checkStep1Ready();
        });
    }

    // ========== 发送验证码 ==========
    function startCountdown(seconds) {
        sendCodeBtn.disabled = true;
        resendCodeBtn.disabled = true;
        countdownDisplay.textContent = seconds + '秒后可重新发送';

        countdownTimer = setInterval(function() {
            seconds--;
            if (seconds <= 0) {
                clearInterval(countdownTimer);
                countdownDisplay.textContent = '';
                if (currentStep === 1) {
                    sendCodeBtn.disabled = false;
                }
                resendCodeBtn.disabled = false;
            } else {
                countdownDisplay.textContent = seconds + '秒后可重新发送';
            }
        }, 1000);
    }

    function sendResetCode() {
        var email = emailInput.value.trim();
        if (!validateEmail()) return;

        sendCodeBtn.disabled = true;
        sendCodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';

        fetch('/accounts/send-verification-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: 'email=' + encodeURIComponent(email) + '&purpose=password_reset'
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.success) {
                userEmail = email;
                displayEmail.textContent = email;
                goToStep(2);
                startCountdown(60);
            } else {
                emailError.textContent = data.message;
                sendCodeBtn.disabled = false;
            }
            sendCodeBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发送验证码';
        })
        .catch(function() {
            emailError.textContent = '发送失败，请稍后重试';
            sendCodeBtn.disabled = false;
            sendCodeBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发送验证码';
        });
    }

    if (sendCodeBtn) {
        sendCodeBtn.addEventListener('click', sendResetCode);
    }

    // ========== 步骤2：验证码验证 ==========
    if (resendCodeBtn) {
        resendCodeBtn.addEventListener('click', function() {
            if (resendCodeBtn.disabled) return;
            resendCodeBtn.disabled = true;
            resendCodeBtn.textContent = '发送中...';

            fetch('/accounts/send-verification-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: 'email=' + encodeURIComponent(userEmail) + '&purpose=password_reset'
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    startCountdown(60);
                } else {
                    codeError.textContent = data.message;
                    resendCodeBtn.disabled = false;
                }
                resendCodeBtn.textContent = '重新发送';
            })
            .catch(function() {
                codeError.textContent = '发送失败，请稍后重试';
                resendCodeBtn.disabled = false;
                resendCodeBtn.textContent = '重新发送';
            });
        });
    }

    if (verifyCodeBtn) {
        verifyCodeBtn.addEventListener('click', function() {
            var code = codeInput.value.trim();
            if (!code) {
                codeError.textContent = '请输入验证码';
                return;
            }
            if (code.length !== 6) {
                codeError.textContent = '验证码为6位数字';
                return;
            }

            verifyCodeBtn.disabled = true;
            verifyCodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 验证中...';

            fetch('/accounts/verify-reset-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: 'email=' + encodeURIComponent(userEmail) + '&code=' + encodeURIComponent(code)
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    verifiedCode = code;
                    goToStep(3);
                } else {
                    codeError.textContent = data.message;
                    codeInput.classList.add('is-invalid');
                    codeInput.classList.remove('is-valid');
                }
                verifyCodeBtn.disabled = false;
                verifyCodeBtn.innerHTML = '<i class="fas fa-check-circle"></i> 验证';
            })
            .catch(function() {
                codeError.textContent = '验证失败，请稍后重试';
                verifyCodeBtn.disabled = false;
                verifyCodeBtn.innerHTML = '<i class="fas fa-check-circle"></i> 验证';
            });
        });
    }

    // ========== 步骤3：密码重置 ==========
    var passwordRules = [
        { test: function(pw) { return pw.length >= 8; }, message: '至少 8 个字符' },
        { test: function(pw) { return /[A-Z]/.test(pw); }, message: '包含大写字母' },
        { test: function(pw) { return /[a-z]/.test(pw); }, message: '包含小写字母' },
        { test: function(pw) { return /[0-9]/.test(pw); }, message: '包含数字' },
        { test: function(pw) { return /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(pw); }, message: '包含特殊字符' }
    ];

    function validatePassword1() {
        var pw = password1Input.value;
        if (!pw) {
            password1Errors.innerHTML = '';
            password1Input.classList.remove('is-invalid', 'is-valid');
            return false;
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

        if (password2Input.value) {
            validatePassword2();
        }

        return allPassed;
    }

    function validatePassword2() {
        var pw2 = password2Input.value;
        if (!pw2) {
            password2Errors.innerHTML = '';
            password2Input.classList.remove('is-invalid', 'is-valid');
            return false;
        }

        if (pw2 !== password1Input.value) {
            password2Errors.innerHTML = '<div class="pw-rule-item pw-rule-fail"><i class="fas fa-times-circle"></i> 两次输入的密码不一致</div>';
            password2Input.classList.add('is-invalid');
            password2Input.classList.remove('is-valid');
            return false;
        } else {
            password2Errors.innerHTML = '<div class="pw-rule-item pw-rule-pass"><i class="fas fa-check-circle"></i> 密码一致</div>';
            password2Input.classList.remove('is-invalid');
            password2Input.classList.add('is-valid');
            return true;
        }
    }

    if (password1Input) {
        password1Input.addEventListener('input', validatePassword1);
    }
    if (password2Input) {
        password2Input.addEventListener('input', validatePassword2);
    }

    if (resetPasswordBtn) {
        resetPasswordBtn.addEventListener('click', function() {
            var pw1Valid = validatePassword1();
            var pw2Valid = validatePassword2();

            if (!pw1Valid || !pw2Valid) {
                return;
            }

            resetPasswordBtn.disabled = true;
            resetPasswordBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 重置中...';

            fetch('/accounts/reset-password-with-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: 'email=' + encodeURIComponent(userEmail) +
                      '&code=' + encodeURIComponent(verifiedCode) +
                      '&new_password1=' + encodeURIComponent(password1Input.value) +
                      '&new_password2=' + encodeURIComponent(password2Input.value)
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    goToStep('success');
                } else {
                    alert(data.message);
                    resetPasswordBtn.disabled = false;
                    resetPasswordBtn.innerHTML = '<i class="fas fa-save"></i> 重置密码';
                }
            })
            .catch(function() {
                alert('重置失败，请稍后重试');
                resetPasswordBtn.disabled = false;
                resetPasswordBtn.innerHTML = '<i class="fas fa-save"></i> 重置密码';
            });
        });
    }

    // ========== 返回按钮 ==========
    var backToStep1 = document.getElementById('back-to-step1');
    var backToStep2 = document.getElementById('back-to-step2');

    if (backToStep1) {
        backToStep1.addEventListener('click', function() {
            goToStep(1);
        });
    }

    if (backToStep2) {
        backToStep2.addEventListener('click', function() {
            goToStep(2);
        });
    }

    // ========== 工具函数 ==========
    function getCsrfToken() {
        var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }
});
