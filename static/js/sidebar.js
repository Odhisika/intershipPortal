/**
 * Sidebar Toggle Functionality
 * Handles toggle for both student portal and admin sidebar
 */

// Student portal sidebar toggle
function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    }
}

// Admin sidebar toggle
function toggleAdminSidebar() {
    var sidebar = document.getElementById('adminSidebar');
    var overlay = document.getElementById('adminSidebarOverlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    }
}

// Auto-attach click handlers if elements exist
document.addEventListener('DOMContentLoaded', () => {
    // Student portal toggle button
    var studentToggle = document.querySelector('.mobile-menu-btn');
    if (studentToggle) {
        studentToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    }
    
    // Student sidebar close button
    var studentClose = document.querySelector('.sidebar-close');
    if (studentClose) {
        studentClose.addEventListener('click', toggleSidebar);
    }
    
    // Admin toggle button
    var adminToggle = document.querySelector('[onclick="toggleAdminSidebar()"]');
    if (adminToggle) {
        adminToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleAdminSidebar();
        });
    }
    
    // Admin sidebar close button
    var adminClose = document.querySelector('.admin-sidebar .sidebar-close');
    if (adminClose) {
        adminClose.addEventListener('click', toggleAdminSidebar);
    }
    
    // Overlay click handlers
    var sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }
    
    var adminSidebarOverlay = document.getElementById('adminSidebarOverlay');
    if (adminSidebarOverlay) {
        adminSidebarOverlay.addEventListener('click', toggleAdminSidebar);
    }
});
