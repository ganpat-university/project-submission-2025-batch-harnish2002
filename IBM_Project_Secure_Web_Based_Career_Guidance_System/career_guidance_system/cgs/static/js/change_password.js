        // Function to toggle password visibility
        function togglePasswordVisibility(inputId) {
            const input = document.getElementById(inputId);
            const icon = input.nextElementSibling.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }
        
        // Form validation
        document.getElementById('changePasswordForm').addEventListener('submit', function(event) {
            const currentPassword = document.getElementById('current_password').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            // Check if new password meets requirements
            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
            if (!passwordRegex.test(newPassword)) {
                event.preventDefault();
                showAlert('New password must be at least 8 characters with letters and numbers.', 'danger');
                return;
            }
            
            // Check if new password matches confirmation
            if (newPassword !== confirmPassword) {
                event.preventDefault();
                showAlert('New password and confirmation do not match.', 'danger');
                return;
            }
            
            // Check if new password is same as current password
            if (newPassword === currentPassword) {
                event.preventDefault();
                showAlert('New password cannot be the same as your current password.', 'warning');
                return;
            }
        });
        
        // Function to show alert
        function showAlert(message, type) {
            const alertElement = document.createElement('div');
            alertElement.className = `alert alert-${type} alert-dismissible fade show`;
            alertElement.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            const cardBody = document.querySelector('.card-body');
            const form = document.getElementById('changePasswordForm');
            cardBody.insertBefore(alertElement, form);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alertElement.classList.remove('show');
                setTimeout(() => alertElement.remove(), 150);
            }, 5000);
        }