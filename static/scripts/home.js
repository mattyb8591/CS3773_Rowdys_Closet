document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded, starting product load...');
    loadProducts();
    setTimeout(initializeScrollers, 100);
});

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
            
            // Display products in their repsective sections
            displayProductsByType(productsByType);
        })
        .catch(error => {
            console.error('Error loading products:', error);
            document.querySelectorAll('.product-scroller').forEach(scroller => {
                scroller.innerHTML = '<div class="no-products">Error loading products. Please refresh the page.</div>';
            });
        });
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
    
    const formattedPrice = parseFloat(product.price).toFixed(2);
    const isOutOfStock = product.stock <= 0;
    
    const stockStatus = isOutOfStock ? 
        '<span class="out-of-stock-tag">Out of Stock</span>' : 
        `<button class="btn btn-sm btn-primary add-to-cart" data-product-id="${product.product_id}">Add to Cart</button>`;
    
    let imagePath = product.img_file_path;
    if (imagePath && !imagePath.match(/\.(png|jpg|jpeg|gif|webp)$/i)) {
        imagePath += '.png';
    }
    
    const imageHtml = imagePath ? 
        `<img src="${imagePath}" alt="${product.name}" onerror="this.style.display='none'">` :
        '<div class="no-image-placeholder"></div>';
    
    card.innerHTML = `
        <div class="product-image-container">
            ${imageHtml}
        </div>
        <div class="product-name">${product.name}</div>
        <div class="product-price">$${formattedPrice}</div>
        ${stockStatus}
    `;
    
    return card;
}