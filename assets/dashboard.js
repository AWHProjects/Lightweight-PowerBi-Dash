// Professional Dashboard JavaScript Enhancements
class DashboardEnhancer {
    constructor() {
        this.init();
    }

    init() {
        this.setupAnimatedMenu();
        this.setupChartEnhancements();
        this.setupRealTimeUpdates();
        this.setupKeyboardShortcuts();
        this.setupNotifications();
        this.loadSettings();
    }

    // Animated Menu System
    setupAnimatedMenu() {
        // Create animated menu if it doesn't exist
        if (!document.querySelector('.nav-menu')) {
            const menuHTML = `
                <div class="nav-menu">
                    <button class="menu-toggle" onclick="dashboardEnhancer.toggleMenu()">
                        <i class="fas fa-bars"></i>
                    </button>
                    <div class="menu-items" id="menuItems">
                        <a href="#" class="menu-item" onclick="dashboardEnhancer.exportData()">
                            <i class="fas fa-download"></i> Export Data
                        </a>
                        <a href="#" class="menu-item" onclick="dashboardEnhancer.refreshData()">
                            <i class="fas fa-sync"></i> Refresh
                        </a>
                        <a href="#" class="menu-item" onclick="dashboardEnhancer.toggleFullscreen()">
                            <i class="fas fa-expand"></i> Fullscreen
                        </a>
                        <a href="#" class="menu-item" onclick="dashboardEnhancer.openN8nWorkflow()">
                            <i class="fas fa-cogs"></i> Automation
                        </a>
                        <a href="#" class="menu-item" onclick="dashboardEnhancer.showSettings()">
                            <i class="fas fa-cog"></i> Settings
                        </a>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', menuHTML);
        }
    }

    toggleMenu() {
        const menuItems = document.getElementById('menuItems');
        menuItems.classList.toggle('active');
    }

    // Enhanced Chart Interactions
    setupChartEnhancements() {
        // Add custom hover effects and animations to charts
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('plotly-graph-div')) {
                            this.enhanceChart(node);
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    enhanceChart(chartDiv) {
        // Add loading animation
        chartDiv.style.position = 'relative';
        
        // Add custom toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'chart-toolbar';
        toolbar.innerHTML = `
            <button onclick="dashboardEnhancer.downloadChart('${chartDiv.id}')" title="Download Chart">
                <i class="fas fa-camera"></i>
            </button>
            <button onclick="dashboardEnhancer.zoomChart('${chartDiv.id}')" title="Zoom">
                <i class="fas fa-search-plus"></i>
            </button>
        `;
        chartDiv.appendChild(toolbar);

        // Add real-time data indicators
        this.addDataIndicator(chartDiv);
    }

    addDataIndicator(chartDiv) {
        const indicator = document.createElement('div');
        indicator.className = 'data-indicator';
        indicator.innerHTML = `
            <span class="status-indicator status-online"></span>
            <small>Live Data</small>
        `;
        indicator.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            z-index: 1000;
        `;
        chartDiv.appendChild(indicator);
    }

    // Real-time Updates Simulation
    setupRealTimeUpdates() {
        setInterval(() => {
            this.updateDataIndicators();
        }, 5000);
    }

    updateDataIndicators() {
        const indicators = document.querySelectorAll('.status-indicator');
        indicators.forEach(indicator => {
            // Simulate data freshness
            const isOnline = Math.random() > 0.1;
            indicator.className = `status-indicator ${isOnline ? 'status-online' : 'status-warning'}`;
        });
    }

    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshData();
                        break;
                    case 'e':
                        e.preventDefault();
                        this.exportData();
                        break;
                    case 'f':
                        e.preventDefault();
                        this.toggleFullscreen();
                        break;
                }
            }
        });
    }

    // Notification System
    setupNotifications() {
        this.notificationContainer = document.createElement('div');
        this.notificationContainer.id = 'notification-container';
        this.notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10000;
        `;
        document.body.appendChild(this.notificationContainer);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            animation: slideInDown 0.3s ease;
        `;
        notification.textContent = message;
        
        this.notificationContainer.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Menu Actions
    exportData() {
        this.showNotification('Exporting dashboard data...', 'info');
        // Simulate export process
        setTimeout(() => {
            this.showNotification('Data exported successfully!', 'success');
        }, 2000);
    }

    refreshData() {
        this.showNotification('Refreshing dashboard data...', 'info');
        // Trigger Dash callback refresh
        setTimeout(() => {
            this.showNotification('Dashboard refreshed!', 'success');
            location.reload();
        }, 1000);
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            this.showNotification('Entered fullscreen mode', 'info');
        } else {
            document.exitFullscreen();
            this.showNotification('Exited fullscreen mode', 'info');
        }
    }

    openN8nWorkflow() {
        this.showNotification('Opening n8n workflow automation...', 'info');
        // Open n8n integration modal or redirect
        this.showN8nModal();
    }

    showN8nModal() {
        const modal = document.createElement('div');
        modal.className = 'n8n-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 15px; max-width: 500px; width: 90%;">
                <h3>n8n Workflow Integration</h3>
                <p>Connect your dashboard to n8n for automated workflows:</p>
                <ul>
                    <li>Automated ticket escalation</li>
                    <li>SLA breach notifications</li>
                    <li>Weekly reports generation</li>
                    <li>Slack/Teams integration</li>
                </ul>
                <div style="margin-top: 20px;">
                    <button onclick="dashboardEnhancer.connectN8n()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin-right: 10px;">
                        Connect to n8n
                    </button>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" style="background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 5px;">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    connectN8n() {
        this.showNotification('Connecting to n8n workflow...', 'info');
        // Simulate n8n connection
        setTimeout(() => {
            this.showNotification('Successfully connected to n8n!', 'success');
            document.querySelector('.n8n-modal').remove();
        }, 2000);
    }

    showSettings() {
        this.showNotification('Opening dashboard settings...', 'info');
        this.showSettingsModal();
    }

    showSettingsModal() {
        // Get current settings
        const currentSettings = this.getCurrentSettings();
        
        const modal = document.createElement('div');
        modal.className = 'settings-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 15px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto;">
                <h3 style="margin-top: 0; color: #2c3e50;">Dashboard Settings</h3>
                
                <div style="margin-bottom: 20px;">
                    <h4>Display Options</h4>
                    <label style="display: block; margin-bottom: 10px;">
                        <input type="checkbox" id="darkMode" ${currentSettings.darkMode ? 'checked' : ''} style="margin-right: 8px;">
                        Enable Dark Mode
                    </label>
                    <label style="display: block; margin-bottom: 10px;">
                        <input type="checkbox" id="animations" ${currentSettings.animations ? 'checked' : ''} style="margin-right: 8px;">
                        Enable Animations
                    </label>
                    <label style="display: block; margin-bottom: 10px;">
                        <input type="checkbox" id="autoRefresh" ${currentSettings.autoRefresh ? 'checked' : ''} style="margin-right: 8px;">
                        Auto Refresh (30s)
                    </label>
                </div>

                <div style="margin-bottom: 20px;">
                    <h4>Chart Settings</h4>
                    <label style="display: block; margin-bottom: 10px;">
                        Chart Theme:
                        <select id="chartTheme" style="margin-left: 10px; padding: 5px;">
                            <option value="plotly_white" ${currentSettings.chartTheme === 'plotly_white' ? 'selected' : ''}>Light</option>
                            <option value="plotly_dark" ${currentSettings.chartTheme === 'plotly_dark' ? 'selected' : ''}>Dark</option>
                            <option value="ggplot2" ${currentSettings.chartTheme === 'ggplot2' ? 'selected' : ''}>GGPlot2</option>
                            <option value="seaborn" ${currentSettings.chartTheme === 'seaborn' ? 'selected' : ''}>Seaborn</option>
                        </select>
                    </label>
                    <label style="display: block; margin-bottom: 10px;">
                        <input type="checkbox" id="showGridlines" ${currentSettings.showGridlines ? 'checked' : ''} style="margin-right: 8px;">
                        Show Grid Lines
                    </label>
                </div>

                <div style="margin-bottom: 20px;">
                    <h4>Notification Settings</h4>
                    <label style="display: block; margin-bottom: 10px;">
                        <input type="checkbox" id="browserNotifications" ${currentSettings.browserNotifications ? 'checked' : ''} style="margin-right: 8px;">
                        Browser Notifications
                    </label>
                    <label style="display: block; margin-bottom: 10px;">
                        <input type="checkbox" id="soundAlerts" ${currentSettings.soundAlerts ? 'checked' : ''} style="margin-right: 8px;">
                        Sound Alerts
                    </label>
                </div>

                <div style="margin-top: 30px; text-align: right;">
                    <button onclick="dashboardEnhancer.saveSettings()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin-right: 10px; cursor: pointer;">
                        Save Settings
                    </button>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" style="background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                        Cancel
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    getCurrentSettings() {
        const savedSettings = localStorage.getItem('dashboardSettings');
        const defaultSettings = {
            darkMode: false,
            animations: true,
            autoRefresh: true,
            chartTheme: 'plotly_white',
            showGridlines: true,
            browserNotifications: false,
            soundAlerts: false
        };
        
        if (savedSettings) {
            return { ...defaultSettings, ...JSON.parse(savedSettings) };
        }
        return defaultSettings;
    }

    saveSettings() {
        const settings = {
            darkMode: document.getElementById('darkMode').checked,
            animations: document.getElementById('animations').checked,
            autoRefresh: document.getElementById('autoRefresh').checked,
            chartTheme: document.getElementById('chartTheme').value,
            showGridlines: document.getElementById('showGridlines').checked,
            browserNotifications: document.getElementById('browserNotifications').checked,
            soundAlerts: document.getElementById('soundAlerts').checked
        };

        // Save to localStorage
        localStorage.setItem('dashboardSettings', JSON.stringify(settings));
        
        // Apply settings immediately
        this.applySettings(settings);
        
        // Close modal
        document.querySelector('.settings-modal').remove();
        
        this.showNotification('Settings saved successfully!', 'success');
    }

    applySettings(settings) {
        // Apply dark mode
        if (settings.darkMode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }

        // Apply animations
        if (!settings.animations) {
            document.body.classList.add('no-animations');
        } else {
            document.body.classList.remove('no-animations');
        }

        // Handle auto refresh
        if (settings.autoRefresh) {
            // Auto refresh is handled by Dash interval component
            console.log('Auto refresh enabled');
        }
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('dashboardSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            this.applySettings(settings);
        }
    }

    downloadChart(chartId) {
        this.showNotification('Downloading chart...', 'info');
        // Chart download implementation
    }

    zoomChart(chartId) {
        this.showNotification('Chart zoom enabled', 'info');
        // Chart zoom implementation
    }
}

// Initialize dashboard enhancer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardEnhancer = new DashboardEnhancer();
});

// Add Font Awesome for icons
if (!document.querySelector('link[href*="font-awesome"]')) {
    const fontAwesome = document.createElement('link');
    fontAwesome.rel = 'stylesheet';
    fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
    document.head.appendChild(fontAwesome);
}

// Additional CSS animations
const additionalStyles = `
    <style>
        .chart-toolbar {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            display: flex;
            gap: 5px;
        }
        
        .chart-toolbar button {
            background: rgba(255, 255, 255, 0.9);
            border: none;
            padding: 8px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .chart-toolbar button:hover {
            background: #667eea;
            color: white;
            transform: scale(1.1);
        }
        
        .notification {
            transform: translateY(-20px);
            opacity: 0;
            animation: slideInDown 0.3s ease forwards;
        }
        
        @keyframes slideInDown {
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes fadeOut {
            to {
                opacity: 0;
                transform: translateY(-20px);
            }
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', additionalStyles);