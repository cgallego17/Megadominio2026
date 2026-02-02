// Main JavaScript for Megadominio

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe service cards and benefit icons
    document.querySelectorAll('.service-card, .benefit-icon').forEach(el => {
        observer.observe(el);
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth < 768) {
            if (sidebar && !sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Loading states for buttons
    document.querySelectorAll('.btn-loading').forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Cargando...';
            
            // Simulate loading (remove this in production)
            setTimeout(() => {
                this.disabled = false;
                this.innerHTML = originalText;
            }, 2000);
        });
    });

    // Copy to clipboard functionality
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check me-2"></i>¡Copiado!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });

    // Auto-resize textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Chart animations (if Chart.js is available)
    if (typeof Chart !== 'undefined') {
        // Default chart options
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.color = '#6c757d';
        
        // Animate charts on scroll
        document.querySelectorAll('canvas[data-chart]').forEach(canvas => {
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        // Trigger chart animation
                        const chart = Chart.getChart(canvas);
                        if (chart) {
                            chart.update();
                        }
                        observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);
            
            observer.observe(canvas);
        });
    }

    // Print functionality
    document.querySelectorAll('.print-btn').forEach(button => {
        button.addEventListener('click', function() {
            const printContent = document.querySelector(this.getAttribute('data-print'));
            if (printContent) {
                const printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>Imprimir</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 20px; }
                                .no-print { display: none; }
                                @media print { .no-print { display: none; } }
                            </style>
                        </head>
                        <body>
                            ${printContent.innerHTML}
                        </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.print();
            }
        });
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.toLowerCase();
            const searchTarget = document.querySelector(this.getAttribute('data-search-target'));
            
            if (searchTarget) {
                searchTimeout = setTimeout(() => {
                    const items = searchTarget.querySelectorAll('.search-item');
                    items.forEach(item => {
                        const text = item.textContent.toLowerCase();
                        if (text.includes(searchTerm)) {
                            item.style.display = '';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                }, 300);
            }
        });
    });

    // Modal auto-focus
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Dynamic table sorting
    document.querySelectorAll('.sortable-table').forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', function() {
                const column = this.getAttribute('data-sort');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    const aText = a.querySelector(`td[data-column="${column}"]`).textContent.trim();
                    const bText = b.querySelector(`td[data-column="${column}"]`).textContent.trim();
                    return aText.localeCompare(bText);
                });
                
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    });

    console.log('Megadominio JavaScript initialized successfully!');
});

// Utility functions
window.Megadominio = {
    // Show notification
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    },
    
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('es-HN', {
            style: 'currency',
            currency: 'HNL'
        }).format(amount);
    },
    
    // Format date
    formatDate: function(date, format = 'short') {
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
        };
        
        return new Date(date).toLocaleDateString('es-HN', options[format]);
    },
    
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};
