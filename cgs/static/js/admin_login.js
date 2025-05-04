// static/js/admin_login.js
document.getElementById('adminLoginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');
    const submitButton = this.querySelector('button[type="submit"]');
    
    // Clear previous error message
    errorMessage.textContent = '';
    
    // Basic validation
    if (!username || !password) {
        errorMessage.textContent = 'Please enter both username and password';
        return;
    }
    
    // Get the CAPTCHA response
    const captchaResponse = grecaptcha.getResponse();
    console.log("CAPTCHA Response:", captchaResponse ? "Valid" : "Empty", captchaResponse ? captchaResponse.substr(0, 20) + "..." : "");
    
    if (!captchaResponse) {
        errorMessage.textContent = 'Please complete the CAPTCHA verification';
        return;
    }
    
    try {
        // Disable submit button while processing
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/admin-login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                username: username,
                password: password,
                captcha: captchaResponse
            }),
            credentials: 'same-origin',
            cache: 'no-cache'
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            
            if (response.ok && data.success) {
                window.location.href = data.redirect;
            } else {
                errorMessage.textContent = data.error || 'Login failed. Please try again.';
                grecaptcha.reset();
            }
        } else {
            throw new Error('Received non-JSON response from server');
        }
    } catch (error) {
        console.error('Login error:', error);
        errorMessage.textContent = 'An error occurred. Please try again.';
        grecaptcha.reset();
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = 'Login';
    }
});

// Password toggle visibility function
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('togglePassword');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    }
}