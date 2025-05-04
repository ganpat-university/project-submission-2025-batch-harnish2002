document.addEventListener('DOMContentLoaded', function() {
    initializeProfilePage();
    initializeEditableFields();
});

function initializeEditableFields() {
    const formInputs = document.querySelectorAll('#profileForm .form-control:not([readonly])');
    
    formInputs.forEach(input => {
        // Make input readonly initially
        input.readOnly = true;
        
        // Add position-relative to parent container if not already present
        const parentElement = input.parentElement;
        if (!parentElement.classList.contains('position-relative')) {
            parentElement.classList.add('position-relative');
        }
        
        // Create edit icon button
        const editIcon = document.createElement('button');
        editIcon.type = 'button';
        editIcon.className = 'btn btn-link position-absolute';
        editIcon.style.cssText = 'right: 10px; top: 66%; transform: translateY(-50%); padding: 0; margin: 0; z-index: 10;';
        editIcon.innerHTML = '<i class="fas fa-edit"></i>';
        
        // Add the edit icon next to the input (inside the parent)
        parentElement.appendChild(editIcon);
        
        // Add click handler for edit icon
        editIcon.addEventListener('click', function() {
            const isEditing = input.readOnly === false;
            
            if (!isEditing) {
                // Enable editing
                input.readOnly = false;
                input.focus();
                editIcon.innerHTML = '<i class="fas fa-check text-success"></i>';
            } else {
                // Disable editing and trigger save
                saveField(input);
            }
        });
        
        // Add blur handler for input
        input.addEventListener('blur', function() {
            // Small delay to allow clicking the edit/save icon
            setTimeout(() => {
                if (!input.readOnly && !input.contains(document.activeElement)) {
                    saveField(input);
                }
            }, 200);
        });
    });
}

function initializeProfilePage() {
    // Profile picture upload
    const profilePictureInput = document.getElementById('profilePictureInput');
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', handleProfilePictureUpload);
    }

    // Profile form submission
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileFormSubmission);
    }

    // Initialize image error handling
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', handleImageError);
    });

    const deletePhotoBtn = document.getElementById('deletePhoto');
    if (deletePhotoBtn) {
        deletePhotoBtn.addEventListener('click', handleDeletePhoto);
    }
}

function handleDeletePhoto() {
    if (confirm('Are you sure you want to remove your profile picture?')) {
        fetch('/delete_profile_picture/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())  // Parse the JSON response first
        .then(data => {
            if (data.success) {
                showNotification(data.message || 'Profile picture removed successfully', 'success');
                
                // Update both the navbar and profile picture displays
                const profilePictureContainers = document.querySelectorAll('.profile-picture');
                profilePictureContainers.forEach(container => {
                    container.innerHTML = `
                        <div class="default-profile">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="upload-overlay">
                            <i class="fas fa-camera text-white"></i>
                            <input type="file" id="profilePictureInput" accept="image/*">
                        </div>
                    `;
                });

                // Update the navbar profile circle
                const profileCircle = document.querySelector('.profile-circle');
                if (profileCircle) {
                    profileCircle.innerHTML = '<i class="fas fa-user"></i>';
                }

                // Remove the delete photo button if it exists
                const deletePhotoBtn = document.getElementById('deletePhoto');
                if (deletePhotoBtn) {
                    deletePhotoBtn.remove();
                }

                // Reinitialize the event listeners
                initializeProfilePage();
            } else {
                throw new Error(data.error || 'Failed to remove profile picture');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification(error.message || 'Failed to remove profile picture', 'danger');
        });
    }
}

function handleProfilePictureUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('profile_picture', file);
    
    showNotification('Uploading profile picture...', 'info');
    
    fetch('/update_profile_picture/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateProfileImages(data.profile_picture_url);
            showNotification('Profile picture updated successfully!', 'success');
        } else {
            throw new Error(data.error || 'Failed to update profile picture');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showNotification(error.message || 'Upload failed. Please try again.', 'danger');
    });
}

function handleProfileFormSubmission(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    
    showNotification('Saving profile changes...', 'info');

    fetch('/update_profile/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            showNotification('Profile updated successfully!', 'success');
            updateUserInterface(data);
        }
    })
    .catch(handleError)
    .finally(() => submitButton.disabled = false);
}

// Shared functions with dashboard
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'} me-2"></i>
            ${message}
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        padding: 15px;
        border-radius: 5px;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;

    document.body.appendChild(notification);
    setTimeout(() => removeNotification(notification), 3000);
}

function removeNotification(notification) {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
}

function handleImageError(img) {
    img.onerror = null;
    img.src = '/static/img/placeholder.jpg';
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function handleResponse(response) {
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
}

function handleError(error) {
    console.error('Error:', error);
    showNotification(error.message || 'An error occurred. Please try again.', 'danger');
}

function updateProfileImages(url) {
    // Refresh profile images
    document.querySelectorAll('.profile-img, #profileImage').forEach(img => {
        img.src = url + '?t=' + new Date().getTime(); // Bypass cache
    });
}

function updateUserInterface(data) {
    if (data.user_name) {
        document.querySelectorAll('.user-name').forEach(el => {
            el.textContent = data.user_name;
        });
    }
}

function saveField(input) {
    const parentElement = input.parentElement;
    const editIcon = parentElement.querySelector('button');
    
    // Get all form data instead of just the single field
    const form = input.closest('form');
    const formData = new FormData(form);
    
    // Show saving indicator
    editIcon.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    fetch('/update_profile/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            input.readOnly = true;
            editIcon.innerHTML = '<i class="fas fa-edit"></i>';
            showNotification('Field updated successfully!', 'success');
            
            // Update UI if needed
            if (data.user_name) {
                updateUserInterface(data);
            }
        }
    })
    .catch(error => {
        console.error('Save error:', error);
        showNotification(error.message || 'Failed to save changes', 'danger');
        editIcon.innerHTML = '<i class="fas fa-edit"></i>';
    });
}

// Add CSS for animations
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = `
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}
`;
document.head.appendChild(styleSheet);