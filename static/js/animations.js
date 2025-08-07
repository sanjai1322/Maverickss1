// Mavericks - GSAP Animations

// Initialize GSAP and set up animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Register GSAP plugins if available
    if (typeof gsap !== 'undefined') {
        initializeAnimations();
    }
});

function initializeAnimations() {
    // Set initial states
    gsap.set('.hero-section', { opacity: 0, y: 50 });
    gsap.set('.card', { opacity: 0, y: 30, scale: 0.9 });
    gsap.set('.feature-icon', { opacity: 0, scale: 0.5, rotation: -45 });
    gsap.set('.step-number', { opacity: 0, scale: 0.3 });
    gsap.set('.navbar', { y: -100 });

    // Create main timeline
    const tl = gsap.timeline();

    // Navbar animation
    tl.to('.navbar', {
        y: 0,
        duration: 0.8,
        ease: 'power3.out'
    });

    // Hero section animation
    tl.to('.hero-section', {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: 'power3.out'
    }, '-=0.3');

    // Animate hero title characters
    if (document.querySelector('.hero-title')) {
        const heroTitle = document.querySelector('.hero-title');
        const titleText = heroTitle.textContent;
        heroTitle.innerHTML = titleText.split('').map(char => 
            char === ' ' ? ' ' : `<span class="char">${char}</span>`
        ).join('');

        gsap.fromTo('.hero-title .char', {
            opacity: 0,
            y: 50,
            rotation: -15
        }, {
            opacity: 1,
            y: 0,
            rotation: 0,
            duration: 0.8,
            ease: 'back.out(1.7)',
            stagger: 0.03,
            delay: 0.5
        });
    }

    // Cards animation with stagger
    tl.to('.card', {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.8,
        ease: 'power3.out',
        stagger: 0.2
    }, '-=0.5');

    // Feature icons animation
    tl.to('.feature-icon', {
        opacity: 1,
        scale: 1,
        rotation: 0,
        duration: 0.6,
        ease: 'back.out(1.7)',
        stagger: 0.15
    }, '-=0.6');

    // Step numbers animation
    tl.to('.step-number', {
        opacity: 1,
        scale: 1,
        duration: 0.5,
        ease: 'back.out(1.7)',
        stagger: 0.1
    }, '-=0.3');

    // Add scroll-triggered animations
    addScrollAnimations();
    
    // Add interactive animations
    addInteractiveAnimations();
    
    // Add floating elements
    addFloatingAnimations();
    
    // Add button hover effects
    addButtonAnimations();
}

function addScrollAnimations() {
    // Animate elements that come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                
                if (target.classList.contains('fade-in-scroll')) {
                    gsap.fromTo(target, {
                        opacity: 0,
                        y: 30
                    }, {
                        opacity: 1,
                        y: 0,
                        duration: 0.8,
                        ease: 'power3.out'
                    });
                }
                
                if (target.classList.contains('slide-in-left')) {
                    gsap.fromTo(target, {
                        opacity: 0,
                        x: -50
                    }, {
                        opacity: 1,
                        x: 0,
                        duration: 0.8,
                        ease: 'power3.out'
                    });
                }
                
                if (target.classList.contains('slide-in-right')) {
                    gsap.fromTo(target, {
                        opacity: 0,
                        x: 50
                    }, {
                        opacity: 1,
                        x: 0,
                        duration: 0.8,
                        ease: 'power3.out'
                    });
                }
                
                observer.unobserve(target);
            }
        });
    }, observerOptions);

    // Add classes to elements that should animate on scroll
    document.querySelectorAll('.card:not(.animated)').forEach(card => {
        card.classList.add('fade-in-scroll');
        observer.observe(card);
    });
}

function addInteractiveAnimations() {
    // Card hover animations
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                scale: 1.05,
                y: -10,
                duration: 0.3,
                ease: 'power2.out',
                boxShadow: '0 25px 50px -12px rgba(99, 102, 241, 0.25)'
            });
            
            const icon = card.querySelector('.feature-icon');
            if (icon) {
                gsap.to(icon, {
                    scale: 1.1,
                    rotation: 5,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            }
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                scale: 1,
                y: 0,
                duration: 0.3,
                ease: 'power2.out',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
            });
            
            const icon = card.querySelector('.feature-icon');
            if (icon) {
                gsap.to(icon, {
                    scale: 1,
                    rotation: 0,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            }
        });
    });

    // Navigation link hover animations
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('mouseenter', () => {
            gsap.to(link, {
                y: -3,
                scale: 1.05,
                duration: 0.2,
                ease: 'power2.out'
            });
        });

        link.addEventListener('mouseleave', () => {
            gsap.to(link, {
                y: 0,
                scale: 1,
                duration: 0.2,
                ease: 'power2.out'
            });
        });
    });
}

function addFloatingAnimations() {
    // Create floating animation for rocket icon
    const rocketIcon = document.querySelector('.brand-logo i');
    if (rocketIcon) {
        gsap.to(rocketIcon, {
            y: -5,
            duration: 2,
            ease: 'power2.inOut',
            yoyo: true,
            repeat: -1
        });
    }

    // Floating animation for feature icons
    document.querySelectorAll('.feature-icon').forEach((icon, index) => {
        gsap.to(icon, {
            y: -8,
            duration: 2 + (index * 0.3),
            ease: 'power2.inOut',
            yoyo: true,
            repeat: -1,
            delay: index * 0.5
        });
    });

    // Create particle effect background
    createParticleEffect();
}

function addButtonAnimations() {
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', () => {
            gsap.to(button, {
                scale: 1.05,
                duration: 0.2,
                ease: 'power2.out'
            });
        });

        button.addEventListener('mouseleave', () => {
            gsap.to(button, {
                scale: 1,
                duration: 0.2,
                ease: 'power2.out'
            });
        });

        button.addEventListener('mousedown', () => {
            gsap.to(button, {
                scale: 0.95,
                duration: 0.1,
                ease: 'power2.out'
            });
        });

        button.addEventListener('mouseup', () => {
            gsap.to(button, {
                scale: 1.05,
                duration: 0.1,
                ease: 'power2.out'
            });
        });
    });
}

function createParticleEffect() {
    // Create floating particles in the background
    const particleContainer = document.createElement('div');
    particleContainer.style.position = 'fixed';
    particleContainer.style.top = '0';
    particleContainer.style.left = '0';
    particleContainer.style.width = '100%';
    particleContainer.style.height = '100%';
    particleContainer.style.pointerEvents = 'none';
    particleContainer.style.zIndex = '-1';
    document.body.appendChild(particleContainer);

    // Create particles
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '4px';
        particle.style.height = '4px';
        particle.style.backgroundColor = '#6366f1';
        particle.style.borderRadius = '50%';
        particle.style.opacity = '0.3';
        
        // Random position
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        
        particleContainer.appendChild(particle);

        // Animate particle
        gsap.to(particle, {
            y: -window.innerHeight - 100,
            duration: 10 + Math.random() * 20,
            ease: 'none',
            repeat: -1,
            delay: Math.random() * 10
        });

        gsap.to(particle, {
            x: (Math.random() - 0.5) * 100,
            duration: 3 + Math.random() * 4,
            ease: 'power2.inOut',
            yoyo: true,
            repeat: -1
        });

        gsap.to(particle, {
            opacity: 0.1 + Math.random() * 0.5,
            duration: 2 + Math.random() * 3,
            ease: 'power2.inOut',
            yoyo: true,
            repeat: -1
        });
    }
}

// Page transition animations
function animatePageTransition() {
    return new Promise((resolve) => {
        gsap.to('main', {
            opacity: 0,
            y: -30,
            duration: 0.3,
            ease: 'power2.in',
            onComplete: resolve
        });
    });
}

function animatePageIn() {
    gsap.fromTo('main', {
        opacity: 0,
        y: 30
    }, {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: 'power2.out'
    });
}

// Form animations
function animateFormElements() {
    const formElements = document.querySelectorAll('.form-control, .form-select');
    
    formElements.forEach(element => {
        element.addEventListener('focus', () => {
            gsap.to(element, {
                scale: 1.02,
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

// Progress bar animations
function animateProgressBar(progressBar, targetValue) {
    gsap.fromTo(progressBar, {
        width: '0%'
    }, {
        width: targetValue + '%',
        duration: 2,
        ease: 'power2.out'
    });
}

// Initialize additional animations when needed
document.addEventListener('DOMContentLoaded', () => {
    animateFormElements();
    
    // Animate progress bars if they exist
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const value = bar.getAttribute('aria-valuenow') || bar.style.width.replace('%', '');
        if (value) {
            animateProgressBar(bar, parseInt(value));
        }
    });
});

// Export functions for use in other scripts
window.MaverickAnimations = {
    animatePageTransition,
    animatePageIn,
    animateProgressBar
};