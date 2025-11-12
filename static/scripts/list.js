// static/scripts/list.js

let currentPage = 1;
const usersPerPage = 10;
let allUsers = [];
let filteredUsers = [];
let userToDelete = null;

// Load users from the server
async function loadUsers() {
    showTableLoading(true);
    
    try {
        const response = await fetch('/admin/api/users');
        if (response.ok) {
            const users = await response.json();
            allUsers = users;
            filteredUsers = [...users];
            displayUsers();
            setupPagination();
        } else {
            throw new Error('Failed to load users');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showToast('Error loading users. Please try again.', 'error');
    } finally {
        showTableLoading(false);
    }
}

// Display users in the table
function displayUsers() {
    const tableBody = document.getElementById('usersTableBody');
    const startIndex = (currentPage - 1) * usersPerPage;
    const endIndex = startIndex + usersPerPage;
    const usersToDisplay = filteredUsers.slice(startIndex, endIndex);

    if (usersToDisplay.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-people" style="font-size: 2rem;"></i>
                        <p class="mt-2">No users found</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = usersToDisplay.map(user => `
        <tr>
            <td>${user.user_id}</td>
            <td>
                <strong>${escapeHtml(user.username)}</strong>
            </td>
            <td>${escapeHtml(user.email)}</td>
            <td>${user.phone_number ? escapeHtml(user.phone_number) : '<span class="text-muted">N/A</span>'}</td>
            <td class="address-column">${user.full_address ? escapeHtml(user.full_address) : '<span class="text-muted">No address</span>'}</td>
            <td>
                <span class="${user.user_role === 'Admin' ? 'role-admin' : 'role-customer'}">
                    ${user.user_role}
                </span>
            </td>
            <td class="actions">
                <button class="btn btn-sm btn-primary" onclick="editUser(${user.user_id})" title="Edit User">
                    <i class="bi bi-pencil"></i> Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.user_id}, '${escapeHtml(user.username)}')" title="Delete User">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </td>
        </tr>
    `).join('');
}

// Setup pagination
function setupPagination() {
    const pagination = document.getElementById('pagination');
    const pageCount = Math.ceil(filteredUsers.length / usersPerPage);
    
    if (pageCount <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Previous</a>
        </li>
    `;
    
    // Page numbers
    for (let i = 1; i <= pageCount; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${currentPage === pageCount ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Next</a>
        </li>
    `;
    
    pagination.innerHTML = paginationHTML;
}

// Change page
function changePage(page) {
    currentPage = page;
    displayUsers();
    setupPagination();
}

// Search users
function searchUsers() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const roleFilter = document.getElementById('roleFilter').value;
    
    filteredUsers = allUsers.filter(user => {
        const matchesSearch = user.username.toLowerCase().includes(searchTerm) ||
                            user.email.toLowerCase().includes(searchTerm) ||
                            (user.phone_number && user.phone_number.toLowerCase().includes(searchTerm)) ||
                            (user.full_address && user.full_address.toLowerCase().includes(searchTerm));
        
        const matchesRole = !roleFilter || user.user_role === roleFilter;
        
        return matchesSearch && matchesRole;
    });
    
    currentPage = 1;
    displayUsers();
    setupPagination();
}

// Filter users by role
function filterUsers() {
    searchUsers(); // Reuse search function which handles both search and filters
}

// Reset filters
function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('roleFilter').value = '';
    filteredUsers = [...allUsers];
    currentPage = 1;
    displayUsers();
    setupPagination();
}

// Open add user modal
function openAddUserModal() {
    document.getElementById('userModalLabel').textContent = 'Add New User';
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('user_role').value = 'Customer';
    document.getElementById('passwordHelp').textContent = 'Required for new users';
    document.getElementById('password').required = true;
    
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
}

// Edit user
async function editUser(userId) {
    // Don't show table loading for edit - we want the table to remain visible
    try {
        const response = await fetch(`/admin/api/users/${userId}`);
        if (response.ok) {
            const user = await response.json();
            
            document.getElementById('userModalLabel').textContent = 'Edit User';
            document.getElementById('userId').value = user.user_id;
            document.getElementById('username').value = user.username;
            document.getElementById('email').value = user.email;
            document.getElementById('phone_number').value = user.phone_number || '';
            document.getElementById('street_number').value = user.street_number || '';
            document.getElementById('street_name').value = user.street_name || '';
            document.getElementById('city').value = user.city || '';
            document.getElementById('state_abrev').value = user.state_abrev || '';
            document.getElementById('zip_code').value = user.zip_code || '';
            document.getElementById('user_role').value = user.user_role;
            document.getElementById('password').value = '';
            document.getElementById('passwordHelp').textContent = 'Leave blank to keep current password';
            document.getElementById('password').required = false;
            
            const modal = new bootstrap.Modal(document.getElementById('userModal'));
            modal.show();
        } else {
            throw new Error('Failed to load user data');
        }
    } catch (error) {
        console.error('Error loading user:', error);
        showToast('Error loading user data. Please try again.', 'error');
    }
}

// Save user (add or update)
async function saveUser() {
    const form = document.getElementById('userForm');
    const formData = new FormData(form);
    const userData = Object.fromEntries(formData.entries());
    
    const userId = document.getElementById('userId').value;
    const isEdit = !!userId;
    
    // Validate required fields
    if (!userData.username || !userData.email) {
        showToast('Username and email are required.', 'error');
        return;
    }
    
    if (!isEdit && !userData.password) {
        showToast('Password is required for new users.', 'error');
        return;
    }
    
    // Remove empty address fields if all are empty
    if (!userData.street_number && !userData.street_name && !userData.city && !userData.state_abrev && !userData.zip_code) {
        userData.street_number = '';
        userData.street_name = '';
        userData.city = '';
        userData.state_abrev = '';
        userData.zip_code = '';
    }
    
    const url = isEdit ? `/admin/api/users/${userId}` : '/admin/api/users';
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
            modal.hide();
            await loadUsers(); // Reload the user list
            showToast(isEdit ? 'User updated successfully!' : 'User added successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to save user');
        }
    } catch (error) {
        console.error('Error saving user:', error);
        showToast('Error saving user: ' + error.message, 'error');
    }
}

// Delete user confirmation
function deleteUser(userId, username) {
    userToDelete = userId;
    document.getElementById('deleteUserName').textContent = username;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Confirm and execute deletion
async function confirmDelete() {
    if (!userToDelete) return;
    
    try {
        const response = await fetch(`/admin/api/users/${userToDelete}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
            modal.hide();
            await loadUsers(); // Reload the user list
            showToast('User deleted successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showToast('Error deleting user: ' + error.message, 'error');
    } finally {
        userToDelete = null;
    }
}

// Show/hide loading spinner for table
function showTableLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const tableBody = document.getElementById('usersTableBody');
    const pagination = document.getElementById('pagination');
    
    if (show) {
        spinner.classList.remove('d-none');
        tableBody.innerHTML = '';
        pagination.innerHTML = '';
    } else {
        spinner.classList.add('d-none');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Utility function to escape HTML
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}