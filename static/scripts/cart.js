// Initial cart data
let cartItems = [
    {
      id: 1,
      name: "UTSA Roadrunners Jersey",
      category: "Apparel",
      price: 64.99,
      quantity: 2,
      image: "/utsa-jersey-apparel.jpg",
    },
    {
      id: 2,
      name: "UTSA Baseball Cap",
      category: "Accessories",
      price: 29.99,
      quantity: 1,
      image: "/utsa-cap-accessory.jpg",
    },
    {
      id: 3,
      name: "UTSA Hoodie",
      category: "Apparel",
      price: 54.99,
      quantity: 1,
      image: "/utsa-hoodie-apparel.jpg",
    },
  ]
  
  let shipping = "standard"
  
  
  function init() {
    renderCartItems()
    updateSummary()
    setupEventListeners()
  }
  
  
  function renderCartItems() {
    const cartItemsContainer = document.getElementById("cartItems")
    cartItemsContainer.innerHTML = ""
  
    cartItems.forEach((item) => {
      const itemElement = document.createElement("div")
      itemElement.className = "cart-item"
      itemElement.innerHTML = `
              <div class="item-grid">
                  <div class="item-details">
                      <img src="${item.image}" alt="${item.name}" class="item-image">
                      <div class="item-info">
                          <h3 class="item-name">${item.name}</h3>
                          <p class="item-category">${item.category}</p>
                          <button class="remove-button" onclick="removeItem(${item.id})">
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                  <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                              </svg>
                              Remove
                          </button>
                      </div>
                  </div>
                  <div class="quantity-controls">
                      <button class="quantity-button" onclick="updateQuantity(${item.id}, -1)">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <path d="M5 12h14"/>
                          </svg>
                      </button>
                      <span class="quantity-value">${item.quantity}</span>
                      <button class="quantity-button" onclick="updateQuantity(${item.id}, 1)">
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
  
  
  function updateQuantity(id, change) {
    const item = cartItems.find((item) => item.id === id)
    if (item) {
      item.quantity = Math.max(1, item.quantity + change)
      renderCartItems()
      updateSummary()
    }
  }
  
  
  function removeItem(id) {
    cartItems = cartItems.filter((item) => item.id !== id)
    renderCartItems()
    updateSummary()
  }
  
  function updateSummary() {
    const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
  
    let shippingCost = 0
    if (shipping === "standard") shippingCost = 5.0
    else if (shipping === "express") shippingCost = 15.0
  
    const total = subtotal + shippingCost
  
    document.getElementById("subtotal").textContent = `$${subtotal.toFixed(2)}`
    document.getElementById("totalCost").textContent = `$${total.toFixed(2)}`
  }
  
  
  function setupEventListeners() {
    const shippingSelect = document.getElementById("shippingSelect")
    shippingSelect.addEventListener("change", (e) => {
      shipping = e.target.value
      updateSummary()
    })
  
    const promoInput = document.getElementById("promoInput")
    const applyButton = document.getElementById("applyPromo")
  
    promoInput.addEventListener("input", (e) => {
      applyButton.disabled = e.target.value.trim() === ""
    })
  
    applyButton.addEventListener("click", () => {
      const promoCode = promoInput.value.trim()
      if (promoCode) {
        alert(`Promo code "${promoCode}" applied!`)
        promoInput.value = ""
        applyButton.disabled = true
      }
    })
  
    const checkoutButton = document.querySelector(".checkout-button")
    checkoutButton.addEventListener("click", () => {
      alert("Proceeding to checkout...")
    })
  }
  
  
  document.addEventListener("DOMContentLoaded", init)
  