/**
 * React-Compatible Components for Mavericks Platform
 * =================================================
 * 
 * This file contains React-style components and utilities that can be used
 * with or without a full React framework. These components provide:
 * 
 * 1. Assessment Quiz Component - Interactive timer-based quiz system
 * 2. Learning Path Tracker - Dynamic progress visualization
 * 3. Skill Display Component - Resume skill visualization
 * 4. Progress Analytics - Real-time progress charts
 * 5. Hackathon Dashboard - Competition management interface
 * 
 * Each component is designed to work standalone or as part of a React app.
 */

// React-style Assessment Component
class AssessmentQuizComponent {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            skills: [],
            timeLimit: 3600, // 1 hour default
            autoSave: true,
            ...options
        };
        this.state = {
            currentQuestion: 0,
            answers: {},
            timeRemaining: this.options.timeLimit,
            isActive: false,
            score: 0
        };
        
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        this.render();
        this.bindEvents();
        
        // Load saved state if available
        if (this.options.autoSave) {
            this.loadState();
        }
    }
    
    render() {
        const { skills } = this.options;
        const { currentQuestion, timeRemaining, isActive } = this.state;
        
        this.container.innerHTML = `
            <div class="assessment-quiz-container">
                <div class="quiz-header">
                    <h3>Personalized Assessment Quiz</h3>
                    <div class="timer ${isActive ? 'active' : ''}">
                        <i class="fas fa-clock"></i>
                        <span class="time-display">${this.formatTime(timeRemaining)}</span>
                    </div>
                </div>
                
                <div class="skills-overview">
                    <h5>Skills Being Assessed:</h5>
                    <div class="skill-tags">
                        ${skills.map(skill => `
                            <span class="badge bg-primary skill-tag">${skill}</span>
                        `).join('')}
                    </div>
                </div>
                
                <div class="question-container">
                    ${this.renderCurrentQuestion()}
                </div>
                
                <div class="quiz-controls">
                    ${!isActive ? 
                        `<button class="btn btn-success btn-lg" onclick="window.assessmentQuiz.startQuiz()">
                            <i class="fas fa-play"></i> Start Assessment
                        </button>` :
                        `<button class="btn btn-primary" onclick="window.assessmentQuiz.nextQuestion()">
                            Next Question
                        </button>
                        <button class="btn btn-outline-warning" onclick="window.assessmentQuiz.saveProgress()">
                            Save Progress
                        </button>`
                    }
                </div>
            </div>
        `;
    }
    
    renderCurrentQuestion() {
        const { skills } = this.options;
        const { currentQuestion } = this.state;
        
        if (currentQuestion >= skills.length) {
            return this.renderQuizComplete();
        }
        
        const skill = skills[currentQuestion];
        const question = this.generateQuestionForSkill(skill);
        
        return `
            <div class="question-card">
                <div class="question-header">
                    <span class="question-number">Question ${currentQuestion + 1} of ${skills.length}</span>
                    <span class="skill-badge">${skill}</span>
                </div>
                
                <div class="question-content">
                    <h4>${question.text}</h4>
                    <div class="question-details">
                        <small class="text-muted">
                            <i class="fas fa-star"></i> ${question.points} points
                            <i class="fas fa-clock ml-3"></i> ${question.timeLimit}s recommended
                        </small>
                    </div>
                </div>
                
                <div class="answer-section">
                    <textarea 
                        class="form-control answer-input" 
                        rows="6" 
                        placeholder="Type your detailed answer here..."
                        onchange="window.assessmentQuiz.updateAnswer(this.value)"
                    >${this.state.answers[currentQuestion] || ''}</textarea>
                    
                    <div class="answer-hints mt-2">
                        <small class="text-muted">
                            <i class="fas fa-lightbulb"></i> 
                            Include examples, explain your reasoning, and use technical terminology.
                        </small>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderQuizComplete() {
        return `
            <div class="quiz-complete">
                <div class="text-center">
                    <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                    <h3>Assessment Complete!</h3>
                    <p class="lead">You've successfully completed all ${this.options.skills.length} questions.</p>
                    
                    <div class="final-score mt-4">
                        <div class="score-display">
                            <h2 class="score-number">${this.state.score}</h2>
                            <p>Total Score</p>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary btn-lg mt-3" onclick="window.assessmentQuiz.submitQuiz()">
                        <i class="fas fa-paper-plane"></i> Submit Assessment
                    </button>
                </div>
            </div>
        `;
    }
    
    generateQuestionForSkill(skill) {
        const questionBank = {
            'python': {
                text: 'Explain the difference between lists and tuples in Python. When would you use each?',
                points: 15,
                timeLimit: 120
            },
            'javascript': {
                text: 'What is event delegation in JavaScript and why is it useful for performance?',
                points: 15,
                timeLimit: 120
            },
            'react': {
                text: 'Explain the concept of Virtual DOM in React and how it improves application performance.',
                points: 20,
                timeLimit: 180
            },
            'java': {
                text: 'What is the difference between abstract classes and interfaces in Java?',
                points: 18,
                timeLimit: 150
            },
            'html': {
                text: 'What are semantic HTML elements and why are they important for accessibility?',
                points: 12,
                timeLimit: 90
            },
            'css': {
                text: 'Explain the CSS box model and how margin, border, padding, and content relate to each other.',
                points: 12,
                timeLimit: 90
            },
            'api': {
                text: 'What is the difference between REST and GraphQL APIs? When would you choose one over the other?',
                points: 20,
                timeLimit: 180
            },
            'machine learning': {
                text: 'Explain overfitting in machine learning and describe 3 techniques to prevent it.',
                points: 25,
                timeLimit: 240
            }
        };
        
        return questionBank[skill.toLowerCase()] || {
            text: `Describe your experience with ${skill} and provide an example of how you've used it in a project.`,
            points: 10,
            timeLimit: 120
        };
    }
    
    // Component Methods
    startQuiz() {
        this.state.isActive = true;
        this.startTimer();
        this.render();
    }
    
    nextQuestion() {
        if (this.state.currentQuestion < this.options.skills.length - 1) {
            this.state.currentQuestion++;
            this.render();
        } else {
            this.completeQuiz();
        }
    }
    
    updateAnswer(value) {
        this.state.answers[this.state.currentQuestion] = value;
        if (this.options.autoSave) {
            this.saveState();
        }
    }
    
    startTimer() {
        this.timer = setInterval(() => {
            this.state.timeRemaining--;
            
            if (this.state.timeRemaining <= 0) {
                this.timeUp();
            } else {
                this.updateTimerDisplay();
            }
        }, 1000);
    }
    
    updateTimerDisplay() {
        const timerElement = this.container.querySelector('.time-display');
        if (timerElement) {
            timerElement.textContent = this.formatTime(this.state.timeRemaining);
        }
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    timeUp() {
        clearInterval(this.timer);
        this.state.isActive = false;
        alert('Time\'s up! Your assessment will be submitted automatically.');
        this.submitQuiz();
    }
    
    completeQuiz() {
        clearInterval(this.timer);
        this.state.isActive = false;
        this.calculateScore();
        this.render();
    }
    
    calculateScore() {
        let totalScore = 0;
        const answers = this.state.answers;
        
        Object.keys(answers).forEach(questionIndex => {
            const answer = answers[questionIndex];
            const skill = this.options.skills[questionIndex];
            const question = this.generateQuestionForSkill(skill);
            
            // Basic scoring algorithm
            let score = 0;
            if (answer && answer.length > 50) {
                score += question.points * 0.6; // Base score for substantial answer
                
                // Bonus for technical keywords
                const technicalWords = ['algorithm', 'performance', 'optimization', 'scalability', 'framework'];
                const wordCount = technicalWords.filter(word => 
                    answer.toLowerCase().includes(word.toLowerCase())
                ).length;
                score += wordCount * 2;
                
                // Bonus for length (comprehensive answers)
                if (answer.length > 200) score += question.points * 0.2;
                if (answer.length > 500) score += question.points * 0.2;
            }
            
            totalScore += Math.min(score, question.points); // Cap at max points
        });
        
        this.state.score = Math.round(totalScore);
    }
    
    submitQuiz() {
        // Submit to Flask backend
        const formData = new FormData();
        
        Object.keys(this.state.answers).forEach(questionIndex => {
            const skill = this.options.skills[questionIndex];
            formData.append(`q_${skill.toLowerCase().replace(' ', '_')}`, this.state.answers[questionIndex]);
        });
        
        fetch('/assessment_panel', {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.ok) {
                window.location.href = '/progress';
            } else {
                alert('Error submitting assessment. Please try again.');
            }
        }).catch(error => {
            console.error('Submit error:', error);
            alert('Network error. Please check your connection and try again.');
        });
    }
    
    saveProgress() {
        this.saveState();
        this.showToast('Progress saved successfully!', 'success');
    }
    
    saveState() {
        try {
            localStorage.setItem('assessment_quiz_state', JSON.stringify(this.state));
        } catch (e) {
            console.warn('Could not save state:', e);
        }
    }
    
    loadState() {
        try {
            const saved = localStorage.getItem('assessment_quiz_state');
            if (saved) {
                this.state = { ...this.state, ...JSON.parse(saved) };
            }
        } catch (e) {
            console.warn('Could not load state:', e);
        }
    }
    
    showToast(message, type = 'info') {
        // Create Bootstrap toast notification
        const toastContainer = document.getElementById('toast-container') || 
            (() => {
                const container = document.createElement('div');
                container.id = 'toast-container';
                container.className = 'toast-container position-fixed top-0 end-0 p-3';
                document.body.appendChild(container);
                return container;
            })();
        
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }
    
    bindEvents() {
        // Bind keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (this.state.isActive) {
                if (e.ctrlKey && e.key === 's') {
                    e.preventDefault();
                    this.saveProgress();
                }
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    this.nextQuestion();
                }
            }
        });
    }
}

// Global initialization function for React components
window.initReactComponents = function(containerId, userSkills) {
    // Initialize Assessment Quiz Component
    if (document.getElementById(containerId)) {
        window.assessmentQuiz = new AssessmentQuizComponent(containerId, {
            skills: userSkills || [],
            timeLimit: 3600,
            autoSave: true
        });
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AssessmentQuizComponent };
}