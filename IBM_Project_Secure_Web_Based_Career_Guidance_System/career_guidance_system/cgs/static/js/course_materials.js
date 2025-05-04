// course_materials.js - Enhanced with better content index navigation
document.addEventListener('DOMContentLoaded', function() {
    
    // Pagination variables
    let currentPage = 0;
    const materialCards = document.querySelectorAll('.material-card');
    const totalPages = materialCards.length;
    
    // Initialize pagination
    initPagination();
    showPage(0); // Show the first page by default
    
    // Initialize material index with improved navigation
    initMaterialIndex();
    
    // Handle marking materials as completed
    const completedButtons = document.querySelectorAll('.mark-completed-btn');
    
    completedButtons.forEach(button => {
        button.addEventListener('click', function() {
            markCurrentPageAsCompleted(this);
        });
    });
    
    // Function to initialize the material index with improved navigation
    function initMaterialIndex() {
        const indexItems = document.querySelectorAll('.material-index-item');
        
        indexItems.forEach(item => {
            item.addEventListener('click', function() {
                const targetPage = parseInt(this.getAttribute('data-page'));
                
                // Highlight the clicked item visually before navigation
                highlightIndexItem(this);
                
                // Navigate to the selected page
                showPage(targetPage);
                
                // Scroll to the beginning of the material for better visibility
                scrollToMaterial(targetPage);
            });
        });
        
        // Set the first item as active by default
        updateIndexActiveState();
    }
    
    // Function to highlight the clicked index item
    function highlightIndexItem(item) {
        // Remove active class from all items
        document.querySelectorAll('.material-index-item').forEach(el => {
            el.classList.remove('active');
        });
        
        // Add active class to clicked item
        item.classList.add('active');
    }
    
    // Function to scroll to the material card
    function scrollToMaterial(pageIndex) {
        // Scroll to the material card with smooth behavior
        const materialCard = materialCards[pageIndex];
        if (materialCard) {
            materialCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    // Function to update the active state in the index
    function updateIndexActiveState() {
        const indexItems = document.querySelectorAll('.material-index-item');
        
        indexItems.forEach((item, index) => {
            if (index === currentPage) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    // Function to initialize pagination
    function initPagination() {
        // Create pagination container if it doesn't exist
        if (!document.getElementById('pagination-container')) {
            // Create pagination container
            const paginationContainer = document.createElement('div');
            paginationContainer.id = 'pagination-container';
            paginationContainer.className = 'pagination-container d-flex justify-content-center align-items-center my-4';
            
            // Add container before the buttons at the bottom
            const bottomButtons = document.querySelector('.text-center.mt-4');
            bottomButtons.parentNode.insertBefore(paginationContainer, bottomButtons);
            
            // Create the pagination HTML
            createPaginationControls();
        }
        
        // Hide all material cards initially
        materialCards.forEach(card => {
            card.style.display = 'none';
            
            // Make sure all cards are expanded by default
            const collapseElement = card.querySelector('[data-bs-toggle="collapse"]');
            if (collapseElement) {
                const collapseId = collapseElement.getAttribute('data-bs-target');
                const collapseElement = document.querySelector(collapseId);
                if (collapseElement) {
                    collapseElement.classList.add('show');
                }
            }
        });
        
        // Add page title/counter above the materials
        const materialsContainer = document.querySelector('.material-card').parentNode;
        const pageCounter = document.createElement('div');
        pageCounter.id = 'page-counter';
        pageCounter.className = 'page-counter text-center mb-3';
        pageCounter.innerHTML = `<h4>Material <span id="current-page-number">1</span> of ${totalPages}</h4>`;
        
        // Insert the page counter before the first material card
        materialsContainer.insertBefore(pageCounter, materialsContainer.firstChild);
        
        // Update pagination buttons status
        updatePaginationStatus();
    }
    
    // Function to create pagination controls
    function createPaginationControls() {
        const paginationContainer = document.getElementById('pagination-container');
        
        // Create Previous button
        const prevButton = document.createElement('button');
        prevButton.id = 'prev-page';
        prevButton.className = 'btn btn-outline-primary me-2';
        prevButton.innerHTML = '<i class="fas fa-chevron-left me-1"></i> Previous';
        prevButton.addEventListener('click', () => navigatePage(-1));
        
        // Create Next button
        const nextButton = document.createElement('button');
        nextButton.id = 'next-page';
        nextButton.className = 'btn btn-outline-primary ms-2';
        nextButton.innerHTML = 'Next <i class="fas fa-chevron-right ms-1"></i>';
        nextButton.addEventListener('click', () => {
            // Auto-mark current page as completed when clicking next
            const currentCard = materialCards[currentPage];
            const completeButton = currentCard.querySelector('.mark-completed-btn');
            
            // Only auto-complete if not already completed and moving forward
            if (completeButton && !completeButton.disabled) {
                markCurrentPageAsCompleted(completeButton, () => {
                    // After completion, navigate to next page
                    navigatePage(1);
                });
            } else {
                // If already completed, just navigate
                navigatePage(1);
            }
        });
        
        // Create Complete Course button for the last page
        const completeButton = document.createElement('button');
        completeButton.id = 'complete-course';
        completeButton.className = 'btn btn-success ms-2 d-none';
        completeButton.innerHTML = '<i class="fas fa-flag-checkered me-1"></i> Complete Course';
        completeButton.addEventListener('click', () => {
            // Mark last page as completed
            const lastCard = materialCards[totalPages - 1];
            const lastCompleteButton = lastCard.querySelector('.mark-completed-btn');
            
            if (lastCompleteButton && !lastCompleteButton.disabled) {
                markCurrentPageAsCompleted(lastCompleteButton);
            }
        });
        
        // Create page number buttons container
        const pageNumbers = document.createElement('div');
        pageNumbers.className = 'page-numbers mx-2';
        
        // Add page number buttons
        for (let i = 0; i < totalPages; i++) {
            const pageButton = document.createElement('button');
            pageButton.className = 'btn btn-outline-secondary mx-1 page-number-btn';
            pageButton.setAttribute('data-page', i);
            pageButton.textContent = i + 1;
            
            // Check if this material is completed
            const materialCard = materialCards[i];
            if (materialCard.querySelector('.completed-icon')) {
                pageButton.classList.add('btn-success');
                pageButton.classList.remove('btn-outline-secondary');
            }
            
            pageButton.addEventListener('click', function() {
                const targetPage = parseInt(this.getAttribute('data-page'));
                
                // Simply navigate to the page without auto-completion
                showPage(targetPage);
                
                // Update the index to show which item is selected
                updateIndexActiveState();
            });
            
            pageNumbers.appendChild(pageButton);
        }
        
        // Add all elements to the pagination container
        paginationContainer.appendChild(prevButton);
        paginationContainer.appendChild(pageNumbers);
        paginationContainer.appendChild(nextButton);
        paginationContainer.appendChild(completeButton);
    }
    
    // Function to mark current page as completed
    function markCurrentPageAsCompleted(button, callback) {
        const materialId = button.getAttribute('data-material-id');
        
        // Disable button to prevent multiple clicks
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        
        fetch(`/course/material/${materialId}/complete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update button appearance
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
                button.innerHTML = '<i class="fas fa-check me-2"></i>Completed';
                
                // Add completed icon
                const headerElement = button.closest('.material-card').querySelector('.material-header h5');
                if (!headerElement.querySelector('.completed-icon')) {
                    const icon = document.createElement('i');
                    icon.className = 'fas fa-check-circle completed-icon';
                    headerElement.appendChild(icon);
                }
                
                // Add progress bar at bottom
                const card = button.closest('.material-card');
                let progressBar = card.querySelector('.material-progress');
                if (!progressBar) {
                    progressBar = document.createElement('div');
                    progressBar.className = 'material-progress';
                    card.appendChild(progressBar);
                }
                progressBar.style.width = '0%';
                setTimeout(() => {
                    progressBar.style.width = '100%';
                    progressBar.style.transition = 'width 0.5s ease-in-out';
                }, 50);
                
                // Update overall progress
                updateProgress(data.completed_count, data.total_materials);
                
                // Update pagination display to show completed status
                updatePaginationStatus();
                
                // Update index to show completed status
                const indexItem = document.querySelector(`.material-index-item[data-page="${currentPage}"]`);
                if (indexItem) {
                    indexItem.classList.add('completed');
                    // Force a refresh of the element to ensure styles are applied
                    indexItem.offsetHeight; // This triggers a reflow
                }
                
                // Execute callback if provided (used for navigation after completion)
                if (typeof callback === 'function') {
                    callback();
                }
            } else {
                // Restore button if error
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-check me-2"></i>Mark as Completed';
                alert('Error updating progress: ' + data.error);
                
                // Don't execute callback on error
            }
        })
        .catch(error => {
            console.error('Error:', error);
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-check me-2"></i>Mark as Completed';
            alert('Error updating progress. Please try again.');
            
            // Don't execute callback on error
        });
    }
    
    // Function to navigate between pages
    function navigatePage(direction) {
        const newPage = currentPage + direction;
        if (newPage >= 0 && newPage < totalPages) {
            showPage(newPage);
        }
    }
    
    // Function to show a specific page
    function showPage(pageIndex) {
        // Hide all material cards
        materialCards.forEach(card => {
            card.style.display = 'none';
        });
        
        // Show only the current page
        materialCards[pageIndex].style.display = 'block';
        
        // Update current page variable
        currentPage = pageIndex;
        
        // Update the current page number display
        document.getElementById('current-page-number').textContent = pageIndex + 1;
        
        // Update pagination buttons active state
        updatePaginationActive();
        
        // Update prev/next button states
        updatePrevNextButtons();
        
        // Update the index active state
        updateIndexActiveState();
        
        // Show/hide complete course button on last page
        toggleCompleteButton();
    }
    
    // Function to toggle the complete course button visibility
    function toggleCompleteButton() {
        const completeButton = document.getElementById('complete-course');
        if (!completeButton) return;
        
        const isLastPage = currentPage === totalPages - 1;
        const currentCard = materialCards[currentPage];
        const completeButtonInCard = currentCard.querySelector('.mark-completed-btn');
        const isAlreadyCompleted = completeButtonInCard && completeButtonInCard.disabled;
        
        if (isLastPage && !isAlreadyCompleted) {
            completeButton.classList.remove('d-none');
        } else {
            completeButton.classList.add('d-none');
        }
    }
    
    // Function to update the prev/next button states
    function updatePrevNextButtons() {
        const prevButton = document.getElementById('prev-page');
        const nextButton = document.getElementById('next-page');
        
        // Update previous button
        if (currentPage === 0) {
            prevButton.disabled = true;
        } else {
            prevButton.disabled = false;
        }
        
        // Update next button
        if (currentPage === totalPages - 1) {
            nextButton.disabled = true;
            
            // Add a "Mark Complete" prompt if the last page isn't completed yet
            const lastCard = materialCards[totalPages - 1];
            const completeButton = lastCard.querySelector('.mark-completed-btn');
            
            if (completeButton && !completeButton.disabled) {
                const pageCounter = document.getElementById('page-counter');
                if (pageCounter && !document.getElementById('last-page-prompt')) {
                    const prompt = document.createElement('div');
                    prompt.id = 'last-page-prompt';
                    prompt.className = 'alert alert-info mt-2';
                    prompt.innerHTML = '<i class="fas fa-info-circle me-2"></i>This is the last page. Don\'t forget to mark it as completed!';
                    pageCounter.after(prompt);
                }
            }
        } else {
            nextButton.disabled = false;
            // Remove the "Mark Complete" prompt if we're not on the last page
            const prompt = document.getElementById('last-page-prompt');
            if (prompt) {
                prompt.remove();
            }
        }
    }
    
    // Function to update the active state of pagination buttons
    function updatePaginationActive() {
        const pageButtons = document.querySelectorAll('.page-number-btn');
        
        pageButtons.forEach((btn, index) => {
            // First remove the active class from all buttons
            btn.classList.remove('active');
            
            // If this button represents the current page, add the active class
            if (index === currentPage) {
                btn.classList.add('active');
                btn.classList.add('btn-primary');
                btn.classList.remove('btn-outline-secondary');
            } else if (!btn.classList.contains('btn-success')) {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-secondary');
            }
        });
    }
    
    // Function to update the pagination buttons to reflect completion status
    function updatePaginationStatus() {
        const pageButtons = document.querySelectorAll('.page-number-btn');
        
        materialCards.forEach((card, index) => {
            const isCompleted = card.querySelector('.completed-icon') !== null;
            const button = pageButtons[index];
            
            if (isCompleted) {
                button.classList.add('btn-success');
                button.classList.remove('btn-outline-secondary');
                button.classList.remove('btn-primary');
                // Add a check icon to the button
                if (!button.querySelector('.fa-check')) {
                    const checkIcon = document.createElement('i');
                    checkIcon.className = 'fas fa-check ms-1';
                    button.appendChild(checkIcon);
                }
            }
        });
        
        // Also update the complete button visibility if we're on the last page
        toggleCompleteButton();
    }
    
    // Function to update overall progress
    function updateProgress(completedCount, totalMaterials) {
        const progressPercentage = (completedCount / totalMaterials) * 100;
        const progressBar = document.querySelector('.course-progress-bar');
        const progressBadge = document.querySelector('.progress-container .badge');
        
        progressBar.style.width = progressPercentage + '%';
        progressBar.setAttribute('aria-valuenow', progressPercentage);
        progressBadge.textContent = `${completedCount}/${totalMaterials} Completed`;
        
        // If all materials completed, show congratulation
        if (completedCount === totalMaterials) {
            const container = document.querySelector('.card-body');
            
            // Check if congratulation alert already exists
            if (!document.querySelector('.alert-success')) {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success mt-3 mb-3 fade-in';
                alertDiv.innerHTML = `
                    <i class="fas fa-thumbs-up fa-2x float-start me-3"></i>
                    <h4 class="alert-heading">Great job!</h4>
                    <p>You've completed all the materials in this course. You're now better prepared to retake the quiz!</p>
                `;
                
                // Insert after the info alert
                const infoAlert = document.querySelector('.alert-info');
                infoAlert.insertAdjacentElement('afterend', alertDiv);
            }
            
            // Remove the last page prompt if it exists
            const prompt = document.getElementById('last-page-prompt');
            if (prompt) {
                prompt.remove();
            }
        }
    }
    
    // Function to get CSRF cookie
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