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
    
    const formattedPrice = parseFloat(product.price).toFixed(2);
    const isOutOfStock = product.stock <= 0;
    
    const stockStatus = isOutOfStock ? 
        '<span class="out-of-stock-tag">Out of Stock</span>' : 
        // make this a link to the item page so the server loads item details
        `<a class="btn btn-sm btn-primary view-item" href="/item/${product.product_id}">View Item</a>`;
    
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


async function searchRequest(searchText, searchForm){

    //POST data to '/home/searchrequest'
    
    
    try {   
      const response = await fetch("/home/searchrequest", {
        method: "POST",
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({search_data: searchText})
      });

      //const result = await response.json();

      if (response.ok) {
        
        searchForm.reset();

        /*setTimeout(() => {
          window.location.href = "/"; 
        }, 2000);*/

      } else {
        console.log("Error with sending search request to home.py");
      }
    } catch (error) {
      console.error("Fetch error:", error);
    }

    //GET results from '/home/searchrequest'
    let searchResults = await getSearchResults();
    console.log(searchResults);
    //Change dom based on the request

    Object.keys(productsCache).forEach(k => delete productsCache[k]); // clear old values
    Object.assign(productsCache, searchResults);    

    //render the searched products
    renderProducts();
    
}

async function getSearchResults(){

    let request_data = null;

    const getResults = await fetch("/home/searchresult")
    .then(getResults => {
            console.log('API response of searched products:', getResults.status);
            if (!getResults.ok) {
                throw new Error(`HTTP error! status: ${getResults.status}`);
            }
            return getResults.json();
    })
    .then(data => {
        console.log(data);
        request_data = data;
    })
    .catch(error => {
            console.error('Error getting searched products:', error);
    });
    
    return request_data;
}

const submit = document.getElementById('search-submit');

submit.addEventListener("click", async (event) => {
    const elSearch = document.getElementById('site-search').value;
    const searchForm = document.getElementById('searchBarGroup');
    event.preventDefault();
    await searchRequest(elSearch, searchForm);
}, false);
