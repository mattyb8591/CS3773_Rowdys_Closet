document.addEventListener('DOMContentLoaded', function() {
    var elUsername = document.getElementById('username');
    var elPassword = document.getElementById('password');
    var loginForm = document.getElementById('loginForm');

    // Client-side validation
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // Basic validation before submitting
            if (!elUsername.value || !elPassword.value) {
                e.preventDefault();
                alert('Please fill in all fields.');
                return;
            }

            if (elUsername.value.length < 5) {
                e.preventDefault();
                alert('Username must be at least 5 characters long.');
                return;
            }

            // Optional: Show loading state
            var submitButton = this.querySelector('button[type="submit"]');
            var originalText = submitButton.textContent;
            submitButton.textContent = 'Logging in...';
            submitButton.disabled = true;

            // Re-enable button after 3 seconds in case submission fails
            setTimeout(() => {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }, 3000);
        });
    }

    // Clear any existing error messages when user starts typing
    if (elUsername) {
        elUsername.addEventListener('input', function() {
            var errorAlert = document.querySelector('.alert-danger');
            if (errorAlert) {
                errorAlert.style.display = 'none';
            }
        });
    }
    
    if (elPassword) {
        elPassword.addEventListener('input', function() {
            var errorAlert = document.querySelector('.alert-danger');
            if (errorAlert) {
                errorAlert.style.display = 'none';
            }
        });
    }
});