// static/js/dashboard.js

// Utility function to show notifications instead of alerts
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        padding: 15px;
        border-radius: 5px;
        animation: slideIn 0.5s ease-out;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.5s ease-in';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Function to get CSRF token
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

// Function to enroll in a course
function enrollCourse(courseId) {
    // Disable the enroll button to prevent double-clicking
    const enrollButton = event.target;
    enrollButton.disabled = true;

    fetch(`/enroll/${courseId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('Successfully enrolled in the course!', 'success');
            // Optional: Update UI to show enrolled status
            enrollButton.textContent = 'Enrolled';
            enrollButton.classList.add('enrolled');
        } else {
            showNotification(data.error || 'Failed to enroll in the course.', 'danger');
            // Re-enable the button on failure
            enrollButton.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while enrolling. Please try again.', 'danger');
        // Re-enable the button on error
        enrollButton.disabled = false;
    });
}

// Function to view roadmap
function viewRoadmap(courseId) {
    try {
        window.location.href = `/course/${courseId}/roadmap/`;
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error accessing roadmap. Please try again.', 'danger');
    }
}

// Function to handle image loading errors
function handleImageError(img) {
    img.onerror = null; // Prevent infinite loop
    img.src = '/static/img/placeholder.jpg'; // Replace with your placeholder image path
    console.warn('Failed to load course image:', img.alt);
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); }
        to { transform: translateX(100%); }
    }

    .notification {
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .enrolled {
        background-color: #28a745 !important;
        cursor: default !important;
    }

    .course-card {
        transition: transform 0.2s ease;
    }

    .course-card:hover {
        transform: translateY(-5px);
    }
`;
document.head.appendChild(style);

// Initialize functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add error handling for course images
    document.querySelectorAll('.course-image').forEach(img => {
        img.addEventListener('error', () => handleImageError(img));
    });

    // Initialize any Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Refresh any dynamic content if needed
    }
});

function handleEnrollClick(enrollmentLink) {
    if (enrollmentLink) {
        window.open(enrollmentLink, '_blank');
    } else {
        alert('Enrollment link is not available for this course.');
    }
}

function handleRoadmapClick(roadmapLink) {
    if (roadmapLink) {
        window.open(roadmapLink, '_blank');
    } else {
        alert('Roadmap link is not available for this course.');
    }
}
function handleEnrollClick(enrollmentLink) {
    if (enrollmentLink) {
        window.open(enrollmentLink, '_blank');
    } else {
        alert('Enrollment link is not available for this course.');
    }
}

function handleRoadmapClick(roadmapLink) {
    if (roadmapLink) {
        window.open(roadmapLink, '_blank');
    } else {
        alert('Roadmap link is not available for this course.');
    }
}