/**
 * Confirmation Modal Functionality
 * Handles delete/suspend confirmation modals
 * Reads data from HTML data attributes instead of template variables
 */

function showConfirmModal(action, studentName) {
    var modal = document.getElementById('confirmModal');
    var icon = document.getElementById('modalIcon');
    var title = document.getElementById('modalTitle');
    var message = document.getElementById('modalMessage');
    var confirmBtn = document.getElementById('modalConfirmBtn');
    var actionInput = document.getElementById('confirmAction');

    if (!modal || !icon || !title || !message || !confirmBtn) {
        console.error('Confirmation modal elements not found');
        return;
    }

    if (action === 'delete') {
        icon.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
        icon.style.color = '#dc2626';
        title.textContent = 'Delete Student?';
        message.textContent = 'Are you sure you want to permanently delete ' + studentName + ' and all associated records? This cannot be undone.';
        confirmBtn.className = 'btn btn-primary';
        confirmBtn.style.background = '#dc2626';
        confirmBtn.textContent = 'Delete';
    } else {
        icon.innerHTML = '<i class="fa-solid fa-pause"></i>';
        icon.style.color = '#f59e0b';
        title.textContent = 'Suspend Student?';
        message.textContent = 'Are you sure you want to suspend ' + studentName + '? They will not be able to log in until reinstated.';
        confirmBtn.className = 'btn btn-primary';
        confirmBtn.style.background = '#f59e0b';
        confirmBtn.textContent = 'Suspend';
    }

    if (actionInput) {
        actionInput.value = action;
    }
    modal.style.display = 'flex';
}

function hideConfirmModal() {
    var modal = document.getElementById('confirmModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    var modal = document.getElementById('confirmModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                hideConfirmModal();
            }
        });
        
        // Attach click handler to Cancel button
        var cancelBtn = document.querySelector('#confirmModal .cancel-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', hideConfirmModal);
        }
        
        // Attach click handlers to action buttons (suspend/delete)
        var actionButtons = document.querySelectorAll('[data-action][data-student]');
        actionButtons.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var action = this.getAttribute('data-action');
                var studentName = this.getAttribute('data-student');
                showConfirmModal(action, studentName);
            });
        });
    }
});
