// Initialize Wishlist count on load
document.addEventListener('DOMContentLoaded', () => {
  updateWishlistCount();
  checkWishlistStatus();
});

function getWishlist() {
  const wishlist = localStorage.getItem('vellora_wishlist');
  return wishlist ? JSON.parse(wishlist) : [];
}

function setWishlist(wishlist) {
  localStorage.setItem('vellora_wishlist', JSON.stringify(wishlist));
  updateWishlistCount();
}

function toggleWishlist(handle) {
  let wishlist = getWishlist();
  const index = wishlist.indexOf(handle);

  if (index > -1) {
    wishlist.splice(index, 1);
  } else {
    wishlist.push(handle);
  }

  setWishlist(wishlist);
  checkWishlistStatus();
}

function updateWishlistCount() {
  const countEls = document.querySelectorAll('#wishlist-count');
  const count = getWishlist().length;
  countEls.forEach(el => {
    el.textContent = count;
  });
}

function checkWishlistStatus() {
  const wishlist = getWishlist();
  const buttons = document.querySelectorAll('.product-card__wishlist');

  buttons.forEach(btn => {
    // Assuming the button has an onclick like "toggleWishlist('handle')"
    const onclickStr = btn.getAttribute('onclick');
    if(onclickStr) {
      const match = onclickStr.match(/'([^']+)'/);
      if (match && match[1]) {
        const handle = match[1];
        if (wishlist.includes(handle)) {
          btn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="var(--color-primary)" stroke="var(--color-primary)" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';
        } else {
          btn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';
        }
      }
    }
  });
}
