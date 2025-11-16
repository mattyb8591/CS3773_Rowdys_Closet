document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded, starting product load...');

    // read sort from URL so the choice persists if user bookmarks or refreshes
    const params = new URLSearchParams(window.location.search);
    currentSort = params.get('sort') || 'default';

    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.value = currentSort;
        // when user changes selection, update currentSort, update URL (no reload), and re-render
        sortSelect.addEventListener('change', (e) => {
            currentSort = e.target.value || 'default';

            // update query param without reloading the page
            const p = new URLSearchParams(window.location.search);
            if (currentSort === 'default') p.delete('sort'); else p.set('sort', currentSort);
            const newUrl = window.location.pathname + (p.toString() ? '?' + p.toString() : '');
            history.replaceState(null, '', newUrl);

            // call renderProducts() directly (no load/reload)
            renderProducts();
        });
    }

    
    loadProducts();
    setTimeout(initializeScrollers, 100);

    // Initialize search functionality
    initializeSearch();
});

let productsCache = {};    // cached API data keyed by type
let currentSort = 'default';

function loadProducts() {
    console.log('Fetching products from API...');
    
    // Fetch products from the API endpoint
    fetch('/home/api/products')
        .then(response => {
            console.log('API response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(productsByType => {
            console.log('Products received from API (organized by type):', productsByType);
            
            // cache API data for client-side sorting/rendering
            productsCache = productsByType || {};
            renderProducts();
        })
        .catch(error => {
            console.error('Error loading products:', error);
            document.querySelectorAll('.product-scroller').forEach(scroller => {
                scroller.innerHTML = '<div class="no-products">Error loading products. Please refresh the page.</div>';
            });
        });
}

function renderProducts() {
    const sorted = sortProductsDeep(productsCache, currentSort);
    displayProductsByType(sorted);
}

function sortProductsDeep(productsByType, sortKey) {
    const out = {};
    Object.keys(productsByType || {}).forEach(type => {
        const arr = (productsByType[type] || []).slice(); // copy so we don't mutate cache
        out[type] = sortArray(arr, sortKey);
    });
    return out;
}

function sortArray(arr, sortKey) {
    if (!sortKey || sortKey === 'default') return arr;
    const multiplier = sortKey.endsWith('-asc') ? 1 : -1;

    if (sortKey.startsWith('price')) {
        return arr.sort((a, b) => {
            const pa = parseFloat(a.price) || 0;
            const pb = parseFloat(b.price) || 0;
            return (pa - pb) * multiplier;
        });
    }

    if (sortKey.startsWith('availability')) {
        return arr.sort((a, b) => {
            const sa = Number(a.stock) || 0;
            const sb = Number(b.stock) || 0;
            return (sa - sb) * multiplier;
        });
    }

    return arr;
}

function displayProductsByType(productsByType) {
    console.log('Displaying products by type:', productsByType);
    
    // For each product type, display products in the corresponding section
    Object.keys(productsByType).forEach(productType => {
        const sectionId = getSectionId(productType);
        const scroller = document.getElementById(sectionId);
        
        console.log(`Looking for section: ${productType} -> ${sectionId}`, scroller);
        
        if (scroller) {
            const products = productsByType[productType];
            console.log(`Found ${products.length} products for ${productType}:`, products.map(p => p.name));
            
            if (products.length === 0) {
                scroller.innerHTML = '<div class="no-products">No products available</div>';
                return;
            }

            scroller.innerHTML = '';

            products.forEach(product => {
                const productCard = createProductCard(product);
                scroller.appendChild(productCard);
            });
        } else {
            console.warn(`No scroller found for product type: ${productType}`);
        }
    });
}

function getSectionId(productType) {
    const typeToId = {
        'T-Shirts': 'shirtsScroller',
        'Hoodies': 'hoodiesScroller',
        'Jackets': 'jacketsScroller',
        'Headwear': 'headwearScroller',
        'Bags': 'bagsScroller'
    };
    return typeToId[productType];
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const isOutOfStock = product.stock <= 0;
    const hasDiscount = product.discount && product.discount > 0;
    
    // Use original_price if available, otherwise use current price
    let priceDisplay = `$${parseFloat(product.price).toFixed(2)}`;
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
        discountBadge = `<span class="discount-badge">-${Math.round(product.discount)}%</span>`;
    }
    
    const stockStatus = isOutOfStock ? 
        '<span class="out-of-stock-tag">Out of Stock</span>' : 
        `<a class="btn btn-sm btn-primary view-item" href="/item/${product.product_id}">View Item</a>`;
    
    let imagePath = product.img_file_path;
    if (imagePath && !imagePath.match(/\.(png|jpg|jpeg|gif|webp)$/i)) {
        imagePath += '.png';
    }
    
    // Fixed: Properly generate image HTML
    let imageHtml = '';
    if (imagePath) {
        imageHtml = `<img src="${imagePath}" alt="${product.name}" onerror="this.style.display='none'">`;
    } else {
        imageHtml = '<div class="no-image-placeholder"></div>';
    }
    
    card.innerHTML = `
        <div class="product-image-container">
            ${imageHtml}
            ${discountBadge}
        </div>
        <div class="product-name">${product.name}</div>
        <div class="product-price-container ${hasDiscount ? 'has-discount' : ''}">
            ${priceDisplay}
        </div>
        ${stockStatus}
    `;
    
    return card;
}

function initializeSearch() {
    const submit = document.getElementById('search-submit');
    const searchInput = document.getElementById('site-search');

    if (submit) {
        submit.addEventListener("click", handleSearch, false);
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch(e);
            }
        });
    }
}

function handleSearch(event) {
    event.preventDefault();
    
    const searchInput = document.getElementById('site-search');
    const searchText = searchInput.value.trim();
    
    if (searchText) {
        // Redirect to search page with the query
        window.location.href = `/search/search?q=${encodeURIComponent(searchText)}`;
    }
}

function initializeScrollers() {
    // Initialize horizontal scrollers if needed
    document.querySelectorAll('.product-scroller').forEach(scroller => {
        if (scroller.scrollWidth > scroller.clientWidth) {
            // Add navigation buttons if content overflows
            addScrollerNavigation(scroller);
        }
    });
}

function addScrollerNavigation(scroller) {
    const wrapper = scroller.parentElement;
    
    // Create previous button
    const prevBtn = document.createElement('button');
    prevBtn.className = 'scroller-btn scroller-prev';
    prevBtn.innerHTML = '‹';
    prevBtn.setAttribute('aria-label', 'Scroll left');
    
    // Create next button
    const nextBtn = document.createElement('button');
    nextBtn.className = 'scroller-btn scroller-next';
    nextBtn.innerHTML = '›';
    nextBtn.setAttribute('aria-label', 'Scroll right');
    
    // Add buttons to wrapper
    wrapper.style.position = 'relative';
    wrapper.appendChild(prevBtn);
    wrapper.appendChild(nextBtn);
    
    // Add event listeners
    prevBtn.addEventListener('click', () => {
        scroller.scrollBy({ left: -300, behavior: 'smooth' });
    });
    
    nextBtn.addEventListener('click', () => {
        scroller.scrollBy({ left: 300, behavior: 'smooth' });
    });
    
    // Update button visibility based on scroll position
    function updateButtonVisibility() {
        prevBtn.style.display = scroller.scrollLeft > 0 ? 'flex' : 'none';
        nextBtn.style.display = scroller.scrollLeft < (scroller.scrollWidth - scroller.clientWidth) ? 'flex' : 'none';
    }
    
    scroller.addEventListener('scroll', updateButtonVisibility);
    updateButtonVisibility();
    
    // Also update on window resize
    window.addEventListener('resize', updateButtonVisibility);
}