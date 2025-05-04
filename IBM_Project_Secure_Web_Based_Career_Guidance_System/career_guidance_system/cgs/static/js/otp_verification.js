document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('.otp-input');
    const form = document.getElementById('otpForm');
    const errorMessage = document.getElementById('error-message');

    // Handle input behavior
    inputs.forEach((input, index) => {
        input.addEventListener('keyup', function(e) {
            if (e.key >= 0 && e.key <= 9) {
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            } else if (e.key === 'Backspace') {
                if (index > 0) {
                    inputs[index - 1].focus();
                }
            }
        });
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const otp = Array.from(inputs).map(input => input.value).join('');
        if (otp.length !== 4) {
            errorMessage.textContent = 'Please enter all 4 digits';
            return;
        }

        const urlParams = new URLSearchParams(window.location.search);
        const email = urlParams.get('email');
        const purpose = urlParams.get('purpose');

        try {
            const response = await fetch(`/${purpose}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    email: email,
                    otp: otp
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                window.location.href = purpose === 'register' ? '/login/' : '/dashboard/';
            } else {
                errorMessage.textContent = data.error;
            }
        } catch (error) {
            errorMessage.textContent = 'An error occurred. Please try again.';
        }
    });

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});