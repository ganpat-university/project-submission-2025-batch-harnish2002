document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");
    const submitButton = this.querySelector('button[type="submit"]');

    // Clear previous error message
    errorMessage.textContent = '';
    
    // Basic validation
    if (!email || !password) {
        errorMessage.textContent = 'Please enter both email and password';
        return;
    }
    
    // Get the CAPTCHA response
    const captchaResponse = grecaptcha.getResponse();
    console.log("CAPTCHA Response:", captchaResponse ? "Valid" : "Empty", captchaResponse ? captchaResponse.substr(0, 20) + "..." : "");
    
    if (!captchaResponse) {
        errorMessage.textContent = 'Please complete the CAPTCHA verification';
        return;
    }

    // Get CSRF token from the cookie
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith('csrftoken=')) {
                    cookieValue = cookie.substring(10);
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrfToken = getCSRFToken();

    try {
        // Disable submit button while processing
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';
        
        const response = await fetch("/login/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ 
                email, 
                password,
                captcha: captchaResponse 
            })
        });

        const data = await response.json();

        if (data.require_otp) {
            // Redirect to OTP verification page
            window.location.href = `/otp_verification/?email=${encodeURIComponent(email)}&purpose=login`;
        } else if (data.error) {
            errorMessage.textContent = data.error;
            grecaptcha.reset();
        }
    } catch (error) {
        errorMessage.textContent = "An error occurred. Please try again.";
        grecaptcha.reset();
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = 'Login';
    }
});

// Password toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('password');
    const passwordToggle = document.getElementById('password-toggle');
    
    passwordToggle.addEventListener('click', function() {
        // Toggle password visibility
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            passwordToggle.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordField.type = 'password';
            passwordToggle.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });
});