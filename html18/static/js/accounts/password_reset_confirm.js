document.addEventListener('DOMContentLoaded', function() {
    const newPassword1 = document.getElementById('id_new_password1');
    const newPassword2 = document.getElementById('id_new_password2');
    const passwordStrength = document.getElementById('passwordStrength');
    const passwordMatch = document.getElementById('passwordMatch');
    const submitBtn = document.getElementById('submitBtn');

    // 密码强度检查
    function checkPasswordStrength(password) {
        let strength = 0;
        let requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)
        };

        // 更新要求显示
        updateRequirement('req-length', requirements.length);
        updateRequirement('req-uppercase', requirements.uppercase);
        updateRequirement('req-lowercase', requirements.lowercase);
        updateRequirement('req-number', requirements.number);
        updateRequirement('req-special', requirements.special);

        // 计算强度
        strength = Object.values(requirements).filter(r => r).length;

        // 显示强度
        if (password.length === 0) {
            passwordStrength.innerHTML = '';
            passwordStrength.className = 'password-strength';
        } else if (strength < 3) {
            passwordStrength.innerHTML = '<i class="fas fa-exclamation-triangle"></i> 密码强度：弱';
            passwordStrength.className = 'password-strength strength-weak';
        } else if (strength < 5) {
            passwordStrength.innerHTML = '<i class="fas fa-info-circle"></i> 密码强度：中';
            passwordStrength.className = 'password-strength strength-medium';
        } else {
            passwordStrength.innerHTML = '<i class="fas fa-check-circle"></i> 密码强度：强';
            passwordStrength.className = 'password-strength strength-strong';
        }

        return strength;
    }

    function updateRequirement(id, valid) {
        const element = document.getElementById(id);
        if (valid) {
            element.className = 'requirement valid';
            element.innerHTML = '<i class="fas fa-check"></i> ' + element.textContent.substring(2);
        } else {
            element.className = 'requirement invalid';
            element.innerHTML = '<i class="fas fa-circle"></i> ' + element.textContent.substring(2);
        }
    }

    // 检查密码匹配
    function checkPasswordMatch() {
        const pass1 = newPassword1.value;
        const pass2 = newPassword2.value;

        if (pass2.length === 0) {
            passwordMatch.innerHTML = '';
            return false;
        } else if (pass1 === pass2) {
            passwordMatch.innerHTML = '<span class="text-success"><i class="fas fa-check"></i> 两次输入的密码一致</span>';
            return true;
        } else {
            passwordMatch.innerHTML = '<span class="text-danger"><i class="fas fa-times"></i> 两次输入的密码不一致</span>';
            return false;
        }
    }

    // 监听密码输入
    newPassword1.addEventListener('input', function() {
        checkPasswordStrength(this.value);
        if (newPassword2.value) {
            checkPasswordMatch();
        }
    });

    newPassword2.addEventListener('input', function() {
        checkPasswordMatch();
    });

    // 表单提交验证
    document.getElementById('resetPasswordForm').addEventListener('submit', function(e) {
        const pass1 = newPassword1.value;
        const pass2 = newPassword2.value;

        // 检查密码强度
        const strength = checkPasswordStrength(pass1);
        if (strength < 5) {
            e.preventDefault();
            alert('新密码强度不足，请满足所有密码要求！');
            return;
        }

        // 检查密码匹配
        if (pass1 !== pass2) {
            e.preventDefault();
            alert('两次输入的新密码不一致！');
            return;
        }
    });
});