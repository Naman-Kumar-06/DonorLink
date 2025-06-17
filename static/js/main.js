// DonorLink - Main JavaScript Functions
// Blood Donation Management System

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize all components
    initializeTooltips();
    initializePopovers();
    initializeModals();
    initializeFormValidation();
    initializeTableFilters();
    initializeCharts();
    initializeNotifications();
    initializeAnimations();
    
    console.log('DonorLink application initialized successfully');
}

// Bootstrap Components Initialization
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function initializeModals() {
    // Auto-dismiss modals after form submission
    const forms = document.querySelectorAll('.modal form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const modal = form.closest('.modal');
            if (modal) {
                setTimeout(() => {
                    bootstrap.Modal.getInstance(modal)?.hide();
                }, 1000);
            }
        });
    });
}

// Form Validation
function initializeFormValidation() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Password confirmation validation
    const confirmPasswordInputs = document.querySelectorAll('input[name="confirm_password"]');
    confirmPasswordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = document.querySelector('input[name="password"]').value;
            const confirmPassword = this.value;
            
            if (password !== confirmPassword) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length >= 6) {
                value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 3) {
                value = value.replace(/(\d{3})(\d{3})/, '($1) $2');
            }
            this.value = value;
        });
    });
}

// Table Filtering
function initializeTableFilters() {
    const filterInputs = document.querySelectorAll('[id$="Filter"]');
    filterInputs.forEach(filter => {
        filter.addEventListener('change', function() {
            filterTable(this);
        });
    });
}

function filterTable(filterElement) {
    const tableId = filterElement.id.replace('Filter', 'Table');
    const table = document.getElementById(tableId);
    
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const filters = table.parentElement.querySelectorAll('[id$="Filter"]');
    
    rows.forEach(row => {
        let showRow = true;
        
        filters.forEach(filter => {
            const filterValue = filter.value.toLowerCase();
            const attributeName = filter.id.replace('Filter', '').replace(/([A-Z])/g, '-$1').toLowerCase();
            const rowValue = row.getAttribute('data-' + attributeName);
            
            if (filterValue && rowValue && !rowValue.toLowerCase().includes(filterValue)) {
                showRow = false;
            }
        });
        
        row.style.display = showRow ? '' : 'none';
    });
    
    // Update table info
    updateTableInfo(table);
}

function updateTableInfo(table) {
    const totalRows = table.querySelectorAll('tbody tr').length;
    const visibleRows = table.querySelectorAll('tbody tr:not([style*="display: none"])').length;
    
    const infoElement = table.parentElement.querySelector('.table-info');
    if (infoElement) {
        infoElement.textContent = `Showing ${visibleRows} of ${totalRows} entries`;
    }
}

// Charts Initialization
function initializeCharts() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.log('Chart.js not loaded');
        return;
    }

    // Set default chart options
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;
    
    // Initialize dashboard charts if on admin dashboard
    if (document.getElementById('bloodTypeChart')) {
        initializeDashboardCharts();
    }
}

function initializeDashboardCharts() {
    // Blood Type Distribution Chart
    const bloodTypeCanvas = document.getElementById('bloodTypeChart');
    if (bloodTypeCanvas) {
        const ctx = bloodTypeCanvas.getContext('2d');
        const bloodTypeData = JSON.parse(bloodTypeCanvas.dataset.chartData || '{}');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(bloodTypeData),
                datasets: [{
                    data: Object.values(bloodTypeData),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Request Urgency Chart
    const urgencyCanvas = document.getElementById('urgencyChart');
    if (urgencyCanvas) {
        const ctx = urgencyCanvas.getContext('2d');
        const urgencyData = JSON.parse(urgencyCanvas.dataset.chartData || '{}');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(urgencyData).map(key => 
                    key.charAt(0).toUpperCase() + key.slice(1)
                ),
                datasets: [{
                    label: 'Number of Requests',
                    data: Object.values(urgencyData),
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Notifications
function initializeNotifications() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Animations
function initializeAnimations() {
    // Fade in animation for cards
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                entry.target.style.transition = 'all 0.6s ease';
                
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    });
    
    cards.forEach(card => {
        observer.observe(card);
    });

    // Blood drop pulse animation
    const bloodDrops = document.querySelectorAll('.blood-drop-animation i');
    bloodDrops.forEach(drop => {
        setInterval(() => {
            drop.style.transform = 'scale(1.1)';
            setTimeout(() => {
                drop.style.transform = 'scale(1)';
            }, 500);
        }, 2000);
    });
}

// Utility Functions
function showLoading(element) {
    element.classList.add('loading');
    element.setAttribute('disabled', 'disabled');
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.removeAttribute('disabled');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^\(\d{3}\) \d{3}-\d{4}$/;
    return phoneRegex.test(phone);
}

// Blood Type Compatibility Functions
const BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'AB+'],
    'A-': ['A+', 'A-', 'AB+', 'AB-'],
    'B+': ['B+', 'AB+'],
    'B-': ['B+', 'B-', 'AB+', 'AB-'],
    'AB+': ['AB+'],
    'AB-': ['AB+', 'AB-'],
    'O+': ['A+', 'B+', 'AB+', 'O+'],
    'O-': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
};

function getCompatibleBloodTypes(donorType) {
    return BLOOD_COMPATIBILITY[donorType] || [];
}

function canDonateToBloodType(donorType, recipientType) {
    const compatibleTypes = BLOOD_COMPATIBILITY[donorType] || [];
    return compatibleTypes.includes(recipientType);
}

// Emergency Functions
function callEmergency() {
    if (confirm('This will attempt to call emergency services (911). Continue?')) {
        window.location.href = 'tel:911';
    }
}

// Export functions for use in other scripts
window.DonorLink = {
    showLoading,
    hideLoading,
    showNotification,
    formatDate,
    formatDateTime,
    validateEmail,
    validatePhone,
    getCompatibleBloodTypes,
    canDonateToBloodType,
    callEmergency
};

console.log('DonorLink main.js loaded successfully');
