let cartItems = typeof initialCartData !== 'undefined' ? initialCartData : [];
  
const TAX_RATE = 0.0825; 
let shipping = "standard" 
let discount = 0;
let appliedDiscount = null;

function init() {
    console.log('Initial cart data:', initialCartData); // Debug log
    
    // Convert string prices to numbers
    cartItems = cartItems.map(item => ({
        ...item,
        price: parseFloat(item.price) || 0,
        quantity: parseInt(item.quantity) || 1
    }));
    
    console.log('Processed cart items:', cartItems); // Debug log
    renderCartItems()
    updateSummary()
    setupEventListeners()
}
  
function renderCartItems() {
    const cartItemsContainer = document.getElementById("cartItems")
    cartItemsContainer.innerHTML = ""

    console.log('Rendering cart items:', cartItems); // Debug log

    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = '<div class="empty-cart-message">Your cart is empty. Continue shopping to add items.</div>';
        return;
    }
  
    cartItems.forEach((item) => {
        console.log('Rendering item:', item); // Debug each item
        const itemElement = document.createElement("div")
        itemElement.className = "cart-item"
        itemElement.innerHTML = `
                <div class="item-grid">
                    <div class="item-details">
                        <img src="${item.image || '../static/img/placeholder.jpg'}" alt="${item.name}" class="item-image">
                        <div class="item-info">
                            <h3 class="item-name">${item.name}</h3>
                            <p class="item-category">${item.category || 'No category'}</p>
                            <p class="item-size">Size: ${item.size || 'N/A'}</p>
                            <button class="remove-button" onclick="removeItem(${item.id}, '${item.size}')">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                                </svg>
                                Remove
                            </button>
                        </div>
                    </div>
                    <div class="quantity-controls">
                        <button class="quantity-button" onclick="updateQuantity(${item.id}, '${item.size}', -1)">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M5 12h14"/>
                            </svg>
                        </button>
                        <span class="quantity-value">${item.quantity}</span>
                        <button class="quantity-button" onclick="updateQuantity(${item.id}, '${item.size}', 1)">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 5v14M5 12h14"/>
                            </svg>
                        </button>
                    </div>
                    <div class="item-price">$${item.price.toFixed(2)}</div>
                    <div class="item-total">$${(item.price * item.quantity).toFixed(2)}</div>
                </div>
            `
        cartItemsContainer.appendChild(itemElement)
    })
  
    document.getElementById("itemCount").textContent = `${cartItems.length} Items`
    document.getElementById("summaryItemCount").textContent = cartItems.length
}
  
async function updateQuantity(id, size, change) {
    try {
        const response = await fetch('/cart/api/update-quantity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: id,
                size: size,
                change: change
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // Update local cart data
            const item = cartItems.find((item) => item.id === id && item.size === size);
            if (item) {
                if (result.new_quantity === 0) {
                    // Remove item from local cart if quantity becomes 0
                    cartItems = cartItems.filter((item) => !(item.id === id && item.size === size));
                } else {
                    item.quantity = result.new_quantity;
                }
            }
            
            renderCartItems();
            updateSummary();
            showToast('Cart updated successfully', 'success');
        } else {
            showToast(result.error || 'Error updating quantity', 'error');
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
        showToast('Error updating quantity', 'error');
    }
}
  
async function removeItem(id, size) {
    try {
        const response = await fetch('/cart/api/remove-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: id,
                size: size
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // Remove item from local cart
            cartItems = cartItems.filter((item) => !(item.id === id && item.size === size));
            renderCartItems();
            updateSummary();
            showToast('Item removed from cart', 'success');
        } else {
            showToast(result.error || 'Error removing item', 'error');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showToast('Error removing item', 'error');
    }
}

async function applyPromoCode(promoCode) {
    try {
        console.log('Applying promo code:', promoCode);
        const subtotal = calculateSubtotal();
        console.log('Current subtotal:', subtotal);
        
        const response = await fetch('/cart/api/validate-discount', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: promoCode,
                subtotal: subtotal
            })
        });

        const result = await response.json();
        console.log('API Response:', result);

        if (response.ok && result.valid) {
            appliedDiscount = result.discount;
            console.log('Applied discount data:', appliedDiscount);
            
            discount = calculateDiscountAmount(result.discount);
            console.log('Calculated discount amount:', discount);
            
            return { success: true, message: `Promo code "${promoCode}" applied successfully!` };
        } else {
            appliedDiscount = null;
            discount = 0;
            return { success: false, message: result.error || 'Invalid promo code' };
        }
    } catch (error) {
        console.error('Error applying promo code:', error);
        appliedDiscount = null;
        discount = 0;
        return { success: false, message: 'Error applying promo code. Please try again.' };
    }
}

function calculateSubtotal() {
    return cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function calculateDiscountAmount(discountData) {
    console.log('Calculating discount for:', discountData);
    
    const subtotal = calculateSubtotal();
    const shippingCost = calculateShippingCost();
    const tax = subtotal * TAX_RATE;
    const totalBeforeDiscount = subtotal + tax + shippingCost;
    
    console.log('Total before discount:', totalBeforeDiscount);
    
    // Check minimum purchase requirement (based on subtotal as per typical e-commerce)
    if (discountData.min_purchase > 0 && subtotal < discountData.min_purchase) {
        console.log('Minimum purchase requirement not met');
        return 0;
    }
    
    let discountAmount = 0;
    
    if (discountData.discount_type === 'percentage') {
        // Percentage discounts apply to subtotal only (typical e-commerce practice)
        discountAmount = subtotal * (discountData.value / 100);
        console.log('Percentage discount calculated on subtotal:', discountAmount);
    } else if (discountData.discount_type === 'fixed') {
        // Fixed discounts apply to the total (including tax and shipping)
        discountAmount = Math.min(discountData.value, totalBeforeDiscount);
        console.log('Fixed discount amount applied to total:', discountAmount);
    }
    
    // Ensure discount doesn't exceed the total before discount
    const finalDiscount = Math.min(discountAmount, totalBeforeDiscount);
    
    console.log('Final discount amount:', finalDiscount);
    return finalDiscount;
}

function calculateShippingCost() {
    if (cartItems.length === 0) {
        return 0; // No shipping cost for empty cart
    }
    
    if (shipping === "standard") return 5.0;
    else if (shipping === "express") return 15.0;
    else return 0; // pickup
}

function updateSummary() {
    const subtotal = calculateSubtotal();
    const tax = subtotal * TAX_RATE;
    const shippingCost = calculateShippingCost();
    
    console.log('Update Summary - Subtotal:', subtotal, 'Tax:', tax, 'Shipping:', shippingCost, 'Current Discount:', discount);
    
    // Recalculate discount in case subtotal or shipping changed
    if (appliedDiscount) {
        console.log('Recalculating discount with applied discount:', appliedDiscount);
        discount = calculateDiscountAmount(appliedDiscount);
        console.log('Recalculated discount:', discount);
    }
    
    const totalBeforeDiscount = subtotal + tax + shippingCost;
    const total = Math.max(0, totalBeforeDiscount - discount);

    console.log('Final values - Subtotal:', subtotal, 'Discount:', discount, 'Total:', total);
    
    document.getElementById("subtotal").textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById("taxCost").textContent = `$${tax.toFixed(2)}`;
    document.getElementById("discountCost").textContent = `-$${discount.toFixed(2)}`;
    
    const shippingDisplay = document.getElementById("shippingCostDisplay");
    if (shippingCost === 0) {
        shippingDisplay.textContent = "FREE";
    } else if (shipping === "standard") {
        shippingDisplay.textContent = "$5.00";
    } else if (shipping === "express") {
        shippingDisplay.textContent = "$15.00";
    }

    document.getElementById("totalCost").textContent = `$${total.toFixed(2)}`;
    
    // Update promo code display
    updatePromoCodeDisplay();
}

function updatePromoCodeDisplay() {
    const promoInput = document.getElementById("promoInput");
    const applyButton = document.getElementById("applyPromo");
    const removeButton = document.getElementById("removePromo");
    
    if (appliedDiscount) {
        promoInput.value = appliedDiscount.code;
        promoInput.disabled = true;
        applyButton.style.display = 'none';
        if (removeButton) {
            removeButton.style.display = 'inline-block';
        }
    } else {
        promoInput.disabled = false;
        applyButton.style.display = 'inline-block';
        if (removeButton) {
            removeButton.style.display = 'none';
        }
    }
}

function removePromoCode() {
    console.log('Removing promo code');
    appliedDiscount = null;
    discount = 0;
    const promoInput = document.getElementById("promoInput");
    promoInput.value = "";
    updateSummary();
}

async function checkout() {
    const paymentType = document.getElementById('paymentType')?.value;
    const paymentDetails = document.getElementById('paymentDetails')?.value || '';
    const shippingMethod = document.getElementById("shippingSelect")?.value || 'standard';

    if (!paymentType) {
        showToast('Please select a payment method', 'error');
        return;
    }

    // Show loading state
    const checkoutButton = document.querySelector('#checkoutModal .btn-primary');
    if (checkoutButton) {
        checkoutButton.disabled = true;
        checkoutButton.textContent = 'Processing...';
    }

    try {
        const response = await fetch('/cart/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                payment_type: paymentType,
                payment_details: paymentDetails,
                discount_code: appliedDiscount ? appliedDiscount.code : null,  // Send discount code if applied
                shipping_method: shippingMethod  // Send the selected shipping method
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showToast(result.message, 'success');
            // Clear local cart
            cartItems = [];
            appliedDiscount = null;
            discount = 0;
            renderCartItems();
            updateSummary();
            
            // Close payment modal
            closePaymentModal();
            
            // Redirect to home or order confirmation page after delay
            setTimeout(() => {
                window.location.href = '/home';
            }, 2000);
        } else {
            showToast(result.error || 'Error during checkout', 'error');
            // Re-enable checkout button on error
            if (checkoutButton) {
                checkoutButton.disabled = false;
                checkoutButton.textContent = 'Complete Purchase';
            }
        }
    } catch (error) {
        console.error('Error during checkout:', error);
        showToast('Error during checkout', 'error');
        // Re-enable checkout button on error
        if (checkoutButton) {
            checkoutButton.disabled = false;
            checkoutButton.textContent = 'Complete Purchase';
        }
    }
}

function showPaymentModal() {
    // Create a simple payment modal
    const modal = document.createElement('div');
    modal.className = 'modal fade show';
    modal.style.display = 'block';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.zIndex = '9999';
    modal.id = 'checkoutModal';
    
    const subtotal = calculateSubtotal();
    const shippingCost = calculateShippingCost();
    const tax = subtotal * TAX_RATE;
    const total = subtotal + shippingCost + tax - discount;
    
    modal.innerHTML = `
        <div class="modal-dialog" style="margin: 10% auto; max-width: 500px;">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Complete Your Order</h5>
                    <button type="button" class="btn-close" onclick="closePaymentModal()"></button>
                </div>
                <div class="modal-body">
                    <div class="order-summary mb-3">
                        <h6>Order Summary</h6>
                        <div class="d-flex justify-content-between">
                            <span>Items (${cartItems.length}):</span>
                            <span>$${subtotal.toFixed(2)}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Shipping:</span>
                            <span>${shippingCost === 0 ? 'FREE' : '$' + shippingCost.toFixed(2)}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Tax:</span>
                            <span>$${tax.toFixed(2)}</span>
                        </div>
                        ${discount > 0 ? `
                        <div class="d-flex justify-content-between text-success">
                            <span>Discount:</span>
                            <span>-$${discount.toFixed(2)}</span>
                        </div>
                        ` : ''}
                        <hr>
                        <div class="d-flex justify-content-between fw-bold">
                            <span>Total:</span>
                            <span>$${total.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="paymentType" class="form-label">Payment Method</label>
                        <select id="paymentType" class="form-select">
                            <option value="">Select a payment method</option>
                            <option value="credit_card">Credit Card</option>
                            <option value="debit_card">Debit Card</option>
                            <option value="paypal">PayPal</option>
                            <option value="apple_pay">Apple Pay</option>
                            <option value="google_pay">Google Pay</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="paymentDetails" class="form-label">Payment Details (Optional)</label>
                        <input type="text" id="paymentDetails" class="form-control" placeholder="Additional payment information">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closePaymentModal()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="checkout()">Complete Purchase</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    document.body.appendChild(backdrop);
}

function closePaymentModal() {
    const modal = document.getElementById('checkoutModal');
    const backdrop = document.querySelector('.modal-backdrop');
    
    if (modal) {
        modal.remove();
    }
    if (backdrop) {
        backdrop.remove();
    }
}

function setupEventListeners() {
    const shippingSelect = document.getElementById("shippingSelect");
    shippingSelect.addEventListener("change", (e) => {
      shipping = e.target.value;
      updateSummary();
    });
  
    const promoInput = document.getElementById("promoInput");
    const applyButton = document.getElementById("applyPromo");
  
    promoInput.addEventListener("input", (e) => {
      if (!appliedDiscount) {
        applyButton.disabled = e.target.value.trim() === "";
      }
    });
  
    applyButton.addEventListener("click", async () => {
      const promoCode = promoInput.value.trim();
      if (promoCode && !appliedDiscount) {
        applyButton.disabled = true;
        applyButton.textContent = "Applying...";
        
        const result = await applyPromoCode(promoCode);
        
        if (result.success) {
            showToast(result.message, 'success');
            updateSummary();
        } else {
            showToast(result.message, 'error');
            promoInput.value = "";
        }
        
        applyButton.disabled = false;
        applyButton.textContent = "Apply";
      }
    });
  
    // Add Enter key support for promo code
    promoInput.addEventListener("keypress", (e) => {
      if (e.key === 'Enter' && !applyButton.disabled && !appliedDiscount) {
        applyButton.click();
      }
    });
  
    const checkoutButton = document.querySelector(".checkout-button");
    checkoutButton.addEventListener("click", showPaymentModal);
    
    // Add event listener for remove promo button
    const removeButton = document.getElementById("removePromo");
    if (removeButton) {
        removeButton.addEventListener("click", removePromoCode);
    }
}

function showToast(message, type = 'info') {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}
  
document.addEventListener("DOMContentLoaded", init);