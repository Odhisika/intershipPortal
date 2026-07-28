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
    // Student portal toggle button (only on portal pages with a sidebar)
    var studentToggle = document.querySelector('.portal-layout .mobile-menu-btn');
    if (studentToggle) {
        studentToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    }
    
    // Student sidebar close button
    var studentClose = document.querySelector('.sidebar:not(.admin-sidebar) .sidebar-close');
    if (studentClose) {
        studentClose.addEventListener('click', toggleSidebar);
    }
    
    // Admin toggle button (onclick attribute handles it on admin pages)
    var adminToggle = document.querySelector('.admin-header .mobile-menu-btn:not([onclick])');
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
