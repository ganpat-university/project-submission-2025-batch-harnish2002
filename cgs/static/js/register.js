document.addEventListener('DOMContentLoaded', function() {
    const skillsSelect = document.getElementById('skills_select');
    const interestsSelect = document.getElementById('interests_select');
    const selectedSkills = document.getElementById('selected_skills');
    const selectedInterests = document.getElementById('selected_interests');
    const form = document.getElementById('registrationForm');

    // Store selected items
    const selectedSkillsArray = [];
    const selectedInterestsArray = [];

    // Handle skills selection
    skillsSelect.addEventListener('change', function() {
        const selectedSkill = this.value;
        if (selectedSkill && !selectedSkillsArray.includes(selectedSkill)) {
            selectedSkillsArray.push(selectedSkill);
            addTag(selectedSkill, 'skill', selectedSkills, selectedSkillsArray);
            this.value = ''; // Reset select
        }
    });

    // Handle interests selection
    interestsSelect.addEventListener('change', function() {
        const selectedInterest = this.value;
        if (selectedInterest && !selectedInterestsArray.includes(selectedInterest)) {
            selectedInterestsArray.push(selectedInterest);
            addTag(selectedInterest, 'interest', selectedInterests, selectedInterestsArray);
            this.value = ''; // Reset select
        }
    });

    // Function to create and add tags
    function addTag(text, type, container, array) {
        const tag = document.createElement('div');
        tag.className = `selected-tag ${type}`;
        
        const tagText = document.createElement('span');
        tagText.textContent = text;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'remove-tag';
        removeButton.innerHTML = '×';
        removeButton.onclick = function() {
            container.removeChild(tag);
            const index = array.indexOf(text);
            if (index > -1) {
                array.splice(index, 1);
            }
        };

        tag.appendChild(tagText);
        tag.appendChild(removeButton);
        container.appendChild(tag);
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearErrors(); // Clear previous errors

        let isValid = true;

        // Validate First Name
        const firstName = document.getElementById('first_name').value;
        if (!firstName) {
            showError('first_name_error', 'First Name is required.');
            isValid = false;
        }

        // Validate Last Name
        const lastName = document.getElementById('last_name').value;
        if (!lastName) {
            showError('last_name_error', 'Last Name is required.');
            isValid = false;
        }

        // Validate Email
        const email = document.getElementById('email').value;
        if (!validateEmail(email)) {
            showError('email_error', 'Please enter a valid email address.');
            isValid = false;
        }

        // Validate Date of Birth
        const dateOfBirth = document.getElementById('date_of_birth').value;
        if (!dateOfBirth) {
            showError('date_of_birth_error', 'Date of Birth is required.');
            isValid = false;
        }

        // Validate Contact Number
        const contactNumber = document.getElementById('contact_number').value;
        if (!contactNumber) {
            showError('contact_number_error', 'Contact Number is required.');
            isValid = false;
        }

        // Validate Skills
        if (selectedSkillsArray.length === 0) {
            showError('skills_error', 'Please select at least one skill.');
            isValid = false;
        }

        // Validate Interests
        if (selectedInterestsArray.length === 0) {
            showError('interests_error', 'Please select at least one interest.');
            isValid = false;
        }

        // Validate Password
        const password = document.getElementById('password').value;
        const passwordError = validatePassword(password);
        if (passwordError) {
            showError('password_error', passwordError);
            isValid = false;
        }

        // Validate Confirm Password
        const confirmPassword = document.getElementById('confirm_password').value;
        if (password !== confirmPassword) {
            showError('confirm_password_error', 'Passwords do not match.');
            isValid = false;
        }

        // Validate Terms and Conditions
        const termsAccepted = document.getElementById('terms_accepted').checked;
        if (!termsAccepted) {
            showError('terms_error', 'You must accept the terms and conditions.');
            isValid = false;
        }

        if (isValid) {
            // Convert arrays to comma-separated strings
            const skills = selectedSkillsArray.join(', ');
            const interests = selectedInterestsArray.join(', ');

            const formData = {
                first_name: firstName,
                last_name: lastName,
                email: email,
                date_of_birth: dateOfBirth,
                contact_number: contactNumber,
                skills: skills,
                interests: interests,
                password: password,
                confirm_password: confirmPassword,
                terms_accepted: termsAccepted
            };

            try {
                const response = await fetch('/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    if (data.require_otp) {
                        // Store form data in session storage
                        sessionStorage.setItem('registrationEmail', email);
                        
                        // Redirect to OTP verification page
                        window.location.href = `/otp_verification/?email=${encodeURIComponent(email)}&purpose=register`;
                    } else {
                        alert(data.message);
                        window.location.href = '/login/';
                    }
                } else {
                    if (data.error.includes('Email already exists')) {
                        showError('email_error', data.error);
                    } else if (data.error.includes('Contact number already exists')) {
                        showError('contact_number_error', data.error);
                    } else {
                        showError('form_error', data.error);
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                showError('form_error', 'An error occurred. Please try again.');
            }
        }
    });

    // Function to show error messages
    function showError(id, message) {
        const errorElement = document.getElementById(id);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    // Function to clear all error messages
    function clearErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(element => {
            element.textContent = '';
            element.style.display = 'none';
        });
    }

    // Function to validate email
    function validateEmail(email) {
        if (!email) return false;
        if (!email.includes('@')) return false;
        if (email.indexOf('@') !== email.lastIndexOf('@')) return false;
        const [localPart, domain] = email.split('@');
        if (!localPart || !domain) return false;
        if (!domain.includes('.')) return false;
        if (domain.split('.').length < 2) return false;
        return true;
    }

    // Function to validate password
    function validatePassword(password) {
        if (password.length < 8) return 'Password must be at least 8 characters long.';
        if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter.';
        if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter.';
        if (!/[0-9]/.test(password)) return 'Password must contain at least one number.';
        if (!/[!@#$%^&*]/.test(password)) return 'Password must contain at least one special character (!@#$%^&*).';
        return null; // No error
    }

    // Function to get CSRF token from cookies
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