document.addEventListener('DOMContentLoaded', function() {
// Utility function to show modal
    function showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('hidden');
    }

    // Utility function to hide modal
    function hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('hidden');
    }

    // Attach event listeners to user management buttons
    function setupUserManagement() {
        const userTable = document.getElementById('userTableBody');
        
        if (userTable) {
            console.log("User table found. Setting up event listeners...");
    
            userTable.addEventListener('click', function(event) {
                console.log("Click detected:", event.target);
    
                const changePasswordBtn = event.target.closest('.change-password-btn');
                const deleteUserBtn = event.target.closest('.delete-user-btn');
    
                if (changePasswordBtn) {
                    console.log("Change Password button clicked");
                    const userId = changePasswordBtn.getAttribute('data-user-id');
                    showModal('passwordModal');
    
                    // Store user ID in save button
                    const saveBtn = document.getElementById('savePasswordBtn');
                    if (saveBtn) saveBtn.setAttribute('data-user-id', userId);
                }
    
                if (deleteUserBtn) {
                    console.log("Delete button clicked");
                    const userId = deleteUserBtn.getAttribute('data-user-id');
                    
                    if (confirm('Are you sure you want to delete this user?')) {
                        fetch(`/api/users/${userId}`, { 
                            method: 'DELETE',
                            headers: { 'Content-Type': 'application/json' }
                        })
                        .then(response => {
                            if (response.ok) {
                                const userRow = deleteUserBtn.closest('tr');
                                if (userRow) {
                                    userRow.remove();
                                }
                                alert('User deleted successfully');
                            } else {
                                return response.text().then(errorMsg => {
                                    throw new Error(errorMsg || 'Failed to delete user');
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert(error.message || 'An error occurred while deleting the user');
                        });
                    }
                }
            });
        } else {
            console.error("User table not found!");
        }

        // Handle password change submission
        const savePasswordBtn = document.getElementById('savePasswordBtn');
        if (savePasswordBtn) {
            savePasswordBtn.addEventListener('click', function() {
                const userId = this.getAttribute('data-user-id');
                const newPassword = document.getElementById('newPassword').value;

                if (!newPassword) {
                    alert('Please enter a new password');
                    return;
                }

                fetch(`/api/users/${userId}/reset-password`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ newPassword: newPassword })
                })
                .then(response => {
                    if (response.ok) {
                        alert('Password updated successfully');
                        hideModal('passwordModal');
                        // Clear the password input
                        document.getElementById('newPassword').value = '';
                    } else {
                        // Try to parse error message
                        return response.text().then(errorMsg => {
                            throw new Error(errorMsg || 'Failed to update password');
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert(error.message || 'An error occurred while updating the password');
                });
            });
        }

        // Close modal button
        const closeModalBtn = document.getElementById('closePasswordModalBtn');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => hideModal('passwordModal'));
        }
    }

    // Initialize user management
    setupUserManagement();
});