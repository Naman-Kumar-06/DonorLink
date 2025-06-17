// DonorLink - Charts and Data Visualization
// Advanced chart configurations and utilities for the admin dashboard

// Chart.js global configuration
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#495057';
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;

// Color schemes for consistent theming
const CHART_COLORS = {
    primary: '#0d6efd',
    success: '#198754', 
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
    dark: '#212529',
    light: '#f8f9fa'
};

const BLOOD_TYPE_COLORS = {
    'A+': '#FF6384',
    'A-': '#36A2EB', 
    'B+': '#FFCE56',
    'B-': '#4BC0C0',
    'AB+': '#9966FF',
    'AB-': '#FF9F40',
    'O+': '#FF6384',
    'O-': '#C9CBCF'
};

const URGENCY_COLORS = {
    'normal': CHART_COLORS.success,
    'urgent': CHART_COLORS.warning,
    'critical': CHART_COLORS.danger
};

// Chart initialization functions
class DonorLinkCharts {
    constructor() {
        this.charts = {};
        this.initializeCharts();
    }

    initializeCharts() {
        // Initialize all charts on page load
        this.initBloodTypeChart();
        this.initUrgencyChart();
        this.initInventoryChart();
        this.initTrendCharts();
        this.initRealTimeCharts();
    }

    // Blood Type Distribution Doughnut Chart
    initBloodTypeChart() {
        const canvas = document.getElementById('bloodTypeChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Get data from the page (passed from Flask)
        let chartData = {};
        try {
            chartData = JSON.parse(canvas.dataset.chartData || '{}');
        } catch (e) {
            console.warn('Could not parse blood type chart data');
            chartData = this.generateSampleBloodTypeData();
        }

        this.charts.bloodType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(chartData),
                datasets: [{
                    data: Object.values(chartData),
                    backgroundColor: Object.keys(chartData).map(type => 
                        BLOOD_TYPE_COLORS[type] || CHART_COLORS.primary
                    ),
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 3,
                    hoverBorderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} donors (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1500
                }
            }
        });
    }

    // Request Urgency Bar Chart
    initUrgencyChart() {
        const canvas = document.getElementById('urgencyChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        let chartData = {};
        try {
            chartData = JSON.parse(canvas.dataset.chartData || '{}');
        } catch (e) {
            console.warn('Could not parse urgency chart data');
            chartData = this.generateSampleUrgencyData();
        }

        const labels = Object.keys(chartData).map(key => 
            key.charAt(0).toUpperCase() + key.slice(1)
        );
        const data = Object.values(chartData);
        const backgroundColors = Object.keys(chartData).map(key => 
            URGENCY_COLORS[key] || CHART_COLORS.primary
        );

        this.charts.urgency = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Requests',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors,
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return Number.isInteger(value) ? value : '';
                            }
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `${context[0].label} Priority`;
                            },
                            label: function(context) {
                                const value = context.parsed.y;
                                return `${value} request${value !== 1 ? 's' : ''}`;
                            }
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Blood Inventory Horizontal Bar Chart
    initInventoryChart() {
        const canvas = document.getElementById('inventoryChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        let inventoryData = {};
        try {
            inventoryData = JSON.parse(canvas.dataset.inventoryData || '{}');
        } catch (e) {
            console.warn('Could not parse inventory data');
            inventoryData = this.generateSampleInventoryData();
        }

        const bloodTypes = Object.keys(inventoryData);
        const units = bloodTypes.map(type => inventoryData[type].units || 0);
        const backgroundColors = units.map(unit => {
            if (unit < 10) return CHART_COLORS.danger;
            if (unit < 20) return CHART_COLORS.warning;
            return CHART_COLORS.success;
        });

        this.charts.inventory = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: bloodTypes,
                datasets: [{
                    label: 'Units Available',
                    data: units,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 10
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Blood Type: ${context[0].label}`;
                            },
                            label: function(context) {
                                const value = context.parsed.x;
                                const status = value < 10 ? ' (Critical)' : 
                                             value < 20 ? ' (Low)' : ' (Good)';
                                return `${value} units available${status}`;
                            }
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Monthly Trends Line Chart
    initTrendCharts() {
        const canvas = document.getElementById('trendsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Generate sample trend data for the last 12 months
        const months = this.getLast12Months();
        const donorData = this.generateTrendData(months.length, 20, 50);
        const requestData = this.generateTrendData(months.length, 10, 30);

        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'New Donors',
                        data: donorData,
                        borderColor: CHART_COLORS.success,
                        backgroundColor: this.addAlpha(CHART_COLORS.success, 0.1),
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: CHART_COLORS.success,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    },
                    {
                        label: 'Blood Requests',
                        data: requestData,
                        borderColor: CHART_COLORS.primary,
                        backgroundColor: this.addAlpha(CHART_COLORS.primary, 0.1),
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: CHART_COLORS.primary,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 5
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#ffffff',
                        borderWidth: 1
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Real-time updating charts
    initRealTimeCharts() {
        // Start real-time updates every 30 seconds
        setInterval(() => {
            this.updateChartsWithLiveData();
        }, 30000);
    }

    // Update charts with live data
    updateChartsWithLiveData() {
        // Fetch live data from API
        this.fetchAnalyticsData()
            .then(data => {
                this.updateBloodTypeChart(data.blood_type_distribution);
                this.updateUrgencyChart(data.urgency_distribution);
            })
            .catch(error => {
                console.warn('Could not fetch live data:', error);
            });
    }

    // Fetch analytics data from API
    async fetchAnalyticsData() {
        try {
            const response = await fetch('/api/analytics');
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.warn('Analytics API not available, using sample data');
            return {
                blood_type_distribution: this.generateSampleBloodTypeData(),
                urgency_distribution: this.generateSampleUrgencyData()
            };
        }
    }

    // Update blood type chart with new data
    updateBloodTypeChart(newData) {
        if (!this.charts.bloodType || !newData) return;

        const chart = this.charts.bloodType;
        chart.data.labels = Object.keys(newData);
        chart.data.datasets[0].data = Object.values(newData);
        chart.update('none'); // Update without animation
    }

    // Update urgency chart with new data
    updateUrgencyChart(newData) {
        if (!this.charts.urgency || !newData) return;

        const chart = this.charts.urgency;
        chart.data.labels = Object.keys(newData).map(key => 
            key.charAt(0).toUpperCase() + key.slice(1)
        );
        chart.data.datasets[0].data = Object.values(newData);
        chart.update('none'); // Update without animation
    }

    // Utility functions
    addAlpha(color, alpha) {
        const hex = color.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    getLast12Months() {
        const months = [];
        const now = new Date();
        
        for (let i = 11; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            months.push(date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }));
        }
        
        return months;
    }

    generateTrendData(length, min, max) {
        const data = [];
        for (let i = 0; i < length; i++) {
            data.push(Math.floor(Math.random() * (max - min + 1)) + min);
        }
        return data;
    }

    // Sample data generators for fallback
    generateSampleBloodTypeData() {
        return {
            'O+': 35,
            'A+': 28,
            'B+': 20,
            'AB+': 12,
            'O-': 15,
            'A-': 10,
            'B-': 8,
            'AB-': 5
        };
    }

    generateSampleUrgencyData() {
        return {
            'normal': 65,
            'urgent': 20,
            'critical': 8
        };
    }

    generateSampleInventoryData() {
        return {
            'A+': { units: 45 },
            'A-': { units: 25 },
            'B+': { units: 38 },
            'B-': { units: 18 },
            'AB+': { units: 15 },
            'AB-': { units: 12 },
            'O+': { units: 52 },
            'O-': { units: 28 }
        };
    }

    // Public methods for external use
    refreshAllCharts() {
        Object.values(this.charts).forEach(chart => {
            chart.update();
        });
    }

    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            chart.destroy();
        });
        this.charts = {};
    }

    exportChartAsPNG(chartId) {
        const chart = this.charts[chartId];
        if (!chart) return;

        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `donorlink-${chartId}-chart.png`;
        link.href = url;
        link.click();
    }
}

// Chart interaction utilities
class ChartInteractions {
    static addHoverEffects() {
        // Add custom hover effects to chart containers
        const chartContainers = document.querySelectorAll('.chart-container');
        
        chartContainers.forEach(container => {
            container.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.02)';
                this.style.transition = 'transform 0.3s ease';
            });

            container.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }

    static addClickToExport() {
        // Add click-to-export functionality
        document.addEventListener('click', function(e) {
            if (e.target.matches('.export-chart-btn')) {
                const chartId = e.target.dataset.chartId;
                if (window.donorLinkCharts) {
                    window.donorLinkCharts.exportChartAsPNG(chartId);
                }
            }
        });
    }

    static addFullscreenToggle() {
        // Add fullscreen toggle for charts
        document.addEventListener('click', function(e) {
            if (e.target.matches('.fullscreen-chart-btn')) {
                const chartContainer = e.target.closest('.card');
                if (chartContainer.requestFullscreen) {
                    chartContainer.requestFullscreen();
                }
            }
        });
    }
}

// Performance monitoring for charts
class ChartPerformance {
    static monitorRenderTime() {
        const originalRender = Chart.prototype.render;
        
        Chart.prototype.render = function() {
            const start = performance.now();
            const result = originalRender.apply(this, arguments);
            const end = performance.now();
            
            console.log(`Chart ${this.canvas.id} rendered in ${(end - start).toFixed(2)}ms`);
            
            return result;
        };
    }

    static optimizeAnimations() {
        // Disable animations on low-performance devices
        if (navigator.hardwareConcurrency < 4) {
            Chart.defaults.animation = false;
            console.log('Chart animations disabled for performance');
        }
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize performance monitoring
    ChartPerformance.monitorRenderTime();
    ChartPerformance.optimizeAnimations();
    
    // Initialize charts
    window.donorLinkCharts = new DonorLinkCharts();
    
    // Add interactions
    ChartInteractions.addHoverEffects();
    ChartInteractions.addClickToExport();
    ChartInteractions.addFullscreenToggle();
    
    console.log('DonorLink charts initialized successfully');
});

// Handle window resize
window.addEventListener('resize', function() {
    if (window.donorLinkCharts) {
        setTimeout(() => {
            window.donorLinkCharts.refreshAllCharts();
        }, 100);
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DonorLinkCharts, ChartInteractions, ChartPerformance };
}
