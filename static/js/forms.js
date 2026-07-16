/**
 * Form-related JavaScript
 * Handles auto-submit on change and payment amount selection
 */

// Auto-submit form on select change
function initAutoSubmitForms() {
    // Admin attendance date filter
    var dateFilter = document.getElementById('date');
    if (dateFilter && dateFilter.form) {
        dateFilter.addEventListener('change', function() {
            this.form.submit();
        });
    }
    
    // Admin students cohort filter
    var cohortFilter = document.getElementById('cohort');
    if (cohortFilter && cohortFilter.form) {
        cohortFilter.addEventListener('change', function() {
            this.form.submit();
        });
    }
    
    // Admin students status filter
    var statusFilter = document.getElementById('status');
    if (statusFilter && statusFilter.form) {
        statusFilter.addEventListener('change', function() {
            this.form.submit();
        });
    }
    
    // Mentor curriculum course filter
    var courseFilter = document.getElementById('course');
    if (courseFilter && courseFilter.form) {
        courseFilter.addEventListener('change', function() {
            this.form.submit();
        });
    }
}

// Payment amount selection
function initPaymentAmountSelectors() {
    var paymentLinks = document.querySelectorAll('.payment-quick-links a[data-amount]');
    paymentLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var amount = parseFloat(this.getAttribute('data-amount'));
            document.getElementById('amount').value = amount;
            return false;
        });
    });
}

// Delete confirmation
function initDeleteConfirmations() {
    // Handle buttons with data-confirm attribute
    var deleteButtons = document.querySelectorAll('button[data-confirm]');
    deleteButtons.forEach(function(btn) {
        var message = btn.getAttribute('data-confirm');
        if (message) {
            btn.addEventListener('click', function(e) {
                return confirm(message);
            });
        }
    });
    
    // Also handle legacy onclick attributes
    var legacyButtons = document.querySelectorAll('button[onclick*="confirm"]');
    legacyButtons.forEach(function(btn) {
        var onclick = btn.getAttribute('onclick');
        var messageMatch = onclick.match(/confirm\(\s*['"]([^'"]+)['"]\s*\)/);
        if (messageMatch) {
            var message = messageMatch[1];
            btn.addEventListener('click', function(e) {
                return confirm(message);
            });
            // Remove the onclick attribute
            btn.removeAttribute('onclick');
        }
    });
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initAutoSubmitForms();
    initPaymentAmountSelectors();
    initDeleteConfirmations();
});
