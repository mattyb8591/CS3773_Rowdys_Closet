// Global variables for user management
let currentPage = 1;
const usersPerPage = 10;
let allUsers = [];
let filteredUsers = [];
let userToDelete = null;

// Global variables for product management
let allProducts = [];
let filteredProducts = [];
let productToDelete = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check which page we're on and initialize accordingly
    if (document.getElementById('usersTableBody')) {
        loadUsers();
    }
    if (document.getElementById('productsTableBody')) {
        initializeProductPage();
        loadProducts();
    }
});

// ==================== SHARED UTILITY FUNCTIONS ====================

// Reset filters for products
function resetProductFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('sizeFilter').value = '';
    document.getElementById('stockFilter').value = '';
    document.getElementById('saleFilter').value = '';
    filteredProducts = [...allProducts];
    currentPage = 1;
    displayProducts();
    setupPagination();
}

// Reset filters for users
function resetUserFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('roleFilter').value = '';
    filteredUsers = [...allUsers];
    currentPage = 1;
    displayUsers();
    setupPagination();
}

// Universal reset function that detects which page we're on
function resetFilters() {
    if (document.getElementById('productsTableBody')) {
        resetProductFilters();
    } else if (document.getElementById('usersTableBody')) {
        resetUserFilters();
    }
}

// Setup pagination
function setupPagination() {
    const pagination = document.getElementById('pagination');
    const items = document.getElementById('usersTableBody') ? filteredUsers : filteredProducts;
    const pageCount = Math.ceil(items.length / usersPerPage);
    
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
    if (document.getElementById('usersTableBody')) {
        displayUsers();
    }
    if (document.getElementById('productsTableBody')) {
        displayProducts();
    }
    setupPagination();
}

// Show/hide loading spinner for table
function showTableLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const tableBody = document.getElementById('usersTableBody') || document.getElementById('productsTableBody');
    const pagination = document.getElementById('pagination');
    
    if (show) {
        spinner.classList.remove('d-none');
        if (tableBody) tableBody.innerHTML = '';
        if (pagination) pagination.innerHTML = '';
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

// ==================== USER MANAGEMENT FUNCTIONS ====================

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
    searchUsers();
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

// ==================== PRODUCT MANAGEMENT FUNCTIONS ====================

// Initialize product page
function initializeProductPage() {
    // Add event listeners for price and discount calculations
    document.getElementById('price').addEventListener('input', calculateSalePrice);
    document.getElementById('discount').addEventListener('input', calculateSalePrice);
}

// Calculate and display sale price
function calculateSalePrice() {
    const price = parseFloat(document.getElementById('price').value) || 0;
    const discount = parseFloat(document.getElementById('discount').value) || 0;
    
    const salePrice = price * (1 - discount / 100);
    const savings = price - salePrice;
    
    document.getElementById('salePriceValue').textContent = salePrice.toFixed(2);
    
    if (discount > 0) {
        document.getElementById('savingsAmount').textContent = `Save $${savings.toFixed(2)} (${discount}% off)`;
        document.getElementById('salePriceDisplay').style.backgroundColor = '#d4edda';
    } else {
        document.getElementById('savingsAmount').textContent = 'No discount applied';
        document.getElementById('salePriceDisplay').style.backgroundColor = '#f8f9fa';
    }
}

// Load products from the server
async function loadProducts() {
    showTableLoading(true);
    
    try {
        const response = await fetch('/admin/api/products');
        if (response.ok) {
            const products = await response.json();
            allProducts = products;
            
            // Apply current filters to the new data
            if (document.getElementById('searchInput').value || 
                document.getElementById('typeFilter').value || 
                document.getElementById('sizeFilter').value || 
                document.getElementById('stockFilter').value ||
                document.getElementById('saleFilter').value) {
                searchProducts(); // This will apply current filters
            } else {
                filteredProducts = [...allProducts];
                displayProducts();
                setupPagination();
            }
        } else {
            throw new Error('Failed to load products');
        }
    } catch (error) {
        console.error('Error loading products:', error);
        showToast('Error loading products. Please try again.', 'error');
    } finally {
        showTableLoading(false);
    }
}

// Display products in the table - Updated to show database price
function displayProducts() {
    const tableBody = document.getElementById('productsTableBody');
    const startIndex = (currentPage - 1) * usersPerPage;
    const endIndex = startIndex + usersPerPage;
    const productsToDisplay = filteredProducts.slice(startIndex, endIndex);

    if (productsToDisplay.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-box" style="font-size: 2rem;"></i>
                        <p class="mt-2">No products found</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = productsToDisplay.map(product => {
        // Use the actual price from database instead of calculating it
        const discount = product.discount || 0;
        const hasDiscount = discount > 0;
        // Use the price field from database which should be the calculated sale price
        const salePrice = product.price || product.original_price * (1 - discount / 100);
        
        return `
        <tr>
            <td>
                ${product.img_file_path ? 
                    `<img src="${escapeHtml(product.img_file_path)}" alt="${escapeHtml(product.name)}" class="img-thumbnail">` : 
                    '<div class="text-muted text-center">No Image</div>'
                }
            </td>
            <td>
                <strong>${escapeHtml(product.name)}</strong>
                ${product.description ? `<br><small class="text-muted">${escapeHtml(product.description.substring(0, 50))}${product.description.length > 50 ? '...' : ''}</small>` : ''}
            </td>
            <td>
                <span class="badge bg-secondary category-badge">${escapeHtml(product.type)}</span>
            </td>
            <td>
                <span class="badge bg-info size-badge">${escapeHtml(product.size || 'One Size')}</span>
            </td>
            <td>
                ${hasDiscount ? 
                    `<div>
                        <span class="price-original">$${parseFloat(product.original_price).toFixed(2)}</span>
                        <br>
                        <span class="price-sale">$${parseFloat(salePrice).toFixed(2)}</span>
                    </div>` : 
                    `$${parseFloat(product.original_price).toFixed(2)}`
                }
            </td>
            <td>
                ${hasDiscount ? 
                    `<span class="badge bg-danger discount-badge">${discount}% OFF</span>` : 
                    '<span class="text-muted">—</span>'
                }
            </td>
            <td>
                <span class="${product.stock === 0 ? 'stock-low' : product.stock < 10 ? 'stock-low' : 'stock-ok'}">
                    ${product.stock}
                </span>
            </td>
            <td class="actions">
                <button class="btn btn-sm btn-primary" onclick="editProduct(${product.product_id})" title="Edit Product">
                    <i class="bi bi-pencil"></i> Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.product_id}, '${escapeHtml(product.name)}')" title="Delete Product">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </td>
        </tr>
        `;
    }).join('');
}

// Search products
function searchProducts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    const sizeFilter = document.getElementById('sizeFilter').value;
    const stockFilter = document.getElementById('stockFilter').value;
    const saleFilter = document.getElementById('saleFilter').value;
    
    filteredProducts = allProducts.filter(product => {
        const matchesSearch = product.name.toLowerCase().includes(searchTerm) ||
                            (product.description && product.description.toLowerCase().includes(searchTerm));
        
        const matchesType = !typeFilter || product.type === typeFilter;
        
        // Handle size filtering (NULL sizes are "One Size")
        const productSize = product.size || 'One Size';
        const matchesSize = !sizeFilter || productSize === sizeFilter;
        
        const matchesStock = !stockFilter || 
            (stockFilter === 'low' && product.stock < 10 && product.stock > 0) ||
            (stockFilter === 'out' && product.stock === 0) ||
            (stockFilter === 'in' && product.stock > 0);
            
        // FIXED: Handle sale filtering - properly check discount status
        let matchesSale = true;
        if (saleFilter) {
            // Get discount value, treating NULL as 0 and ensuring it's a number
            const discount = product.discount ? parseFloat(product.discount) : 0;
            
            if (saleFilter === 'sale') {
                matchesSale = discount > 0;
            } else if (saleFilter === 'regular') {
                matchesSale = discount === 0;
            }
        }
        
        return matchesSearch && matchesType && matchesSize && matchesStock && matchesSale;
    });
    
    currentPage = 1;
    displayProducts();
    setupPagination();
}

// Filter products
function filterProducts() {
    searchProducts();
}

// Open add product modal
function openAddProductModal() {
    document.getElementById('productModalLabel').textContent = 'Add New Product';
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    document.getElementById('discount').value = '0';
    
    calculateSalePrice(); // Initialize sale price display
    
    const modal = new bootstrap.Modal(document.getElementById('productModal'));
    modal.show();
}


// Edit product
async function editProduct(productId) {
    try {
        const response = await fetch(`/admin/api/products/${productId}`);
        if (response.ok) {
            const product = await response.json();
            
            document.getElementById('productModalLabel').textContent = 'Edit Product';
            document.getElementById('productId').value = product.product_id;
            document.getElementById('name').value = product.name;
            document.getElementById('description').value = product.description || '';
            document.getElementById('type').value = product.type;
            document.getElementById('price').value = product.original_price;
            document.getElementById('discount').value = product.discount || '0';
            
            // Handle NULL size - convert to "One Size" for the form
            const displaySize = product.size || 'One Size';
            document.getElementById('size').value = displaySize;
            
            document.getElementById('stock').value = product.stock;
            document.getElementById('img_file_path').value = product.img_file_path || '';
            
            // Calculate and display sale price
            calculateSalePrice();
            
            const modal = new bootstrap.Modal(document.getElementById('productModal'));
            modal.show();
        } else {
            throw new Error('Failed to load product data');
        }
    } catch (error) {
        console.error('Error loading product:', error);
        showToast('Error loading product data. Please try again.', 'error');
    }
}

// Check if product already exists (for duplicate validation)
function checkForDuplicateProduct(productData, currentProductId = null) {
    return allProducts.some(product => {
        // Skip the current product when editing
        if (currentProductId && product.product_id === currentProductId) {
            return false;
        }
        
        // Handle NULL discounts (treat as 0 for comparison)
        const productDiscount = product.discount || 0;
        const newProductDiscount = productData.discount || 0;
        
        // Compare all relevant fields
        return product.name === productData.name &&
               product.type === productData.type &&
               product.size === productData.size &&
               parseFloat(product.original_price) === parseFloat(productData.original_price) &&
               parseFloat(productDiscount) === parseFloat(newProductDiscount) &&
               product.description === (productData.description || '') &&
               product.img_file_path === (productData.img_file_path || '');
    });
}

async function saveProduct() {
    const form = document.getElementById('productForm');
    const formData = new FormData(form);
    let productData = Object.fromEntries(formData.entries());
    
    // Convert "One Size" to NULL for database storage
    if (productData.size === 'One Size') {
        productData.size = null;
    }
    
    // Convert numeric fields
    productData.original_price = parseFloat(productData.price);
    productData.discount = parseFloat(productData.discount) || 0;
    productData.stock = parseInt(productData.stock);
    
    // Handle empty strings for optional fields
    if (!productData.description) productData.description = '';
    if (!productData.img_file_path) productData.img_file_path = '';
    
    const productId = document.getElementById('productId').value;
    const isEdit = !!productId;
    
    // Validate required fields
    if (!productData.name || !productData.type || !productData.original_price || productData.stock === '') {
        showToast('Name, type, original price, and stock are required.', 'error');
        return;
    }
    
    // Validate discount range
    if (productData.discount < 0 || productData.discount > 100) {
        showToast('Discount must be between 0 and 100 percent.', 'error');
        return;
    }
    
    // Size is required but can be "One Size" (which becomes NULL)
    if (!productData.size && productData.size !== null) {
        showToast('Size is required.', 'error');
        return;
    }
    
    // Check for duplicate product
    if (checkForDuplicateProduct(productData, isEdit ? parseInt(productId) : null)) {
        showToast('A product with these exact attributes already exists. Please modify at least one attribute.', 'error');
        return;
    }
    
    const url = isEdit ? `/admin/api/products/${productId}` : '/admin/api/products';
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
            modal.hide();
            
            // Show success message indicating which changes were applied
            let successMessage = isEdit ? 'Product updated successfully!' : 'Product added successfully!';
            successMessage += ' Product details (name, description, price, discount, type, image) applied to all sizes. Stock updated only for this size.';
            
            // Save current filter state before reloading
            const currentSearch = document.getElementById('searchInput').value;
            const currentType = document.getElementById('typeFilter').value;
            const currentSize = document.getElementById('sizeFilter').value;
            const currentStock = document.getElementById('stockFilter').value;
            const currentSale = document.getElementById('saleFilter').value;
            
            await loadProducts(); // Reload the product list
            
            // Try to restore the previous page and selection
            if (currentSearch || currentType || currentSize || currentStock || currentSale) {
                // If filters were active, they will be reapplied by loadProducts()
                // Try to find and select the edited/added product
                setTimeout(() => {
                    const editedProductId = isEdit ? parseInt(productId) : result.product_id;
                    highlightProductRow(editedProductId);
                }, 100);
            } else {
                // No filters, just go to first page
                currentPage = 1;
                displayProducts();
                setupPagination();
                
                // Highlight the edited/added product
                setTimeout(() => {
                    const editedProductId = isEdit ? parseInt(productId) : result.product_id;
                    highlightProductRow(editedProductId);
                }, 100);
            }
            
            showToast(successMessage, 'success');
        } else {
            throw new Error(result.error || 'Failed to save product');
        }
    } catch (error) {
        console.error('Error saving product:', error);
        showToast('Error saving product: ' + error.message, 'error');
    }
}



// Delete product confirmation
function deleteProduct(productId, productName) {
    productToDelete = productId;
    document.getElementById('deleteProductName').textContent = productName;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteProductModal'));
    modal.show();
}

// Confirm and execute product deletion
async function confirmProductDelete() {
    if (!productToDelete) return;
    
    try {
        const response = await fetch(`/admin/api/products/${productToDelete}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteProductModal'));
            modal.hide();
            await loadProducts(); // Reload the product list
            showToast('Product deleted successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to delete product');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        showToast('Error deleting product: ' + error.message, 'error');
    } finally {
        productToDelete = null;
    }
}

// Highlight a product row after edit/add (optional enhancement)
function highlightProductRow(productId) {
    const rows = document.querySelectorAll('#productsTableBody tr');
    rows.forEach(row => {
        // Remove any existing highlights
        row.classList.remove('table-success');
        
        // Check if this row contains the product ID
        const firstCell = row.querySelector('td:first-child');
        if (firstCell && firstCell.textContent.includes(productId)) {
            row.classList.add('table-success');
            
            // Scroll to the row if it's not visible
            row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });
}