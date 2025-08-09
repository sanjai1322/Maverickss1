// Global JavaScript for the Skill Assessment Platform
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'form-text text-end';
            counter.style.fontSize = '0.8rem';
            
            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${remaining} characters remaining`;
                
                if (remaining < 50) {
                    counter.classList.add('text-warning');
                } else {
                    counter.classList.remove('text-warning');
                }
                
                if (remaining < 0) {
                    counter.classList.add('text-danger');
                    counter.classList.remove('text-warning');
                } else {
                    counter.classList.remove('text-danger');
                }
            }
            
            textarea.addEventListener('input', updateCounter);
            if (textarea.parentNode) {
                textarea.parentNode.appendChild(counter);
                updateCounter();
            }
        }
    });
    
    // Auto-save form data to localStorage (for longer forms)
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        const formId = form.getAttribute('action') || window.location.pathname;
        const storageKey = `form_data_${formId}`;
        
        // Load saved data
        const savedData = localStorage.getItem(storageKey);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(function(key) {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'submit' && input.value !== undefined) {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.log('Error loading saved form data:', e);
            }
        }
        
        // Save data on input
        form.addEventListener('input', function(e) {
            if (e.target.name) {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem(storageKey, JSON.stringify(data));
            }
        });
        
        // Clear saved data on successful submission
        form.addEventListener('submit', function() {
            setTimeout(() => {
                localStorage.removeItem(storageKey);
            }, 1000);
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Progress indicator for multi-step forms
    function updateProgress() {
        const progressBars = document.querySelectorAll('.progress-bar[data-target]');
        progressBars.forEach(function(bar) {
            const targetSelector = bar.getAttribute('data-target');
            const targets = document.querySelectorAll(targetSelector);
            const completed = Array.from(targets).filter(function(input) {
                return input.value.trim() !== '';
            }).length;
            const percentage = (completed / targets.length) * 100;
            bar.style.width = percentage + '%';
            bar.textContent = Math.round(percentage) + '%';
        });
    }
    
    // Update progress on input
    document.addEventListener('input', updateProgress);
    updateProgress();
    
    // Word count for textareas
    const wordCountTextareas = document.querySelectorAll('textarea[data-word-count]');
    wordCountTextareas.forEach(function(textarea) {
        const counter = document.createElement('div');
        counter.className = 'form-text text-muted';
        counter.style.fontSize = '0.8rem';
        
        function updateWordCount() {
            const words = textarea.value.trim().split(/\s+/).filter(word => word.length > 0).length;
            counter.textContent = `${words} words`;
            
            const minWords = parseInt(textarea.getAttribute('data-min-words')) || 0;
            if (words < minWords) {
                counter.classList.add('text-warning');
                counter.textContent += ` (minimum ${minWords} words)`;
            } else {
                counter.classList.remove('text-warning');
            }
        }
        
        textarea.addEventListener('input', updateWordCount);
        textarea.parentNode.appendChild(counter);
        updateWordCount();
    });
    
    // Loading states for form submissions
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            });
        }
    });
    
    // Alert auto-dismiss
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
});

// Utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Export functions for use in other scripts
window.SkillAssessment = {
    showNotification,
    formatDate
};
