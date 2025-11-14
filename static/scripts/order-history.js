// Global variables for order management
let currentPage = 1;
const ordersPerPage = 10;
let allOrders = [];
let filteredOrders = [];

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
            filteredOrders = [...orders];
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
                        <p class="mt-2">No orders found</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = ordersToDisplay.map(order => `
        <tr>
            <td>${order.order_id}</td>
            <td class="customer-column">
                <strong>${escapeHtml(order.username)}</strong>
                <br>
                <small class="text-muted">ID: ${order.customer_id}</small>
            </td>
            <td>$${parseFloat(order.total).toFixed(2)}</td>
            <td>${order.discount_code ? escapeHtml(order.discount_code) : '<span class="text-muted">None</span>'}</td>
            <td>${formatDate(order.order_date)}</td>
            <td>${order.payment_type ? escapeHtml(order.payment_type) : '<span class="text-muted">N/A</span>'}</td>
            <td>${order.shipping_method ? escapeHtml(order.shipping_method) : '<span class="text-muted">Standard</span>'}</td>
        </tr>
    `).join('');
}

// Search orders
function searchOrders() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    filteredOrders = allOrders.filter(order => {
        return order.username.toLowerCase().includes(searchTerm) ||
               order.order_id.toString().includes(searchTerm) ||
               (order.discount_code && order.discount_code.toLowerCase().includes(searchTerm)) ||
               (order.payment_type && order.payment_type.toLowerCase().includes(searchTerm));
    });
    
    currentPage = 1;
    displayOrders();
    setupPagination();
}

// Reset filters
function resetFilters() {
    document.getElementById('searchInput').value = '';
    filteredOrders = [...allOrders];
    currentPage = 1;
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
    displayOrders();
    setupPagination();
}
