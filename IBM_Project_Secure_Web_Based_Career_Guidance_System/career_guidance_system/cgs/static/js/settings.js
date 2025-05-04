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

// Password strength checker
document.getElementById('new_password').addEventListener('input', function() {
    const password = this.value;
    const strengthEl = document.getElementById('passwordStrength');
    
    if (password.length === 0) {
        strengthEl.innerHTML = '';
        return;
    }
    
    let strength = 0;
    let feedback = '';
    
    // Length check
    if (password.length >= 8) {
        strength += 1;
    }
    
    // Contains number
    if (/\d/.test(password)) {
        strength += 1;
    }
    
    // Contains lowercase
    if (/[a-z]/.test(password)) {
        strength += 1;
    }
    
    // Contains uppercase
    if (/[A-Z]/.test(password)) {
        strength += 1;
    }
    
    // Contains special char
    if (/[^A-Za-z0-9]/.test(password)) {
        strength += 1;
    }
    
    // Set feedback based on strength
    if (strength < 2) {
        feedback = '<div class="progress" style="height: 5px;"><div class="progress-bar bg-danger" style="width: 20%"></div></div><small class="text-danger">Weak password</small>';
    } else if (strength < 4) {
        feedback = '<div class="progress" style="height: 5px;"><div class="progress-bar bg-warning" style="width: 60%"></div></div><small class="text-warning">Moderate password</small>';
    } else {
        feedback = '<div class="progress" style="height: 5px;"><div class="progress-bar bg-success" style="width: 100%"></div></div><small class="text-success">Strong password</small>';
    }
    
    strengthEl.innerHTML = feedback;
});

// Password match checker
document.getElementById('confirm_password').addEventListener('input', function() {
    const password = document.getElementById('new_password').value;
    const confirmPassword = this.value;
    const matchEl = document.getElementById('passwordMatch');
    
    if (confirmPassword.length === 0) {
        matchEl.innerHTML = '';
        return;
    }
    
    if (password === confirmPassword) {
        matchEl.innerHTML = '<small class="text-success"><i class="fas fa-check-circle"></i> Passwords match</small>';
    } else {
        matchEl.innerHTML = '<small class="text-danger"><i class="fas fa-times-circle"></i> Passwords do not match</small>';
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
    
    const tabPane = document.querySelector('#password-settings');
    const header = tabPane.querySelector('.settings-header');
    tabPane.insertBefore(alertElement, header.nextSibling);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => alertElement.remove(), 150);
    }, 5000);
}

// Client-side form validation
document.getElementById('changePasswordForm').addEventListener('submit', function(event) {
    const currentPassword = document.getElementById('current_password').value;
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    let isValid = true;
    let errorMessage = '';
    
    // Password requirements validation
    if (newPassword.length < 8) {
        isValid = false;
        errorMessage = 'Password must be at least 8 characters long.';
    } else if (!(/[A-Za-z]/.test(newPassword) && /\d/.test(newPassword))) {
        isValid = false;
        errorMessage = 'Password must contain both letters and numbers.';
    }
    
    // Password match validation
    if (newPassword !== confirmPassword) {
        isValid = false;
        errorMessage = 'New password and confirmation do not match.';
    }
    
    // Current password validation
    if (newPassword === currentPassword) {
        isValid = false;
        errorMessage = 'New password cannot be the same as your current password.';
    }
    
    if (!isValid) {
        event.preventDefault();
        showAlert(errorMessage, 'danger');
    }
    
    // Add active tab to form data
    const activeTab = document.querySelector('.nav-link.active');
    if (activeTab) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'active_tab';
        input.value = activeTab.getAttribute('href').substring(1);
        this.appendChild(input);
    }
});

// Tab state management
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab from server-side state or URL hash
    let activeTabId = '{{ active_tab }}' || window.location.hash.substring(1);
    
    if (activeTabId) {
        // Remove the '-settings' suffix if present
        activeTabId = activeTabId.replace('-settings', '-settings');
        const tab = document.querySelector(`a[href="#${activeTabId}"]`);
        if (tab) {
            const bsTab = new bootstrap.Tab(tab);
            bsTab.show();
        }
    }
    
    // Update URL hash when tabs change
    const tabElements = document.querySelectorAll('a[data-bs-toggle="pill"]');
    tabElements.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            const hash = event.target.getAttribute('href');
            if (history.pushState) {
                history.pushState(null, null, hash);
            } else {
                window.location.hash = hash;
            }
        });
    });
    
    // Handle browser back/forward
    window.addEventListener('popstate', function() {
        const hash = window.location.hash;
        if (hash) {
            const tab = document.querySelector(`a[href="${hash}"]`);
            if (tab) {
                const bsTab = new bootstrap.Tab(tab);
                bsTab.show();
            }
        }
    });
});

// Form submission handlers for other settings forms (if enabled in the future)
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!this.matches('#changePasswordForm')) { // Skip password form as it's handled separately
            e.preventDefault();
            
            // Simulate form submission - replace with your actual API calls
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            
            // Simulate API call
            setTimeout(() => {
                showAlert('Settings saved successfully!', 'success');
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }, 1000);
        }
    });
});