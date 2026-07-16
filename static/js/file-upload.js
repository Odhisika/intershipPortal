/**
 * File Upload Label Update
 * Updates the file input label when a file is selected
 */
document.addEventListener('DOMContentLoaded', () => {
    var fileInput = document.getElementById('attachment_letter');
    var fileLabel = document.getElementById('file-label');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileLabel.textContent = this.files[0].name;
            } else {
                fileLabel.textContent = 'Drag and drop or Browse';
            }
        });
    }
});
