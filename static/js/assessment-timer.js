// Assessment Timer Management System
class AssessmentTimer {
    constructor() {
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.timers = new Map();
        this.totalTimeLimit = 0;
        this.overallTimer = null;
        this.isAssessmentActive = false;
        
        this.initializeQuestions();
        this.setupEventListeners();
    }
    
    initializeQuestions() {
        document.querySelectorAll('.assessment-question').forEach((element, index) => {
            const questionData = {
                id: element.dataset.questionId,
                timeLimit: parseInt(element.dataset.timeLimit),
                points: parseInt(element.dataset.points),
                element: element,
                timer: null,
                timeRemaining: parseInt(element.dataset.timeLimit)
            };
            
            this.questions.push(questionData);
            this.totalTimeLimit += questionData.timeLimit;
        });
    }
    
    setupEventListeners() {
        const startButton = document.getElementById('start-assessment');
        const submitButton = document.getElementById('submit-assessment');
        
        if (startButton) {
            startButton.addEventListener('click', () => this.startAssessment());
        }
        
        if (submitButton) {
            submitButton.addEventListener('click', (e) => this.handleSubmit(e));
        }
        
        // Add auto-save functionality
        document.querySelectorAll('textarea[name^="q_"]').forEach(textarea => {
            textarea.addEventListener('input', () => {
                this.saveProgress();
            });
        });
    }
    
    startAssessment() {
        this.isAssessmentActive = true;
        
        // Hide start button, show submit button
        document.getElementById('start-assessment').style.display = 'none';
        document.getElementById('submit-assessment').style.display = 'inline-block';
        
        // Show question timers
        document.querySelectorAll('.question-timer').forEach(timer => {
            timer.style.display = 'block';
        });
        
        // Start overall timer
        this.startOverallTimer();
        
        // Start individual question timers
        this.questions.forEach((question, index) => {
            setTimeout(() => {
                this.startQuestionTimer(question);
            }, index * 1000); // Stagger timer starts
        });
        
        // Update main timer display
        this.updateMainTimerDisplay();
        
        // Show notification
        this.showNotification('Assessment started! Timer is running.', 'success');
    }
    
    startOverallTimer() {
        const timerElement = document.getElementById('timer-text');
        let totalTimeRemaining = this.totalTimeLimit;
        
        this.overallTimer = setInterval(() => {
            totalTimeRemaining--;
            
            const minutes = Math.floor(totalTimeRemaining / 60);
            const seconds = totalTimeRemaining % 60;
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            // Change color based on time remaining
            const timerDisplay = document.getElementById('timer-display');
            if (totalTimeRemaining < 300) { // Last 5 minutes
                timerDisplay.className = 'badge bg-danger fs-6';
            } else if (totalTimeRemaining < 600) { // Last 10 minutes
                timerDisplay.className = 'badge bg-warning fs-6';
            }
            
            if (totalTimeRemaining <= 0) {
                this.timeUp();
            }
        }, 1000);
    }
    
    startQuestionTimer(question) {
        const timerElement = document.getElementById(`timer-${question.id}`);
        if (!timerElement) return;
        
        const progressBar = timerElement.querySelector('.progress-bar');
        const timeRemainingSpan = timerElement.querySelector('.time-remaining');
        
        let timeRemaining = question.timeLimit;
        
        question.timer = setInterval(() => {
            timeRemaining--;
            question.timeRemaining = timeRemaining;
            
            // Update progress bar
            const percentage = (timeRemaining / question.timeLimit) * 100;
            if (progressBar) progressBar.style.width = percentage + '%';
            
            // Update time display
            if (timeRemainingSpan) timeRemainingSpan.textContent = timeRemaining + 's';
            
            // Change progress bar color based on time remaining
            if (progressBar) {
                if (percentage < 20) {
                    progressBar.className = 'progress-bar bg-danger';
                } else if (percentage < 50) {
                    progressBar.className = 'progress-bar bg-warning';
                }
            }
            
            // Disable question when time runs out
            if (timeRemaining <= 0) {
                clearInterval(question.timer);
                this.disableQuestion(question);
            }
        }, 1000);
    }
    
    disableQuestion(question) {
        const textarea = question.element.querySelector('textarea');
        if (textarea) {
            textarea.disabled = true;
            textarea.style.backgroundColor = '#f8f9fa';
        }
        
        // Show timeout notification
        this.showNotification(`Time's up for ${question.id.replace('q_', '').replace('_', ' ')} question!`, 'warning');
    }
    
    timeUp() {
        if (this.overallTimer) clearInterval(this.overallTimer);
        
        // Clear all question timers
        this.questions.forEach(question => {
            if (question.timer) {
                clearInterval(question.timer);
            }
        });
        
        // Auto-submit the form
        const timerText = document.getElementById('timer-text');
        if (timerText) timerText.textContent = 'Time\'s up!';
        this.showNotification('Assessment time completed! Auto-submitting...', 'info');
        
        setTimeout(() => {
            const form = document.getElementById('assessment-form');
            if (form) form.submit();
        }, 2000);
    }
    
    updateMainTimerDisplay() {
        const totalMinutes = Math.floor(this.totalTimeLimit / 60);
        const timerText = document.getElementById('timer-text');
        if (timerText) timerText.textContent = `${totalMinutes}:00 total`;
    }
    
    saveProgress() {
        const form = document.getElementById('assessment-form');
        if (!form) return;
        
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        try {
            localStorage.setItem('assessment_progress', JSON.stringify(data));
        } catch (e) {
            console.warn('Could not save progress to localStorage:', e);
        }
    }
    
    loadProgress() {
        try {
            const saved = localStorage.getItem('assessment_progress');
            if (saved) {
                const data = JSON.parse(saved);
                
                Object.keys(data).forEach(key => {
                    const textarea = document.querySelector(`textarea[name="${key}"]`);
                    if (textarea) {
                        textarea.value = data[key];
                    }
                });
            }
        } catch (e) {
            console.warn('Could not load progress from localStorage:', e);
        }
    }
    
    handleSubmit(e) {
        if (this.isAssessmentActive) {
            // Clear all timers
            if (this.overallTimer) clearInterval(this.overallTimer);
            this.questions.forEach(question => {
                if (question.timer) {
                    clearInterval(question.timer);
                }
            });
            
            // Clear saved progress
            try {
                localStorage.removeItem('assessment_progress');
            } catch (e) {
                console.warn('Could not clear localStorage:', e);
            }
            
            this.showNotification('Submitting assessment...', 'info');
        }
        
        return true; // Allow form submission
    }
    
    showNotification(message, type = 'info') {
        console.log(`Assessment Timer: ${message}`);
        
        // Try to create Bootstrap toast if available
        if (typeof bootstrap !== 'undefined') {
            const toastHtml = `
                <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="fas fa-${type === 'success' ? 'check' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            // Create toast container if it doesn't exist
            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                document.body.appendChild(toastContainer);
            }
            
            // Add toast to container
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            
            // Initialize and show toast
            const toastElement = toastContainer.lastElementChild;
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
            
            // Remove toast element after it's hidden
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    }
}

// Initialize assessment timer when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if assessment questions exist
    if (document.querySelector('.assessment-question')) {
        window.assessmentTimer = new AssessmentTimer();
        
        // Load any saved progress
        window.assessmentTimer.loadProgress();
    }
    
    // Form validation
    const form = document.getElementById('assessment-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const textareas = form.querySelectorAll('textarea');
            let hasAnswers = false;
            
            textareas.forEach(textarea => {
                if (textarea.value.trim().length > 0) {
                    hasAnswers = true;
                }
            });
            
            if (!hasAnswers) {
                e.preventDefault();
                alert('Please answer at least one question before submitting.');
                return false;
            }
        });
    }
});