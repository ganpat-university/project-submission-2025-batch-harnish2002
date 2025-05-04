// quiz.js
document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('quizForm');
    if (!quizForm) return;

    // Initialize progress tracking
    const totalQuestions = document.querySelectorAll('.question-container').length;
    let answeredQuestions = 0;
    let isSubmitting = false; // Flag to track submission state
    updateProgress();

    // Timer functionality with warning colors
    let timeLeft = 15 * 60; // 15 minutes in seconds
    const timerDisplay = document.querySelector('#timer span');
    const timerIcon = document.querySelector('#timer i');

    const timer = setInterval(() => {
        timeLeft--;
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        // Change timer color based on time remaining
        if (timeLeft <= 60) { // Last minute
            timerDisplay.style.color = '#dc3545';
            timerIcon.style.color = '#dc3545';
            if (!document.querySelector('.timer-warning')) {
                showNotification('Only 1 minute remaining!', 'warning');
            }
        } else if (timeLeft <= 180) { // Last 3 minutes
            timerDisplay.style.color = '#ffc107';
            timerIcon.style.color = '#ffc107';
        }

        if (timeLeft <= 0) {
            clearInterval(timer);
            showNotification('Time\'s up! Submitting quiz...', 'info');
            submitQuiz();
        }
    }, 1000);

    // Track question answers for progress bar
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const questionContainer = this.closest('.question-container');
            if (!questionContainer.classList.contains('answered')) {
                questionContainer.classList.add('answered');
                answeredQuestions++;
                updateProgress();
            }
        });
    });

    function updateProgress() {
        const progressBar = document.querySelector('.progress-bar');
        const percentage = (answeredQuestions / totalQuestions) * 100;
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('aria-valuenow', percentage);
    }

    // Enhanced quiz submission with validation
    function submitQuiz() {
        if (isSubmitting) return; // Prevent multiple submissions
        
        const attemptId = quizForm.dataset.attemptId;
        const answers = [];
        const questions = document.querySelectorAll('.question-container');
        let unansweredCount = 0;

        questions.forEach(question => {
            const questionId = question.querySelector('input[type="radio"]').name.slice(1);
            const selectedOption = question.querySelector('input[type="radio"]:checked');
            
            if (selectedOption) {
                answers.push({
                    question_id: questionId,
                    selected_option: selectedOption.value
                });
            } else {
                unansweredCount++;
                question.classList.add('unanswered-warning');
            }
        });

        if (unansweredCount > 0 && timeLeft > 0) {
            showNotification(`You have ${unansweredCount} unanswered questions!`, 'warning');
            return;
        }

        // Set submitting flag
        isSubmitting = true;

        // Disable form submission
        const submitButton = quizForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';

        // Show a loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-white">Submitting your quiz and preparing results...</p>
        `;
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
        document.body.appendChild(loadingOverlay);

        fetch(`/quiz/${attemptId}/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(answers)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                clearInterval(timer); // Stop the timer
                showNotification('Quiz submitted successfully!', 'success');
                
                // Remove the beforeunload event listener
                window.removeEventListener('beforeunload', beforeUnloadHandler);
                
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1000);
            } else {
                throw new Error(data.error || 'Failed to submit quiz');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Remove loading overlay
            document.body.removeChild(loadingOverlay);
            showNotification('Failed to submit quiz. Please try again.', 'error');
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-check-circle me-2"></i>Submit Quiz';
            isSubmitting = false; // Reset submitting flag
        });
    }

    // Custom notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification fade-in`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 300px;
        `;
        notification.innerHTML = `
            <i class="fas ${getIconForType(type)} me-2"></i>
            ${message}
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    function getIconForType(type) {
        const icons = {
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            error: 'fa-times-circle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    // Define beforeUnloadHandler separately so we can remove it later
    const beforeUnloadHandler = function(e) {
        if (!isSubmitting && timeLeft > 0 && answeredQuestions > 0) {
            e.preventDefault();
            e.returnValue = '';
        }
    };

    // Add beforeunload event listener
    window.addEventListener('beforeunload', beforeUnloadHandler);

    // Form submission handler
    quizForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (timeLeft > 0) {
            if (confirm('Are you sure you want to submit the quiz?')) {
                submitQuiz();
            }
        } else {
            submitQuiz();
        }
    });
});