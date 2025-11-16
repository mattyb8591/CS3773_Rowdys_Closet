document.addEventListener('DOMContentLoaded', function () {
    console.log('Search page loaded');
    
    // Update year in footer
    document.getElementById('year').textContent = new Date().getFullYear();
    
    // Load search results if query exists
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');
    
    if (searchQuery && searchQuery.trim() !== '') {
        console.log('Initial search query found:', searchQuery);
        loadSearchResults(searchQuery);
    } else {
        console.log('No search query found in URL');
    }
    
    // Add search suggestions functionality
    initializeSearchSuggestions();
});

function loadSearchResults(query) {
    console.log('Loading search results for:', query);
    
    const resultsContainer = document.getElementById('searchResultsContainer');
    const resultsCount = document.getElementById('resultsCount');
    
    if (!resultsContainer) {
        console.error('Search results container not found');
        return;
    }
    
    // Show loading state
    resultsContainer.innerHTML = '<div class="loading-message">Searching for "' + escapeHtml(query) + '"...</div>';
    
    if (resultsCount) {
        resultsCount.innerHTML = 'Searching for "' + escapeHtml(query) + '"...';
    }
    
    // Fetch search results from API
    fetch(`/search/api/search?q=${encodeURIComponent(query)}`)
        .then(response => {
            console.log('API response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Search results received:', data);
            console.log('Number of unique products:', data.results ? data.results.length : 0);
            
            if (data.error) {
                throw new Error(data.error);
            }
            displaySearchResults(data.results, data.count, query);
        })
        .catch(error => {
            console.error('Error loading search results:', error);
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <h3>Error loading search results</h3>
                    <p>Please try again later.</p>
                    <p><small>Error: ${escapeHtml(error.message)}</small></p>
                </div>
            `;
            if (resultsCount) {
                resultsCount.innerHTML = `Error searching for "${escapeHtml(query)}"`;
            }
        });
}

function displaySearchResults(products, count, query) {
    const resultsContainer = document.getElementById('searchResultsContainer');
    const resultsCount = document.getElementById('resultsCount');
    
    if (!resultsContainer) return;
    
    console.log(`Displaying ${count} unique products for query: ${query}`);
    
    // Update results count
    if (resultsCount) {
        resultsCount.innerHTML = `Found <strong>${count}</strong> unique product${count !== 1 ? 's' : ''} for "${escapeHtml(query)}"`;
    }
    
    if (!products || products.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <h3>No products found</h3>
                <p>Try different keywords or browse our <a href="/home/">home page</a>.</p>
                <p><small>Searched for: "${escapeHtml(query)}"</small></p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Track displayed product names for debugging
    const displayedProducts = [];
    
    products.forEach(product => {
        console.log('Displaying unique product:', product.name);
        displayedProducts.push(product.name);
        
        const isOutOfStock = product.stock <= 0;
        const stockStatus = isOutOfStock ? 'Out of Stock' : `${product.stock} in stock`;
        const stockClass = isOutOfStock ? 'out-of-stock' : 'in-stock';
        const hasDiscount = product.discount && product.discount > 0;
        
        // Handle image path
        let imageHtml = '';
        if (product.img_file_path) {
            imageHtml = `<img src="${product.img_file_path}" alt="${product.name}" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">`;
        }
        
        // Price display with discount
        let priceDisplay = `$${parseFloat(product.price || 0).toFixed(2)}`;
        let discountBadge = '';

        if (hasDiscount && product.original_price) {
            const originalPrice = parseFloat(product.original_price);
            const currentPrice = parseFloat(product.price);
            priceDisplay = `
                <div class="price-with-discount">
                    <span class="original-price">$${originalPrice.toFixed(2)}</span>
                    <span class="discounted-price">$${currentPrice.toFixed(2)}</span>
                </div>
            `;
            discountBadge = `<span class="discount-badge">-${Math.round(product.discount)}% OFF</span>`;
        }
                
        html += `
            <div class="search-product-card">
                <div class="product-image">
                    ${imageHtml}
                    ${discountBadge}
                    <div class="no-image-placeholder" ${product.img_file_path ? 'style="display:none;"' : ''}>
                        No Image
                    </div>
                </div>
                
                <div class="product-details">
                    <h3 class="product-name">${escapeHtml(product.name)}</h3>
                    <p class="product-type">${escapeHtml(product.type)}</p>
                    <p class="product-description">${escapeHtml(product.description || 'No description available')}</p>
                    
                    <div class="product-meta">
                        <div class="product-price ${hasDiscount ? 'has-discount' : ''}">
                            ${priceDisplay}
                        </div>
                        <div class="product-stock ${stockClass}">
                            ${stockStatus}
                        </div>
                    </div>
                    
                    ${isOutOfStock ? 
                        '<button class="btn btn-secondary" disabled>Out of Stock</button>' : 
                        `<a href="/item/${product.product_id}" class="btn btn-primary view-item-btn">
                            View Item
                         </a>`
                    }
                </div>
            </div>
        `;
    });
    
    console.log('Total unique products displayed:', displayedProducts.length);
    console.log('Displayed product names:', displayedProducts);
    
    resultsContainer.innerHTML = html;
}

function initializeSearchSuggestions() {
    const searchInput = document.getElementById('site-search');
    const suggestionsList = document.getElementById('search-suggestions');
    const searchForm = document.getElementById('searchBarGroup');
    
    if (!searchInput || !suggestionsList) {
        console.log('Search suggestions elements not found');
        return;
    }
    
    let currentFocus = -1;
    let debounceTimer;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous debounce timer
        clearTimeout(debounceTimer);
        
        if (query.length < 2) {
            suggestionsList.setAttribute('hidden', '');
            return;
        }
        
        // Debounce the search to avoid too many requests
        debounceTimer = setTimeout(() => {
            // Fetch search suggestions
            fetch(`/search/api/search?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    displaySuggestions(data.results || []);
                })
                .catch(error => {
                    console.error('Error fetching search suggestions:', error);
                    suggestionsList.setAttribute('hidden', '');
                });
        }, 300);
    });
    
    searchInput.addEventListener('keydown', function(e) {
        const items = suggestionsList.querySelectorAll('li[role="option"]');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentFocus = Math.min(currentFocus + 1, items.length - 1);
            setActiveItem(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentFocus = Math.max(currentFocus - 1, -1);
            setActiveItem(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                items[currentFocus].click();
            } else {
                searchForm.submit();
            }
        } else if (e.key === 'Escape') {
            suggestionsList.setAttribute('hidden', '');
            currentFocus = -1;
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchForm.contains(e.target)) {
            suggestionsList.setAttribute('hidden', '');
            currentFocus = -1;
        }
    });
    
    function displaySuggestions(products) {
        suggestionsList.innerHTML = '';
        
        if (!products || products.length === 0) {
            suggestionsList.setAttribute('hidden', '');
            return;
        }
        
        // Show up to 5 suggestions
        products.slice(0, 5).forEach(product => {
            const li = document.createElement('li');
            li.setAttribute('role', 'option');
            li.innerHTML = `
                <div class="suggestion-item">
                    <span class="suggestion-name">${escapeHtml(product.name)}</span>
                    <span class="suggestion-type">${escapeHtml(product.type)}</span>
                </div>
            `;
            
            li.addEventListener('click', function() {
                searchInput.value = product.name;
                searchForm.submit();
            });
            
            suggestionsList.appendChild(li);
        });
        
        suggestionsList.removeAttribute('hidden');
    }
    
    function setActiveItem(items) {
        items.forEach(item => item.classList.remove('active'));
        
        if (currentFocus >= 0 && items[currentFocus]) {
            items[currentFocus].classList.add('active');
            items[currentFocus].scrollIntoView({ block: 'nearest' });
        }
    }
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Add some CSS for suggestions in the nav search
const style = document.createElement('style');
style.textContent = `
    .suggestion-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
    }
    .suggestion-name {
        font-weight: 500;
    }
    .suggestion-type {
        font-size: 0.8rem;
        color: #6c757d;
        text-transform: uppercase;
    }
    .loading-message {
        text-align: center;
        padding: 3rem;
        color: #6c757d;
        font-style: italic;
    }
    .nav-search {
        display: flex;
        align-items: center;
        gap: 8px;
        position: relative;
        width: clamp(180px, 36vw, 420px);
        min-width: 160px;
        background: #fff;
        padding: 4px 8px;
        border-radius: 999px;
        border: 1px solid #e6e6e6;
        box-shadow: 0 1px 4px rgba(12,34,64,0.06);
        transition: box-shadow .15s ease, border-color .15s ease;
    }
    .nav-search:focus-within {
        border-color: #007bff;
        box-shadow: 0 6px 20px rgba(0,123,255,0.08);
    }
    .nav-search input[type="search"] {
        flex: 1 1 auto;
        width: 100%;
        border: none;
        outline: none;
        background: transparent;
        font-size: 0.95rem;
        padding: 6px 4px;
        color: #111;
    }
    .nav-search button {
        background: transparent;
        border: none;
        padding: 6px;
        margin: 0;
        font-size: 1.05rem;
        cursor: pointer;
        color: #0C2340;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Discount badge styling for search results */
    .discount-badge {
        background-color: #dc3545;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 2;
    }
    
    /* Price display for discounted items */
    .price-with-discount {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    
    .original-price {
        text-decoration: line-through;
        color: #dc3545;
        font-size: 0.9rem;
        opacity: 0.7;
    }
    
    .discounted-price {
        color: #2c5530;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .discount-percentage {
        color: #dc3545;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    /* Regular price styling */
    .product-price {
        color: #2c5530;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    /* Container for product images */
    .product-image-container {
        position: relative;
        display: inline-block;
    }
    
    .search-product-card .product-image {
        position: relative;
    }
`;
document.head.appendChild(style);