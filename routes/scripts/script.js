document.addEventListener('DOMContentLoaded', function() {
    const fetchButton = document.getElementById('fetchProducts');
    const productsTable = document.getElementById('productsTable');

    fetchButton.addEventListener('click', function() {
        // Make GET request to Flask API Endpoint
        fetch('/api/products')
            .then(response => response.json())

            // processes the data into table
            .then(data => {
                displayProductsTable(data.products);
            })
            .catch(error => {
                productsTable.innerHTML = `
                    <div class="error">
                        Error fetching products: ${error}
                    </div>
                `;
            });
    });

    // function for displaying the table
    function displayProductsTable(products) {
        if (products.length === 0) {
            productsTable.innerHTML = '<div class="message">No products found</div>';
            return;
        }

        // table structure
        let tableHTML = `
            <table class="products-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Product Name</th>
                        <th>Stock</th>
                        <th>Price</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // loops through the product object to create rows
        products.forEach(product => {
            tableHTML += `
                <tr>
                    <td>${product.productID}</td>
                    <td>${product.productName}</td>
                    <td>${product.numInStock}</td>
                    <td>$${product.price.toFixed(2)}</td>
                    <td>${product.rating}/5.0</td>
                </tr>
            `;
        });

        tableHTML += `
                </tbody>
            </table>
        `;

        // inserts the created table into the productsTable div
        productsTable.innerHTML = tableHTML;
    }
});
