/**
 * Contact Form Handler for Django Backend
 * Sabor Con Flow Dance Studio
 *
 * Provides client-side validation and AJAX form submission with CSRF token.
 */
(function() {
    'use strict';

    const form = document.getElementById('contact-form');
    if (!form) return;

    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    const successMsg = document.getElementById('form-success');
    const errorMsg = document.getElementById('form-error');
    const errorText = document.getElementById('error-message');
    const messageField = document.getElementById('message');
    const messageCounter = document.getElementById('message-counter');
    const honeypot = document.getElementById('website');

    // Get CSRF token from Django
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // Validation rules
    const validators = {
        name: {
            validate: (value) => value.trim().length >= 2 && value.trim().length <= 100,
            message: 'Name must be between 2 and 100 characters'
        },
        email: {
            validate: (value) => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return emailRegex.test(value.trim()) && value.length <= 254;
            },
            message: 'Please enter a valid email address'
        },
        message: {
            validate: (value) => value.trim().length >= 10 && value.trim().length <= 2000,
            message: 'Message must be between 10 and 2000 characters'
        }
    };

    // Initialize character counter
    function updateCharacterCount() {
        const count = messageField.value.length;
        const max = 2000;
        messageCounter.textContent = `${count} / ${max}`;

        if (count > max * 0.9) {
            messageCounter.classList.add('warning');
        } else {
            messageCounter.classList.remove('warning');
        }

        if (count > max) {
            messageCounter.classList.add('error');
        } else {
            messageCounter.classList.remove('error');
        }
    }

    messageField.addEventListener('input', updateCharacterCount);

    // Validate a single field
    function validateField(field) {
        const name = field.name;
        const value = field.value;
        const errorElement = document.getElementById(`${name}-error`);
        const validator = validators[name];

        if (!validator) return true;

        const isValid = validator.validate(value);

        if (!isValid) {
            field.classList.add('invalid');
            field.classList.remove('valid');
            field.setAttribute('aria-invalid', 'true');
            if (errorElement) {
                errorElement.textContent = validator.message;
            }
        } else {
            field.classList.remove('invalid');
            field.classList.add('valid');
            field.setAttribute('aria-invalid', 'false');
            if (errorElement) {
                errorElement.textContent = '';
            }
        }

        return isValid;
    }

    // Validate all fields
    function validateForm() {
        const fields = form.querySelectorAll('[required]');
        let isValid = true;

        fields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    // Real-time validation on blur
    form.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.classList.contains('invalid')) {
                validateField(input);
            }
        });
    });

    // Set loading state
    function setLoading(loading) {
        submitBtn.disabled = loading;
        btnText.hidden = loading;
        btnLoading.hidden = !loading;

        if (loading) {
            submitBtn.setAttribute('aria-busy', 'true');
        } else {
            submitBtn.removeAttribute('aria-busy');
        }
    }

    // Show message
    function showMessage(type, message) {
        successMsg.hidden = type !== 'success';
        errorMsg.hidden = type !== 'error';

        if (type === 'error' && message) {
            errorText.textContent = message;
        }

        // Scroll to message
        const msgElement = type === 'success' ? successMsg : errorMsg;
        msgElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        msgElement.focus();
    }

    // Hide messages
    function hideMessages() {
        successMsg.hidden = true;
        errorMsg.hidden = true;
    }

    // Reset form
    function resetForm() {
        form.reset();
        form.querySelectorAll('.form-input').forEach(input => {
            input.classList.remove('valid', 'invalid');
            input.removeAttribute('aria-invalid');
        });
        form.querySelectorAll('.form-error-text').forEach(error => {
            error.textContent = '';
        });
        updateCharacterCount();
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Check honeypot (spam protection)
        if (honeypot && honeypot.value) {
            // Silently fail - likely a bot
            showMessage('success');
            resetForm();
            return;
        }

        hideMessages();

        if (!csrfToken) {
            showMessage('error', 'Security token missing. Please refresh the page and try again.');
            return;
        }

        if (!validateForm()) {
            // Focus first invalid field
            const firstInvalid = form.querySelector('.invalid');
            if (firstInvalid) {
                firstInvalid.focus();
            }
            return;
        }

        setLoading(true);

        const formData = new FormData(form);
        const data = {
            name: formData.get('name').trim(),
            email: formData.get('email').trim(),
            subject: formData.get('subject'),
            message: formData.get('message').trim(),
            website: formData.get('website') || ''  // Honeypot
        };

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showMessage('success');
                resetForm();
            } else {
                showMessage('error', result.message || 'Failed to send message. Please try again.');
            }
        } catch (error) {
            console.error('Contact form error:', error);
            showMessage('error', 'Network error. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    });

    // Initialize
    updateCharacterCount();
})();
