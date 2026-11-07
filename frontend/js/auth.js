/**
 * SmartLearn - Authentication Script (Vanilla JS)
 * Fully compliant with Issue 14:
 * - Calls POST /auth/login with { email, password }
 * - Calls POST /auth/register with { full_name, email, password, role }
 * - Displays error message from backend when login or registration fails
 * - Saves JWT access token on success and redirects to dashboard
 */

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const alertContainer = document.getElementById('authAlert');

  // Helper to show alert message
  function showAlert(message, type = 'danger') {
    if (!alertContainer) return;
    alertContainer.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;
    alertContainer.classList.remove('d-none');
  }

  // Handle Login Form Submit
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = loginForm.querySelector('button[type="submit"]');
      const email = document.getElementById('email')?.value.trim();
      const password = document.getElementById('password')?.value;

      if (!email || !password) {
        showAlert('Please enter both your email address and password.', 'warning');
        return;
      }

      const originalBtnText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Signing in...`;

      try {
        // Call backend API via SmartLearnAPI helper: POST /auth/login
        const result = await window.SmartLearnAPI.auth.login(email, password);

        if (result.success && result.data && result.data.access_token) {
          showAlert('Login successful! Redirecting to dashboard...', 'success');
          setTimeout(() => {
            window.location.href = 'dashboard.html';
          }, 600);
        } else {
          // Show actual error message from backend
          const errorMsg = result.error || (result.data && result.data.detail) || 'Invalid email or password.';
          showAlert(errorMsg, 'danger');
        }
      } catch (err) {
        showAlert(err.message || 'Unable to connect to the backend server. Please try again.', 'danger');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }

  // Handle Register Form Submit
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = registerForm.querySelector('button[type="submit"]');
      const fullName = document.getElementById('fullName')?.value.trim();
      const email = document.getElementById('email')?.value.trim();
      const password = document.getElementById('password')?.value;
      const role = document.getElementById('roleSelect')?.value || 'student';

      if (!fullName || !email || !password) {
        showAlert('Please fill in all required fields.', 'warning');
        return;
      }

      if (password.length < 8) {
        showAlert('Password must be at least 8 characters long.', 'danger');
        return;
      }

      const originalBtnText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Creating account...`;

      try {
        // Backend expects: { full_name, email, password, role }
        const result = await window.SmartLearnAPI.auth.register({
          full_name: fullName,
          email,
          password,
          role
        });

        if (result.success) {
          showAlert('Account created successfully! Redirecting to login...', 'success');
          setTimeout(() => {
            window.location.href = 'login.html';
          }, 800);
        } else {
          // Show actual error message from backend
          const errorMsg = result.error || (result.data && result.data.detail) || 'Registration failed. Please check your inputs.';
          showAlert(errorMsg, 'danger');
        }
      } catch (err) {
        showAlert(err.message || 'Unable to connect to the server. Please try again.', 'danger');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }
});
