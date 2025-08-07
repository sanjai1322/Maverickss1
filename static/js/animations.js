// Mavericks - Professional Animations

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof gsap !== 'undefined') {
        initializeAnimations();
    }
});

function initializeAnimations() {
    // Simple fade-in animation for main content
    gsap.from('main', {
        opacity: 0,
        y: 20,
        duration: 0.6,
        ease: 'power2.out'
    });

    // Stagger animation for cards if they exist
    const cards = document.querySelectorAll('.card');
    if (cards.length > 0) {
        gsap.from(cards, {
            opacity: 0,
            y: 30,
            duration: 0.6,
            ease: 'power2.out',
            stagger: 0.1,
            delay: 0.2
        });
    }

    // Add interactive animations
    addInteractiveAnimations();
}

function addInteractiveAnimations() {
    // Card hover animations
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                y: -2,
                duration: 0.3,
                ease: 'power2.out'
            });
            
            const icon = card.querySelector('.feature-icon');
            if (icon) {
                gsap.to(icon, {
                    scale: 1.05,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            }
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                y: 0,
                duration: 0.3,
                ease: 'power2.out'
            });
            
            const icon = card.querySelector('.feature-icon');
            if (icon) {
                gsap.to(icon, {
                    scale: 1,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            }
        });
    });

    // Button hover animations
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', () => {
            gsap.to(button, {
                y: -1,
                duration: 0.2,
                ease: 'power2.out'
            });
        });

        button.addEventListener('mouseleave', () => {
            gsap.to(button, {
                y: 0,
                duration: 0.2,
                ease: 'power2.out'
            });
        });
    });
}

// Form animations for professional focus states
function animateFormElements() {
    const formElements = document.querySelectorAll('.form-control, .form-select');
    
    formElements.forEach(element => {
        element.addEventListener('focus', () => {
            gsap.to(element, {
                scale: 1.01,
                duration: 0.2,
                ease: 'power2.out'
            });
        });

        element.addEventListener('blur', () => {
            gsap.to(element, {
                scale: 1,
                duration: 0.2,
                ease: 'power2.out'
            });
        });
    });
}

// Initialize form animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    animateFormElements();
});