// Global variables for order management
let currentPage = 1;
const ordersPerPage = 10;
let allOrders = [];
let filteredOrders = [];
let currentSort = {
    field: 'date',
    direction: 'desc'
};
let currentFilters = {
    status: 'all',
    shipping: 'all'
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('ordersTableBody')) {
        loadOrders();
    }
});

// Load orders from the server
async function loadOrders() {
    showTableLoading(true);
    
    try {
        const response = await fetch('/admin/api/orders');
        if (response.ok) {
            const orders = await response.json();
            allOrders = orders;
            applyFilters();
            applySorting(); // Apply initial sort
            displayOrders();
            setupPagination();
        } else {
            throw new Error('Failed to load orders');
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        showToast('Error loading orders. Please try again.', 'error');
    } finally {
        showTableLoading(false);
    }
}

// Apply filters based on current filter settings
function applyFilters() {
    filteredOrders = allOrders.filter(order => {
        const status = order.dynamic_status || order.order_status || 'Processing';
        const shippingMethod = order.shipping_method || 'standard';
        
        // Status filter
        if (currentFilters.status !== 'all' && status !== currentFilters.status) {
            return false;
        }
        
        // Shipping method filter
        if (currentFilters.shipping !== 'all' && shippingMethod !== currentFilters.shipping) {
            return false;
        }
        
        return true;
    });
    
    currentPage = 1; // Reset to first page when filters change
}

// Apply sorting based on current sort settings
function applySorting() {
    filteredOrders.sort((a, b) => {
        let aValue, bValue;
        
        switch (currentSort.field) {
            case 'date':
                aValue = new Date(a.order_date);
                bValue = new Date(b.order_date);
                break;
            case 'customer':
                aValue = (a.username || '').toLowerCase();
                bValue = (b.username || '').toLowerCase();
                break;
            case 'total':
                aValue = parseFloat(a.total) || 0;
                bValue = parseFloat(b.total) || 0;
                break;
            case 'order_id':
                aValue = a.order_id;
                bValue = b.order_id;
                break;
            case 'status':
                aValue = (a.dynamic_status || a.order_status || '').toLowerCase();
                bValue = (b.dynamic_status || b.order_status || '').toLowerCase();
                break;
            default:
                return 0;
        }
        
        // Handle comparison based on data type
        let result;
        if (currentSort.field === 'date') {
            result = aValue - bValue;
        } else if (currentSort.field === 'customer' || currentSort.field === 'status') {
            result = aValue.localeCompare(bValue);
        } else {
            // For numbers and order_id
            result = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        }
        
        // Apply sort direction
        return currentSort.direction === 'desc' ? -result : result;
    });
    
    updateSortIndicators();
}

// Filter orders based on current filter selections
function filterOrders() {
    const statusFilter = document.getElementById('statusFilter');
    const shippingFilter = document.getElementById('shippingFilter');
    
    currentFilters.status = statusFilter.value;
    currentFilters.shipping = shippingFilter.value;
    
    applyFilters();
    applySorting();
    displayOrders();
    setupPagination();
}

// Sort by specific field (header click)
function sortBy(field) {
    // If clicking the same field, toggle direction
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        // New field, default to descending for dates/numbers, ascending for text
        currentSort.field = field;
        currentSort.direction = (field === 'date' || field === 'total') ? 'desc' : 'asc';
    }
    
    applySorting();
    displayOrders();
    setupPagination();
    
    // Update dropdown to reflect current sort
    updateSortDropdown();
}

// Apply sort from dropdown
function applySort() {
    const sortSelect = document.getElementById('sortSelect');
    const value = sortSelect.value;
    
    const [field, direction] = value.split('-');
    currentSort.field = field;
    currentSort.direction = direction;
    
    applySorting();
    displayOrders();
    setupPagination();
}

// Update sort dropdown to reflect current sort
function updateSortDropdown() {
    const sortSelect = document.getElementById('sortSelect');
    const value = `${currentSort.field}-${currentSort.direction}`;
    sortSelect.value = value;
}

// Update sort indicators in table headers
function updateSortIndicators() {
    // Clear all indicators
    document.querySelectorAll('.sort-indicator').forEach(indicator => {
        indicator.innerHTML = '';
    });
    
    // Set indicator for current sort field
    const indicator = document.getElementById(`sort-${currentSort.field}`);
    if (indicator) {
        indicator.innerHTML = currentSort.direction === 'asc' ? '↑' : '↓';
    }
}

// Display orders in the table
function displayOrders() {
    const tableBody = document.getElementById('ordersTableBody');
    const startIndex = (currentPage - 1) * ordersPerPage;
    const endIndex = startIndex + ordersPerPage;
    const ordersToDisplay = filteredOrders.slice(startIndex, endIndex);

    if (ordersToDisplay.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-receipt" style="font-size: 2rem;"></i>
                        <p class="mt-2">No orders found matching your filters</p>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="resetFilters()">
                            Reset Filters
                        </button>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = ordersToDisplay.map(order => {
        const status = order.dynamic_status || order.order_status || 'Processing';
        const statusClass = getStatusClass(status);
        
        return `
            <tr>
                <td>${order.order_id}</td>
                <td class="customer-column">
                    <strong>${escapeHtml(order.username)}</strong>
                    <br>
                    <small class="text-muted">ID: ${order.customer_id}</small>
                </td>
                <td>$${parseFloat(order.total).toFixed(2)}</td>
                <td>
                    <span class="badge status-badge ${statusClass}">${status}</span>
                </td>
                <td>${order.shipping_method ? formatShippingMethod(order.shipping_method) : '<span class="text-muted">Standard</span>'}</td>
                <td>${formatDate(order.order_date)}</td>
                <td>${order.discount_code ? escapeHtml(order.discount_code) : '<span class="text-muted">None</span>'}</td>
            </tr>
        `;
    }).join('');
}

// Search orders
function searchOrders() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    filteredOrders = allOrders.filter(order => {
        const status = order.dynamic_status || order.order_status || '';
        return order.username.toLowerCase().includes(searchTerm) ||
               order.order_id.toString().includes(searchTerm) ||
               (order.discount_code && order.discount_code.toLowerCase().includes(searchTerm)) ||
               status.toLowerCase().includes(searchTerm) ||
               (order.shipping_method && order.shipping_method.toLowerCase().includes(searchTerm));
    });
    
    // Reapply sorting after filtering
    applySorting();
    currentPage = 1;
    displayOrders();
    setupPagination();
}

// Reset filters and sorting
function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = 'all';
    document.getElementById('shippingFilter').value = 'all';
    document.getElementById('sortSelect').value = 'date-desc';
    
    filteredOrders = [...allOrders];
    currentSort = { field: 'date', direction: 'desc' };
    currentFilters = { status: 'all', shipping: 'all' };
    currentPage = 1;
    
    applySorting();
    displayOrders();
    setupPagination();
}

// Refresh orders
function refreshOrders() {
    loadOrders();
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function getStatusClass(status) {
    const statusClasses = {
        'Processing': 'status-processing',
        'Shipped': 'status-shipped',
        'Out for Delivery': 'status-out-for-delivery',
        'In Transit': 'status-in-transit',
        'Delivered': 'status-delivered',
        'Ready for Pickup': 'status-ready-for-pickup',
        'Picked Up': 'status-picked-up'
    };
    return statusClasses[status] || 'status-processing';
}

function formatShippingMethod(method) {
    const methodNames = {
        'standard': 'Standard Delivery',
        'express': 'Express Delivery',
        'pickup': 'Store Pickup'
    };
    return methodNames[method] || method;
}

// Reuse utility functions from list.js
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

function showTableLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const tableBody = document.getElementById('ordersTableBody');
    const pagination = document.getElementById('pagination');
    
    if (show) {
        spinner.classList.remove('d-none');
        if (tableBody) tableBody.innerHTML = '';
        if (pagination) pagination.innerHTML = '';
    } else {
        spinner.classList.add('d-none');
    }
}

function showToast(message, type = 'info') {
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
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Setup pagination
function setupPagination() {
    const pagination = document.getElementById('pagination');
    const pageCount = Math.ceil(filteredOrders.length / ordersPerPage);
    
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
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(pageCount, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
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
    displayOrders();
    setupPagination();
}