/**
 * API Status Monitoring and Real-time Updates
 * ==========================================
 * 
 * This module handles:
 * - Real-time API status monitoring
 * - Service availability checking
 * - User interface updates based on API status
 * - Error handling and fallback mechanisms
 */

class APIStatusMonitor {
    constructor() {
        this.statusEndpoints = {
            main: '/api/status',
            aiServices: '/api/ai-services/status',
            recentActivities: '/api/recent-activities',
            progressData: '/api/progress-data'
        };
        
        this.status = {
            main: 'unknown',
            aiServices: 'unknown',
            lastChecked: null
        };
        
        this.init();
    }
    
    init() {
        this.checkAllServices();
        this.setupPeriodicChecks();
        this.setupUI();
    }
    
    async checkAllServices() {
        console.log('Checking API services status...');
        
        try {
            // Check main API status
            const mainStatus = await this.checkService(this.statusEndpoints.main);
            this.status.main = mainStatus.status || 'offline';
            
            // Check AI services
            const aiStatus = await this.checkService(this.statusEndpoints.aiServices);
            this.status.aiServices = aiStatus.status || 'offline';
            
            this.status.lastChecked = new Date().toISOString();
            
            // Update UI
            this.updateStatusDisplay();
            
            console.log('API Status Check Complete:', this.status);
            
        } catch (error) {
            console.error('Error checking API services:', error);
            this.status.main = 'error';
            this.status.aiServices = 'error';
            this.updateStatusDisplay();
        }
    }
    
    async checkService(endpoint) {
        try {
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout: 5000 // 5 second timeout
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.warn(`Service ${endpoint} unavailable:`, error.message);
            return { status: 'offline', error: error.message };
        }
    }
    
    setupPeriodicChecks() {
        // Check every 30 seconds
        setInterval(() => {
            this.checkAllServices();
        }, 30000);
    }
    
    setupUI() {
        // Create status indicator if it doesn't exist
        this.createStatusIndicator();
    }
    
    createStatusIndicator() {
        // Check if status container already exists
        let statusContainer = document.getElementById('api-status-container');
        
        if (!statusContainer) {
            // Create status container and add to appropriate location
            statusContainer = document.createElement('div');
            statusContainer.id = 'api-status-container';
            statusContainer.className = 'api-status-container mt-3';
            
            // Try to add to learning path or main content area
            const learningContent = document.querySelector('.card-body');
            const mainContent = document.querySelector('.container');
            
            if (learningContent) {
                learningContent.appendChild(statusContainer);
            } else if (mainContent) {
                mainContent.appendChild(statusContainer);
            }
        }
        
        // Update the container content
        statusContainer.innerHTML = `
            <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center">
                    <span class="badge me-2" id="api-status-badge">
                        <i class="fas fa-circle" id="api-status-icon"></i>
                        <span id="api-status-text">Checking API...</span>
                    </span>
                    <small class="text-muted">AI Services Status</small>
                </div>
                <div class="d-flex align-items-center">
                    <button class="btn btn-sm btn-outline-secondary" onclick="window.apiMonitor.checkAllServices()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
            </div>
            <div class="mt-2" id="api-details" style="display: none;">
                <small class="text-muted">
                    <div>Main API: <span id="main-api-status">Unknown</span></div>
                    <div>AI Services: <span id="ai-services-status">Unknown</span></div>
                    <div>Last checked: <span id="last-checked">Never</span></div>
                </small>
            </div>
        `;
        
        // Add click handler to show/hide details
        const statusBadge = statusContainer.querySelector('#api-status-badge');
        const detailsDiv = statusContainer.querySelector('#api-details');
        
        statusBadge.addEventListener('click', () => {
            detailsDiv.style.display = detailsDiv.style.display === 'none' ? 'block' : 'none';
        });
    }
    
    updateStatusDisplay() {
        const statusBadge = document.getElementById('api-status-badge');
        const statusIcon = document.getElementById('api-status-icon');
        const statusText = document.getElementById('api-status-text');
        
        if (!statusBadge || !statusIcon || !statusText) {
            console.warn('Status UI elements not found');
            return;
        }
        
        // Determine overall status
        let overallStatus = 'offline';
        let statusColor = 'danger';
        let statusMessage = 'Services Offline';
        
        if (this.status.main === 'online' && this.status.aiServices === 'online') {
            overallStatus = 'online';
            statusColor = 'success';
            statusMessage = 'All Services Online';
        } else if (this.status.main === 'online') {
            overallStatus = 'limited';
            statusColor = 'warning';
            statusMessage = 'Limited Services';
        } else if (this.status.main === 'error' || this.status.aiServices === 'error') {
            overallStatus = 'error';
            statusColor = 'danger';
            statusMessage = 'Service Error';
        }
        
        // Update badge appearance
        statusBadge.className = `badge bg-${statusColor} me-2`;
        statusText.textContent = statusMessage;
        
        // Update icon
        statusIcon.className = `fas fa-circle`;
        
        // Update details if visible
        const mainStatus = document.getElementById('main-api-status');
        const aiStatus = document.getElementById('ai-services-status');
        const lastChecked = document.getElementById('last-checked');
        
        if (mainStatus) mainStatus.textContent = this.status.main;
        if (aiStatus) aiStatus.textContent = this.status.aiServices;
        if (lastChecked && this.status.lastChecked) {
            lastChecked.textContent = new Date(this.status.lastChecked).toLocaleTimeString();
        }
    }
    
    // Public method to get current status
    getStatus() {
        return { ...this.status };
    }
    
    // Check if APIs are ready for use
    isReady() {
        return this.status.main === 'online';
    }
    
    // Check if AI services are available
    hasAIServices() {
        return this.status.aiServices === 'online';
    }
}

// Initialize API monitoring when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing API Status Monitor...');
    window.apiMonitor = new APIStatusMonitor();
    
    // Also expose for debugging
    window.checkAPIStatus = () => window.apiMonitor.checkAllServices();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIStatusMonitor };
}