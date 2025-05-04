// Get CSRF token from cookie
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
const csrfToken = getCookie('csrftoken');

// Helper function to show alerts
function showAlert(type, message) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Remove any existing alerts
    $('#alert-container').html('');
    
    // Add new alert
    $('#alert-container').append(alertHtml);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

// Document ready function
$(document).ready(function() {
    // Add a slight delay to ensure the DOM is fully loaded
    setTimeout(function() {
        // Only initialize charts if on the dashboard tab
        if ($('#dashboard-tab').hasClass('active')) {
            setInterval(refreshRecentActivities, 60000);
            console.log('Dashboard tab is active, initializing charts');
            initializeQuizPerformanceCharts();
        }
        
        // Also initialize charts when switching to dashboard tab
        $('.tab-link, .active-tab').on('click', function() {
            if ($(this).data('tab') === 'dashboard') {
                refreshRecentActivities();
                console.log('Switched to dashboard tab, initializing charts');
                // Small timeout to ensure the tab is visible
                setTimeout(initializeQuizPerformanceCharts, 300);
            }
        });
    }, 500);
    
    // Initialize sidebar toggle
    const toggleSidebar = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('#sidebar');
    
    toggleSidebar.addEventListener('click', function() {
        sidebar.classList.toggle('hide');
    });

    // Tab switching
    const tabLinks = document.querySelectorAll('.tab-link, .active-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const sectionTitle = document.getElementById('current-section-title');
    const activeBreadcrumb = document.querySelector('.active-breadcrumb');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs and links
            tabLinks.forEach(tab => {
                tab.classList.remove('active');
                tab.parentElement.classList.remove('active');
            });
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            this.parentElement.classList.add('active');
            
            const tabId = this.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
            
            // Update section title and breadcrumb
            sectionTitle.textContent = tabId.charAt(0).toUpperCase() + tabId.slice(1);
            activeBreadcrumb.textContent = sectionTitle.textContent;
            
            // Initialize DataTables for tables in the active tab
            if (tabId === 'users') {
                $('#users-table').DataTable();
            } else if (tabId === 'courses') {
                $('#courses-table').DataTable();
            } else if (tabId === 'quizzes') {
                $('#quizzes-table').DataTable();
            } else if (tabId === 'questions') {
                $('#questions-table').DataTable();
            }
        });
    });
    // Initialize DataTables
    //$('#users-table').DataTable();
    //$('#courses-table').DataTable();
    //$('#quizzes-table').DataTable();

    // QUESTIONS MANAGEMENT
// Initialize DataTable for questions
const questionsTable = $('#questions-table').DataTable({
    responsive: true,
    columnDefs: [
        { orderable: false, targets: [4] } // Disable ordering on action column
    ],
    order: [[0, 'asc']], // Sort by ID by default
    pageLength: 10
});

// Handle quiz filter
$('#quizFilter').on('change', function() {
    const quizId = $(this).val();
    questionsTable.column(1).search(quizId ? $(this).find('option:selected').text() : '').draw();
});

// Handle add question button
$('#add-question-btn').on('click', function() {
    // Clear form
    $('#questionForm')[0].reset();
    $('#questionId').val('');
    $('#questionModalTitle').text('Add New Question');
    $('#questionModal').modal('show');
});

// Handle edit question button
$(document).on('click', '.edit-question', function() {
    const questionId = $(this).data('id');
    $('#questionId').val(questionId);
    $('#questionModalTitle').text('Edit Question');
    
    // Fetch question details
    fetch(`/get_question/${questionId}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const question = data.question;
            $('#questionQuiz').val(question.quiz_id);
            $('#questionText').val(question.text);
            $('#option1').val(question.option1);
            $('#option2').val(question.option2);
            $('#option3').val(question.option3);
            $('#option4').val(question.option4);
            $('#correctOption').val(question.correct_option);
            $('#questionModal').modal('show');
        } else {
            showAlert('danger', 'Error fetching question details: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while fetching question details.');
    });
});

// Handle save question button
$('#saveQuestionBtn').on('click', function() {
    // Validate form
    if (!$('#questionForm')[0].checkValidity()) {
        $('#questionForm')[0].reportValidity();
        return;
    }
    
    const questionId = $('#questionId').val();
    const isNewQuestion = !questionId;
    
    const questionData = {
        quiz_id: $('#questionQuiz').val(),
        text: $('#questionText').val(),
        option1: $('#option1').val(),
        option2: $('#option2').val(),
        option3: $('#option3').val(),
        option4: $('#option4').val(),
        correct_option: $('#correctOption').val()
    };
    
    if (questionId) {
        questionData.id = questionId;
    }
    
    // Send request
    const url = isNewQuestion ? '/question/add/' : '/question/update/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(questionData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            $('#questionModal').modal('hide');
            showAlert('success', isNewQuestion ? 'Question added successfully!' : 'Question updated successfully!');
            location.reload();
        } else {
            showAlert('danger', 'Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while saving question data.');
    });
});

// Handle delete question button
let questionIdToDelete;
let questionTextToDelete;

$(document).on('click', '.delete-question', function() {
    questionIdToDelete = $(this).data('id');
    // Get the question text from the table row
    questionTextToDelete = $(this).closest('tr').find('td:nth-child(3)').text();
    $('#questionToDelete').text(questionTextToDelete);
    $('#deleteQuestionModal').modal('show');
});

// Handle confirm delete question button
$('#confirmDeleteQuestionBtn').on('click', function() {
    fetch(`/question/delete/${questionIdToDelete}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            $('#deleteQuestionModal').modal('hide');
            showAlert('success', 'Question deleted successfully!');
            location.reload();
        } else {
            showAlert('danger', 'Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while deleting the question.');
    });
});

    // USERS MANAGEMENT
    // Initialize DataTable for users
    const userTable = $('#users-table').DataTable({
        responsive: true,
        columnDefs: [
            { orderable: false, targets: -1 } // Disable ordering on action column
        ],
        order: [[0, 'asc']], // Sort by ID by default
        pageLength: 10, // Show 10 entries per page
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]]
    });
    
    // Handle add user button
    $('#add-user-btn').on('click', function() {
        // Clear form
        $('#userForm')[0].reset();
        $('#userId').val('');
        $('#modalTitle').text('Add New User');
        $('.password-field small').text('Password is required for new users.');
        $('#password').attr('required', true);
        $('#userModal').modal('show');
    });
    
    // Handle edit user button
    $(document).on('click', '.edit-user', function() {
        const userId = $(this).data('id');
        $('#userId').val(userId);
        $('#modalTitle').text('Edit User');
        $('.password-field small').text('Leave blank to keep current password.');
        $('#password').removeAttr('required');
        
        // Fetch user details
        fetch(`/get_user/${userId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const user = data.user;
                $('#firstName').val(user.first_name);
                $('#lastName').val(user.last_name);
                $('#email').val(user.email);
                $('#contactNumber').val(user.contact_number);
                $('#dateOfBirth').val(user.date_of_birth);
                $('#skills').val(user.skills);
                $('#interests').val(user.interests);
                $('#password').val('');
                $('#userModal').modal('show');
            } else {
                showAlert('danger', 'Error fetching user details: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while fetching user details.');
        });
    });
    
    // Handle save user button
    $('#saveUserBtn').on('click', function() {
        // Validate form
        if (!$('#userForm')[0].checkValidity()) {
            $('#userForm')[0].reportValidity();
            return;
        }
        
        const userId = $('#userId').val();
        const userData = {
            first_name: $('#firstName').val(),
            last_name: $('#lastName').val(),
            email: $('#email').val(),
            contact_number: $('#contactNumber').val(),
            date_of_birth: $('#dateOfBirth').val(),
            skills: $('#skills').val(),
            interests: $('#interests').val()
        };
        
        if ($('#password').val()) {
            userData.password = $('#password').val();
        }
        
        if (userId) {
            userData.id = userId;
        }
        
        // Send request
        const url = userId ? '/user/update/' : '/user/add/';
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#userModal').modal('hide');
                showAlert('success', userId ? 'User updated successfully!' : 'User added successfully!');
                location.reload();
            } else {
                showAlert('danger', 'Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while saving user data.');
        });
    });
    
    // Handle delete user button
    let userIdToDelete;
    $(document).on('click', '.delete-user', function() {
        userIdToDelete = $(this).data('id');
        $('#deleteModal').modal('show');
    });
    
    // Handle confirm delete button
    $('#confirmDeleteBtn').on('click', function() {
        fetch(`/user/delete/${userIdToDelete}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#deleteModal').modal('hide');
                showAlert('success', 'User deleted successfully!');
                location.reload();
            } else {
                showAlert('danger', 'Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while deleting the user.');
        });
    });

    // Form validation
    $('#userForm input').on('input', function() {
        this.setCustomValidity('');
        this.checkValidity();
    });

    // Custom validation messages
    $('#userForm input').on('invalid', function() {
        if (!this.validity.valid) {
            if (this.validity.valueMissing) {
                this.setCustomValidity('This field is required');
            } else if (this.validity.typeMismatch) {
                this.setCustomValidity('Please enter a valid value');
            }
        }
    });

    // COURSES MANAGEMENT 
    // Initialize DataTable for courses
    const courseTable = $('#courses-table').DataTable({
        responsive: true,
        columnDefs: [
            { orderable: false, targets: [3, 6] } // Disable ordering on image and action columns
        ],
        order: [[0, 'asc']], // Sort by ID by default
        pageLength: 10
    });
    
    // Handle add course button
    $('#add-course-btn').on('click', function() {
        // Clear form
        $('#courseForm')[0].reset();
        $('#courseId').val('');
        $('#courseModalTitle').text('Add New Course');
        $('#currentImageContainer').addClass('d-none');
        $('#courseImage').attr('required', true);
        $('#courseModal').modal('show');
    });
    
    // Handle edit course button
    $(document).on('click', '.edit-course', function() {
        const courseId = $(this).data('id');
        $('#courseId').val(courseId);
        $('#courseModalTitle').text('Edit Course');
        $('#courseImage').removeAttr('required');
        
        // Fetch course details
        fetch(`/get_course/${courseId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const course = data.course;
                $('#courseTitle').val(course.title);
                $('#courseDescription').val(course.description);
                $('#courseStatus').val(course.is_active.toString());
                $('#courseRoadmap').val(course.roadmap_link);
                //$('#courseEnrollment').val(course.enrollment_link);
                
                // Handle image display
                if (course.image_url) {
                    $('#currentImageContainer').removeClass('d-none');
                    $('#currentImage').attr('src', course.image_url);
                } else {
                    $('#currentImageContainer').addClass('d-none');
                }
                
                $('#courseModal').modal('show');
            } else {
                showAlert('danger', 'Error fetching course details: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while fetching course details.');
        });
    });
    
    // Handle save course button
    $('#saveCourseBtn').on('click', function() {
        // Validate form
        if (!$('#courseForm')[0].checkValidity()) {
            $('#courseForm')[0].reportValidity();
            return;
        }
        
        const courseId = $('#courseId').val();
        const isNewCourse = !courseId;
        
        // Create FormData object to handle file uploads
        const formData = new FormData();
        formData.append('title', $('#courseTitle').val());
        formData.append('description', $('#courseDescription').val());
        formData.append('is_active', $('#courseStatus').val());
        formData.append('roadmap_link', $('#courseRoadmap').val());
        //formData.append('enrollment_link', $('#courseEnrollment').val());
        
        // Add course image if provided
        const courseImageInput = document.getElementById('courseImage');
        if (courseImageInput.files.length > 0) {
            formData.append('image', courseImageInput.files[0]);
        }
        
        if (courseId) {
            formData.append('id', courseId);
        }
        
        // Send request
        const url = isNewCourse ? '/course/add/' : '/course/update/';
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#courseModal').modal('hide');
                showAlert('success', isNewCourse ? 'Course added successfully!' : 'Course updated successfully!');
                location.reload();
            } else {
                showAlert('danger', 'Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while saving course data.');
        });
    });
    
    // Handle delete course button
    let courseIdToDelete;
    let courseTitleToDelete;
    
    $(document).on('click', '.delete-course', function() {
        courseIdToDelete = $(this).data('id');
        // Get the course title from the table row
        courseTitleToDelete = $(this).closest('tr').find('td:nth-child(2)').text();
        $('#courseToDelete').text(courseTitleToDelete);
        $('#deleteCourseModal').modal('show');
    });
    
    // Handle confirm delete button
    $('#confirmDeleteCourseBtn').on('click', function() {
        fetch(`/course/delete/${courseIdToDelete}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#deleteCourseModal').modal('hide');
                showAlert('success', 'Course deleted successfully!');
                location.reload();
            } else {
                showAlert('danger', 'Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while deleting the course.');
        });
    });

    // QUIZZES MANAGEMENT
    // Initialize DataTable for quizzes
    const quizzesTable = $('#quizzes-table').DataTable({
        responsive: true,
        columnDefs: [
            { orderable: false, targets: [5] } // Disable ordering on action column (now index 5)
        ],
        order: [[0, 'asc']], // Sort by ID by default
        pageLength: 10
    });

    // Handle add quiz button
    $('#add-quiz-btn').on('click', function() {
        // Clear form
        $('#quizForm')[0].reset();
        $('#quizId').val('');
        $('#quizModalTitle').text('Add New Quiz');
        $('#quizModal').modal('show');
    });

    // Handle edit quiz button
    $(document).on('click', '.edit-quiz', function() {
        const quizId = $(this).data('id');
        $('#quizId').val(quizId);
        $('#quizModalTitle').text('Edit Quiz');
        
        // Fetch quiz details
        fetch(`/get_quiz/${quizId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const quiz = data.quiz;
                $('#quizTitle').val(quiz.title);
                $('#quizCourse').val(quiz.course_id);
                $('#quizDuration').val(quiz.duration);
                $('#quizDescription').val(quiz.description);
                $('#quizModal').modal('show');
            } else {
                showAlert('danger', 'Error fetching quiz details: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while fetching quiz details.');
        });
    });

    // Handle save quiz button
    $('#saveQuizBtn').on('click', function() {
        // Validate form
        if (!$('#quizForm')[0].checkValidity()) {
            $('#quizForm')[0].reportValidity();
            return;
        }
        
        const quizId = $('#quizId').val();
        const isNewQuiz = !quizId;
        
        const quizData = {
            title: $('#quizTitle').val(),
            course_id: $('#quizCourse').val(),
            duration: $('#quizDuration').val(),
            description: $('#quizDescription').val()
        };
        
        if (quizId) {
            quizData.id = quizId;
        }
        
        // Send request
        const url = isNewQuiz ? '/quiz/add/' : '/quiz/update/';
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(quizData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#quizModal').modal('hide');
                showAlert('success', isNewQuiz ? 'Quiz added successfully!' : 'Quiz updated successfully!');
                location.reload();
            } else {
                showAlert('danger', 'Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while saving quiz data.');
        });
    });

    // Handle delete quiz button
    let quizIdToDelete;
    let quizTitleToDelete;
    
    $(document).on('click', '.delete-quiz', function() {
        quizIdToDelete = $(this).data('id');
        // Get the quiz title from the table row
        quizTitleToDelete = $(this).closest('tr').find('td:nth-child(2)').text();
        $('#quizToDelete').text(quizTitleToDelete);
        $('#deleteQuizModal').modal('show');
    });
    
    // Handle confirm delete quiz button
    $('#confirmDeleteQuizBtn').on('click', function() {
        fetch(`/quiz/delete/${quizIdToDelete}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#deleteQuizModal').modal('hide');
                showAlert('success', 'Quiz deleted successfully!');
                location.reload();
            } else {
                showAlert('danger', 'Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while deleting the quiz.');
        });
    });
}); 

// Initialize charts function
function initializeQuizPerformanceCharts() {
    console.log('Initializing charts...');
    
    // Make sure the charts container exists
    if ($('#dashboard-tab .dashboard-section .dashboard-stats .row').length === 0) {
        // Create the row container if it doesn't exist
        $('#dashboard-tab .dashboard-section:last').append(`
            <div class="dashboard-stats mt-4">
                <div class="row">
                    <!-- Charts will be inserted here -->
                </div>
            </div>
        `);
    }
    
    // Check if Chart is defined
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library is not loaded');
        showAlert('danger', 'Failed to load charting library. Please refresh the page.');
        return;
    }
    
    // Fetch quiz performance data from the server
    fetch('/quiz-performance-data/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
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
        console.log('Data received:', data);
        createAverageScoresChart(data.average_scores);
        createPassRateChart(data.pass_rate_trend);
        createPassFailChart(data.pass_fail_percentage);
        createTopAttemptedQuizzesChart(data.top_attempted_quizzes);
    })
    .catch(error => {
        console.error('Error fetching quiz performance data:', error);
        // Use fallback data
        console.log('Using fallback data for charts');
        createAverageScoresChart();
        createPassRateChart();
        createPassFailChart();
        createTopAttemptedQuizzesChart();
        showAlert('warning', 'Using sample data for charts. Actual quiz data could not be loaded.');
    });
}

function createAverageScoresChart(data) {
    // Clear any existing chart
    $('#averageScoresChart').remove();
    
    // If canvas doesn't exist yet, create it
    const chartContainer = $('#dashboard-tab .dashboard-section:last .dashboard-stats .row');
    chartContainer.append(`
        <div class="col-md-6 mt-4">
            <div class="card">
                <div class="card-header">
                    <h5>Average Quiz Scores by Course</h5>
                </div>
                <div class="card-body">
                    <canvas id="averageScoresChart"></canvas>
                </div>
            </div>
        </div>
    `);
    
    // For demonstration, create sample data if none provided
    if (!data || !data.labels || !data.scores || data.labels.length === 0) {
        data = {
            labels: ['Web Development', 'Data Science', 'UI/UX Design', 'Digital Marketing', 'Mobile App Dev'],
            scores: [78.5, 82.3, 75.1, 68.9, 80.2]
        };
    }
    
    const ctx = document.getElementById('averageScoresChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Score (%)',
                data: data.scores,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Average Score (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Course'
                    }
                }
            }
        }
    });
}

function createPassRateChart(data) {
    // Clear any existing chart
    $('#passRateChart').remove();
    
    // If canvas doesn't exist yet, create it
    const chartContainer = $('#dashboard-tab .dashboard-section:last .dashboard-stats .row');
    chartContainer.append(`
        <div class="col-md-6 mt-4">
            <div class="card">
                <div class="card-header">
                    <h5>Quiz Pass Rate Trend</h5>
                </div>
                <div class="card-body">
                    <canvas id="passRateChart"></canvas>
                </div>
            </div>
        </div>
    `);
    
    // For demonstration, create sample data if none provided
    if (!data || !data.labels || !data.passRates || data.labels.length === 0) {
        data = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            passRates: [65, 70, 68, 75, 78, 82]
        };
    }
    
    const ctx = document.getElementById('passRateChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Pass Rate (%)',
                data: data.passRates,
                fill: false,
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.1,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Pass Rate (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            }
        }
    });
}

function createPassFailChart(data) {
    // Clear any existing chart
    $('#passFailChart').remove();
    
    // If canvas doesn't exist yet, create it
    const chartContainer = $('#dashboard-tab .dashboard-section:last .dashboard-stats .row');
    chartContainer.append(`
        <div class="col-md-6 mt-4">
            <div class="card">
                <div class="card-header">
                    <h5>Quiz Pass/Fail Distribution</h5>
                </div>
                <div class="card-body">
                    <canvas id="passFailChart" style="max-height: 250px;"></canvas>
                </div>
            </div>
        </div>
    `);
    
    // For demonstration, create sample data if none provided
    if (!data || !data.passed === undefined || data.failed === undefined) {
        data = {
            passed: 72,
            failed: 28
        };
    }
    
    const ctx = document.getElementById('passFailChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Passed', 'Failed'],
            datasets: [{
                data: [data.passed, data.failed],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.raw + '%';
                        }
                    }
                }
            }
        }
    });
}

function createTopAttemptedQuizzesChart(data) {
    // Clear any existing chart
    $('#topAttemptedQuizzesChart').remove();
    
    // If canvas doesn't exist yet, create it
    const chartContainer = $('#dashboard-tab .dashboard-section:last .dashboard-stats .row');
    chartContainer.append(`
        <div class="col-md-6 mt-4">
            <div class="card">
                <div class="card-header">
                    <h5>Top 5 Most Attempted Quizzes</h5>
                </div>
                <div class="card-body">
                    <canvas id="topAttemptedQuizzesChart"></canvas>
                </div>
            </div>
        </div>
    `);
    
    // For demonstration, create sample data if none provided
    if (!data || !data.labels || !data.attempts || data.labels.length === 0) {
        data = {
            labels: ['Web Dev Basics', 'Data Science Intro', 'UI/UX Fundamentals', 'Digital Marketing', 'Python Essentials'],
            attempts: [45, 38, 32, 28, 24]
        };
    }
    
    // Sort data to display in ascending order (for horizontal bar chart)
    const sortedData = [...Array(data.labels.length).keys()]
        .map(i => ({ label: data.labels[i], value: data.attempts[i] }))
        .sort((a, b) => a.value - b.value);
    
    // Define an array of colors for the bars
    const backgroundColors = [
        'rgba(255, 99, 132, 0.7)',   // Red
        'rgba(54, 162, 235, 0.7)',   // Blue
        'rgba(255, 206, 86, 0.7)',   // Yellow
        'rgba(75, 192, 192, 0.7)',   // Green
        'rgba(153, 102, 255, 0.7)',  // Purple
        'rgba(255, 159, 64, 0.7)',   // Orange
        'rgba(199, 199, 199, 0.7)'   // Grey
    ];
    
    const borderColors = [
        'rgba(255, 99, 132, 1)',     // Red
        'rgba(54, 162, 235, 1)',     // Blue
        'rgba(255, 206, 86, 1)',     // Yellow
        'rgba(75, 192, 192, 1)',     // Green
        'rgba(153, 102, 255, 1)',    // Purple
        'rgba(255, 159, 64, 1)',     // Orange
        'rgba(199, 199, 199, 1)'     // Grey
    ];
    
    // Generate backgroundColor and borderColor arrays based on the number of bars
    const bgColors = sortedData.map((_, index) => backgroundColors[index % backgroundColors.length]);
    const bdColors = sortedData.map((_, index) => borderColors[index % borderColors.length]);
    
    const ctx = document.getElementById('topAttemptedQuizzesChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(item => item.label),
            datasets: [{
                label: 'Number of Attempts',
                data: sortedData.map(item => item.value),
                backgroundColor: bgColors,
                borderColor: bdColors,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',  // Horizontal bar chart
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Attempts: ' + context.raw;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Attempts'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Quiz Title'
                    }
                }
            }
        }
    });
}

        // Also update the refreshRecentActivities function in JavaScript
        function refreshRecentActivities() {
            $.ajax({
                url: '/get-recent-activities/',
                method: 'GET',
                success: function(data) {
                    // Update the activities list
                    let activitiesList = '';
                    
                    if (data.activities.length > 0) {
                        data.activities.forEach(function(activity) {
                            activitiesList += `<li class="list-group-item">${activity.description} <small class="text-muted">${activity.time_ago} ago</small></li>`;
                        });
                    } else {
                        activitiesList = '<li class="list-group-item">No recent activities found</li>';
                    }
                    
                    $('.activities-container ul.list-group').html(activitiesList);
                },
                error: function(error) {
                    console.error('Error fetching activities:', error);
                }
            });
        }