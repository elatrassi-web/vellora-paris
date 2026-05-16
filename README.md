# VELLORA PARIS - Shopify Theme

A custom, mobile-first, and high-performance Shopify 2.0 theme built exclusively for VELLORA PARIS.

## Architecture

This theme is built natively without relying on any paid Shopify applications. It utilizes the following technologies:
- **Shopify Liquid**: The backbone of the templating engine.
- **HTML5 & CSS3**: Using CSS Variables and a mobile-first responsive approach.
- **Vanilla JavaScript**: ES6+ modules. No jQuery.

## Installation

1. Download or clone this repository as a `.zip` file.
2. In your Shopify admin, go to **Online Store > Themes**.
3. In the Theme library section, click **Add theme > Upload zip file**.
4. Select the `.zip` file and upload.
5. Once uploaded, click **Actions > Publish** to make it the live theme.

## Features Built-in

- **Wishlist**: Built via `localStorage`, persisting user favorites across sessions.
- **Mini-cart**: Asynchronous slide-in cart using the Storefront Cart API.
- **Quick View**: Custom modal fetching product data natively.
- **AJAX Search**: Real-time predictive search suggestions.
- **Advanced Filters**: Sidebar filtering on Collection pages with AJAX HTML updates.

## Technical Notes

- **CSS Variables**: Core colors and fonts are controlled via `assets/theme.css` using CSS custom properties (`var(--color-primary)`), which map directly to `settings_schema.json`.
- **Animations**: Handled primarily via CSS transitions and the `IntersectionObserver` API in `theme.js` (look for the `.fade-up` class).
- **Fonts**: Montserrat and Poppins are loaded via Google Fonts in `layout/theme.liquid`.
