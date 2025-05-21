/**
 * Main JavaScript for Dev.to Post Analyzer
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission animation
    const analyzeForm = document.getElementById('analyze-form');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            submitButton.disabled = true;
        });
    }
    
    // Toggle password visibility for API key field
    const apiKeyField = document.getElementById('api_key');
    if (apiKeyField) {
        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.className = 'toggle-password';
        toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
        toggleButton.style.position = 'absolute';
        toggleButton.style.right = '40px';
        toggleButton.style.top = '50%';
        toggleButton.style.transform = 'translateY(-50%)';
        toggleButton.style.background = 'none';
        toggleButton.style.border = 'none';
        toggleButton.style.cursor = 'pointer';
        toggleButton.style.color = '#555';
        
        // Add to parent
        apiKeyField.parentElement.style.position = 'relative';
        apiKeyField.parentElement.appendChild(toggleButton);
        
        // Add event listener
        toggleButton.addEventListener('click', function() {
            if (apiKeyField.type === 'password') {
                apiKeyField.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                apiKeyField.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    }
    
    // Tab buttons for results page
    const initTabs = function() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        if (tabButtons.length > 0) {
            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    // Remove active class from all buttons and contents
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabContents.forEach(content => content.classList.remove('active'));
                    
                    // Add active class to clicked button
                    button.classList.add('active');
                    
                    // Show corresponding tab content
                    const tabId = button.dataset.tab;
                    document.getElementById(tabId).classList.add('active');
                });
            });
        }
    };
    
    // Initialize tabs if present
    initTabs();
});