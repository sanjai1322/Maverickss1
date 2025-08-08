// Mavericks Onboarding Tour
class OnboardingTour {
    constructor() {
        this.currentStep = 0;
        this.steps = [
            {
                target: '.brand-logo',
                title: 'Welcome to Mavericks!',
                content: 'Your AI-powered skill assessment platform. Let\'s take a quick tour to get you started.',
                position: 'bottom'
            },
            {
                target: 'a[href="/profile"]',
                title: 'Create Your Profile',
                content: 'Start by uploading your resume. Our AI will analyze your skills and create your professional profile.',
                position: 'bottom'
            },
            {
                target: 'a[href="/assessment"]',
                title: 'Take Skill Assessments',
                content: 'Test your technical skills with our AI-powered assessments. Get detailed feedback on your performance.',
                position: 'bottom'
            },
            {
                target: 'a[href="/progress"]',
                title: 'Track Your Progress',
                content: 'Monitor your skill development and assessment scores over time.',
                position: 'bottom'
            },
            {
                target: 'a[href="/learning_path"]',
                title: 'Follow Learning Paths',
                content: 'Get personalized learning recommendations based on your skills and career goals.',
                position: 'bottom'
            },
            {
                target: 'a[href="/hackathon"]',
                title: 'Join Hackathons',
                content: 'Participate in coding challenges and compete with other developers.',
                position: 'bottom'
            }
        ];
        this.overlay = null;
        this.tooltip = null;
    }

    start() {
        // Check if user has already seen the tour
        if (localStorage.getItem('mavericks_tour_completed') === 'true') {
            return;
        }

        this.createOverlay();
        this.showStep(0);
    }

    createOverlay() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'onboarding-overlay';
        this.overlay.innerHTML = `
            <div class="onboarding-tooltip" id="onboarding-tooltip">
                <div class="tooltip-header">
                    <h5 class="tooltip-title"></h5>
                    <button class="btn-close-tour" onclick="onboardingTour.skip()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="tooltip-content"></div>
                <div class="tooltip-footer">
                    <div class="step-indicator">
                        <span class="current-step">1</span> of <span class="total-steps">${this.steps.length}</span>
                    </div>
                    <div class="tooltip-buttons">
                        <button class="btn btn-outline-secondary btn-sm me-2" onclick="onboardingTour.skip()">Skip Tour</button>
                        <button class="btn btn-maverick btn-sm" onclick="onboardingTour.next()">Next</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(this.overlay);
        this.tooltip = document.getElementById('onboarding-tooltip');
    }

    showStep(stepIndex) {
        if (stepIndex >= this.steps.length) {
            this.complete();
            return;
        }

        const step = this.steps[stepIndex];
        const target = document.querySelector(step.target);

        if (!target) {
            // Update current step before skipping to prevent infinite loop
            this.currentStep = stepIndex;
            this.next();
            return;
        }

        // Update tooltip content
        this.tooltip.querySelector('.tooltip-title').textContent = step.title;
        this.tooltip.querySelector('.tooltip-content').textContent = step.content;
        this.tooltip.querySelector('.current-step').textContent = stepIndex + 1;

        // Update button text for last step
        const nextBtn = this.tooltip.querySelector('.tooltip-buttons .btn-maverick');
        if (stepIndex === this.steps.length - 1) {
            nextBtn.textContent = 'Get Started';
            nextBtn.onclick = () => this.complete();
        } else {
            nextBtn.textContent = 'Next';
            nextBtn.onclick = () => this.next();
        }

        // Position tooltip
        this.positionTooltip(target, step.position);

        // Highlight target element
        this.highlightElement(target);

        this.currentStep = stepIndex;
    }

    positionTooltip(target, position) {
        const rect = target.getBoundingClientRect();
        const tooltip = this.tooltip;
        
        // Reset classes
        tooltip.className = 'onboarding-tooltip';
        tooltip.classList.add(`position-${position}`);

        let top, left;

        switch (position) {
            case 'bottom':
                top = rect.bottom + 15;
                left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2);
                break;
            case 'top':
                top = rect.top - tooltip.offsetHeight - 15;
                left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2);
                break;
            case 'right':
                top = rect.top + (rect.height / 2) - (tooltip.offsetHeight / 2);
                left = rect.right + 15;
                break;
            case 'left':
                top = rect.top + (rect.height / 2) - (tooltip.offsetHeight / 2);
                left = rect.left - tooltip.offsetWidth - 15;
                break;
        }

        // Keep tooltip within viewport
        const margin = 20;
        top = Math.max(margin, Math.min(top, window.innerHeight - tooltip.offsetHeight - margin));
        left = Math.max(margin, Math.min(left, window.innerWidth - tooltip.offsetWidth - margin));

        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
    }

    highlightElement(target) {
        // Remove previous highlights
        document.querySelectorAll('.onboarding-highlight').forEach(el => {
            el.classList.remove('onboarding-highlight');
        });

        // Add highlight to current target
        target.classList.add('onboarding-highlight');

        // Scroll target into view if needed
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    next() {
        this.showStep(this.currentStep + 1);
    }

    previous() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }

    skip() {
        this.complete();
    }

    complete() {
        // Remove overlay and cleanup
        if (this.overlay) {
            document.body.removeChild(this.overlay);
        }

        // Remove highlights
        document.querySelectorAll('.onboarding-highlight').forEach(el => {
            el.classList.remove('onboarding-highlight');
        });

        // Mark tour as completed
        localStorage.setItem('mavericks_tour_completed', 'true');

        // Show completion message
        this.showCompletionMessage();
    }

    showCompletionMessage() {
        // Create a temporary success message
        const message = document.createElement('div');
        message.className = 'onboarding-complete-message';
        message.innerHTML = `
            <div class="alert alert-success fade-in">
                <i class="fas fa-rocket me-2"></i>
                Welcome aboard, Maverick! Start by creating your profile to begin your journey.
            </div>
        `;
        document.body.appendChild(message);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (message.parentNode) {
                document.body.removeChild(message);
            }
        }, 4000);
    }

    // Method to reset tour (for testing)
    reset() {
        localStorage.removeItem('mavericks_tour_completed');
    }
}

// Initialize tour when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only start tour on the homepage for new users
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        window.onboardingTour = new OnboardingTour();
        
        // Start tour after a brief delay to ensure page is fully loaded
        setTimeout(() => {
            window.onboardingTour.start();
        }, 1000);
    }
});

// Add manual tour trigger for testing
window.startOnboardingTour = function() {
    if (window.onboardingTour) {
        window.onboardingTour.reset();
        window.onboardingTour.start();
    } else {
        window.onboardingTour = new OnboardingTour();
        window.onboardingTour.start();
    }
};