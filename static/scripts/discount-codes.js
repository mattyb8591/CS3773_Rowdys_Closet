// Global variables for discount management
let currentPage = 1;
const discountsPerPage = 10;
let allDiscounts = [];
let filteredDiscounts = [];
let discountToDelete = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDiscounts();
});

// Load discounts from the server
async function loadDiscounts() {
    showTableLoading(true);
    
    try {
        const response = await fetch('/admin/api/discounts');
        if (response.ok) {
            const discounts = await response.json();
            allDiscounts = discounts;
            filteredDiscounts = [...discounts];
            displayDiscounts();
            setupPagination();
        } else {
            throw new Error('Failed to load discount codes');
        }
    } catch (error) {
        console.error('Error loading discount codes:', error);
        showToast('Error loading discount codes. Please try again.', 'error');
    } finally {
        showTableLoading(false);
    }
}

// Display discounts in the table
function displayDiscounts() {
    const tableBody = document.getElementById('discountsTableBody');
    const startIndex = (currentPage - 1) * discountsPerPage;
    const endIndex = startIndex + discountsPerPage;
    const discountsToDisplay = filteredDiscounts.slice(startIndex, endIndex);

    if (discountsToDisplay.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-tag" style="font-size: 2rem;"></i>
                        <p class="mt-2">No discount codes found</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = discountsToDisplay.map(discount => {
        const isExpired = discount.expiration_date && new Date(discount.expiration_date) < new Date();
        const isActive = discount.is_active && !isExpired;
        const statusClass = isExpired ? 'status-expired' : (isActive ? 'status-active' : 'status-inactive');
        const statusText = isExpired ? 'Expired' : (isActive ? 'Active' : 'Inactive');
        
        return `
        <tr>
            <td>
                <strong>${escapeHtml(discount.code)}</strong>
            </td>
            <td>
                <span class="${discount.discount_type === 'percentage' ? 'discount-percentage' : 'discount-fixed'}">
                    ${discount.discount_type === 'percentage' ? 'Percentage' : 'Fixed Amount'}
                </span>
            </td>
            <td>
                ${discount.discount_type === 'percentage' ? 
                    `<strong>${discount.value}%</strong>` : 
                    `<strong>$${parseFloat(discount.value).toFixed(2)}</strong>`
                }
            </td>
            <td>
                ${discount.min_purchase > 0 ? `$${parseFloat(discount.min_purchase).toFixed(2)}` : '<span class="text-muted">None</span>'}
            </td>
            <td>
                ${discount.expiration_date ? 
                    new Date(discount.expiration_date).toLocaleDateString() : 
                    '<span class="text-muted">No expiration</span>'
                }
            </td>
            <td>
                <span class="${statusClass}">
                    ${statusText}
                </span>
            </td>
            <td class="actions">
                <button class="btn btn-sm btn-primary" onclick="editDiscount(${discount.discount_id})" title="Edit Discount">
                    <i class="bi bi-pencil"></i> Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteDiscount(${discount.discount_id}, '${escapeHtml(discount.code)}')" title="Delete Discount">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </td>
        </tr>
        `;
    }).join('');
}

// Search discounts
function searchDiscounts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    
    filteredDiscounts = allDiscounts.filter(discount => {
        const matchesSearch = discount.code.toLowerCase().includes(searchTerm);
        
        const matchesType = !typeFilter || discount.discount_type === typeFilter;
        
        // Handle status filtering
        const isExpired = discount.expiration_date && new Date(discount.expiration_date) < new Date();
        const isActive = discount.is_active && !isExpired;
        let matchesStatus = true;
        
        if (statusFilter === 'active') {
            matchesStatus = isActive;
        } else if (statusFilter === 'inactive') {
            matchesStatus = !isActive && !isExpired;
        } else if (statusFilter === 'expired') {
            matchesStatus = isExpired;
        }
        
        return matchesSearch && matchesType && matchesStatus;
    });
    
    currentPage = 1;
    displayDiscounts();
    setupPagination();
}

// Filter discounts
function filterDiscounts() {
    searchDiscounts();
}

// Reset filters
function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    filteredDiscounts = [...allDiscounts];
    currentPage = 1;
    displayDiscounts();
    setupPagination();
}

// Setup pagination
function setupPagination() {
    const pagination = document.getElementById('pagination');
    const pageCount = Math.ceil(filteredDiscounts.length / discountsPerPage);
    
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
    displayDiscounts();
    setupPagination();
}

// Open add discount modal
function openAddDiscountModal() {
    document.getElementById('discountModalLabel').textContent = 'Add New Discount Code';
    document.getElementById('discountForm').reset();
    document.getElementById('discountId').value = '';
    document.getElementById('discount_type').value = 'percentage';
    document.getElementById('is_active').checked = true;
    
    const modal = new bootstrap.Modal(document.getElementById('discountModal'));
    modal.show();
}

// Edit discount
async function editDiscount(discountId) {
    try {
        const response = await fetch(`/admin/api/discounts/${discountId}`);
        if (response.ok) {
            const discount = await response.json();
            
            document.getElementById('discountModalLabel').textContent = 'Edit Discount Code';
            document.getElementById('discountId').value = discount.discount_id;
            document.getElementById('code').value = discount.code;
            document.getElementById('discount_type').value = discount.discount_type;
            document.getElementById('value').value = discount.value;
            document.getElementById('min_purchase').value = discount.min_purchase || 0;
            document.getElementById('expiration_date').value = discount.expiration_date || '';
            document.getElementById('is_active').checked = discount.is_active;
            
            const modal = new bootstrap.Modal(document.getElementById('discountModal'));
            modal.show();
        } else {
            throw new Error('Failed to load discount data');
        }
    } catch (error) {
        console.error('Error loading discount:', error);
        showToast('Error loading discount data. Please try again.', 'error');
    }
}

// Save discount (add or update)
async function saveDiscount() {
    const form = document.getElementById('discountForm');
    const formData = new FormData(form);
    const discountData = Object.fromEntries(formData.entries());
    
    const discountId = document.getElementById('discountId').value;
    const isEdit = !!discountId;
    
    // Convert numeric fields
    discountData.value = parseFloat(discountData.value);
    discountData.min_purchase = parseFloat(discountData.min_purchase) || 0;
    discountData.is_active = document.getElementById('is_active').checked;
    
    // Validate required fields
    if (!discountData.code || !discountData.value) {
        showToast('Code and value are required.', 'error');
        return;
    }
    
    // Validate discount value based on type
    if (discountData.discount_type === 'percentage' && (discountData.value < 0 || discountData.value > 100)) {
        showToast('Percentage discount must be between 0 and 100.', 'error');
        return;
    }
    
    const url = isEdit ? `/admin/api/discounts/${discountId}` : '/admin/api/discounts';
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(discountData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('discountModal'));
            modal.hide();
            await loadDiscounts(); // Reload the discount list
            showToast(isEdit ? 'Discount code updated successfully!' : 'Discount code added successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to save discount code');
        }
    } catch (error) {
        console.error('Error saving discount code:', error);
        showToast('Error saving discount code: ' + error.message, 'error');
    }
}

// Delete discount confirmation
function deleteDiscount(discountId, code) {
    discountToDelete = discountId;
    document.getElementById('deleteDiscountCode').textContent = code;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteDiscountModal'));
    modal.show();
}

// Confirm and execute deletion
async function confirmDiscountDelete() {
    if (!discountToDelete) return;
    
    try {
        const response = await fetch(`/admin/api/discounts/${discountToDelete}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteDiscountModal'));
            modal.hide();
            await loadDiscounts(); // Reload the discount list
            showToast('Discount code deleted successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to delete discount code');
        }
    } catch (error) {
        console.error('Error deleting discount code:', error);
        showToast('Error deleting discount code: ' + error.message, 'error');
    } finally {
        discountToDelete = null;
    }
}

// Show/hide loading spinner for table
function showTableLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const tableBody = document.getElementById('discountsTableBody');
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