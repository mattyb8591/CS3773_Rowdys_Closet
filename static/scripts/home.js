document.addEventListener('DOMContentLoaded', function () {
	// Simple small script to set current year
	const yearEl = document.getElementById('year');
	if (yearEl) yearEl.textContent = new Date().getFullYear();

	// Initialize all product scrollers on the page
	document.querySelectorAll('.product-scroller').forEach(scroller => {
		const wrapper = scroller.closest('.scroller-wrapper');
		if (!wrapper) return;
		const prevBtn = wrapper.querySelector('.scroller-prev');
		const nextBtn = wrapper.querySelector('.scroller-next');

		function updateButtons() {
			if (prevBtn) prevBtn.disabled = scroller.scrollLeft <= 0;
			if (nextBtn) nextBtn.disabled = Math.ceil(scroller.scrollLeft + scroller.clientWidth) >= scroller.scrollWidth;
		}

		function scrollByCard(direction) {
			const card = scroller.querySelector('.product-card');
			if (!card) return;
			let gap = 16;
			try {
				const cs = window.getComputedStyle(scroller);
				gap = parseFloat(cs.columnGap || cs.gap) || gap;
			} catch (e) { /* ignore */ }
			const scrollAmount = (card.getBoundingClientRect().width + gap) * direction;
			scroller.scrollBy({ left: scrollAmount, behavior: 'smooth' });
		}

		if (prevBtn) prevBtn.addEventListener('click', () => scrollByCard(-1));
		if (nextBtn) nextBtn.addEventListener('click', () => scrollByCard(1));

		scroller.addEventListener('scroll', updateButtons);
		window.addEventListener('resize', updateButtons);
		updateButtons();

		// Mouse drag-to-scroll for this scroller
		let isDown = false, startX = 0, scrollLeft = 0;
		scroller.addEventListener('mousedown', (e) => {
			isDown = true;
			scroller.classList.add('dragging');
			startX = e.pageX - scroller.offsetLeft;
			scrollLeft = scroller.scrollLeft;
		});
		scroller.addEventListener('mouseleave', () => { isDown = false; scroller.classList.remove('dragging'); });
		scroller.addEventListener('mouseup', () => { isDown = false; scroller.classList.remove('dragging'); });
		scroller.addEventListener('mousemove', (e) => {
			if (!isDown) return;
			e.preventDefault();
			const x = e.pageX - scroller.offsetLeft;
			const walk = (x - startX) * 1;
			scroller.scrollLeft = scrollLeft - walk;
		});
	});

	// Add-to-cart handlers (delegated/static)
	document.querySelectorAll('.add-to-cart').forEach(btn => {
		btn.addEventListener('click', (e) => {
			const id = btn.getAttribute('data-product-id');
			console.log('Add to cart clicked for product', id);
			// TODO: call your add-to-cart endpoint or form here
		});
	});
});
