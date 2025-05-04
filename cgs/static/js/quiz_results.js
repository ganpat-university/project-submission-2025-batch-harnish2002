// static/js/quiz_results.js
document.addEventListener('DOMContentLoaded', () => {
    // Set progress bar widths dynamically
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const score = parseFloat(bar.getAttribute('data-score'));
        bar.style.width = `${score}%`;
    });
});