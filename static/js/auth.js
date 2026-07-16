/**
 * Authentication-related JavaScript
 * Handles password toggle and modal behaviors
 */

// Password visibility toggle
function togglePassword() {
    var input = document.getElementById('password');
    var icon = document.getElementById('toggleIcon');
    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
}

// Modal close handler
function closeSuspendedModal() {
    var modal = document.getElementById('suspendedModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function closeModalOnOutsideClick() {
    var modal = document.getElementById('suspendedModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeSuspendedModal();
            }
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    closeModalOnOutsideClick();
    
    // Attach click handler to password toggle button
    var toggleBtn = document.querySelector('.icon-right');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', togglePassword);
    }
    
    // Attach click handler to OK button in suspended modal
    var okButton = document.querySelector('#suspendedModal .suspend-ok-btn');
    if (okButton) {
        okButton.addEventListener('click', closeSuspendedModal);
    }
});
