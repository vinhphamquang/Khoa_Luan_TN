// ===================================================================
// Page Transitions & Graceful Logout
// Shared across index.html, nutrition.html, admin.html
// ===================================================================

(function () {
    'use strict';

    const FADE_OUT_MS = 280;
    const LOGOUT_DELAY_MS = 650;

    // ---------- Toast ----------
    function ensureToastHost() {
        let host = document.getElementById('app-toast-host');
        if (!host) {
            host = document.createElement('div');
            host.id = 'app-toast-host';
            host.className = 'app-toast-host';
            document.body.appendChild(host);
        }
        return host;
    }

    function showToast(message, type = 'success', durationMs = 2200) {
        const host = ensureToastHost();
        const toast = document.createElement('div');
        toast.className = `app-toast app-toast-${type}`;
        const icon = type === 'success' ? 'fa-circle-check'
                   : type === 'error'   ? 'fa-circle-xmark'
                   : type === 'warning' ? 'fa-triangle-exclamation'
                                        : 'fa-circle-info';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i><span>${message}</span>`;
        host.appendChild(toast);

        // Force reflow then add show class
        requestAnimationFrame(() => toast.classList.add('show'));

        setTimeout(() => {
            toast.classList.remove('show');
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 320);
        }, durationMs);

        return toast;
    }

    // ---------- Fade out helper ----------
    function fadeOutBody() {
        document.body.classList.add('is-leaving');
    }

    // ---------- Graceful logout ----------
    function gracefulLogout(options = {}) {
        const { redirectTo = '/', message = 'Đăng xuất thành công. Hẹn gặp lại!' } = options;

        try { localStorage.removeItem('smartfood_user'); } catch (e) { /* ignore */ }

        showToast(message, 'success', LOGOUT_DELAY_MS + 400);

        // Slight delay so the toast is visible, then fade out and navigate
        setTimeout(fadeOutBody, 120);
        setTimeout(() => {
            window.location.href = redirectTo;
        }, LOGOUT_DELAY_MS);
    }

    // ---------- Smooth in-app navigation ----------
    function smoothNavigate(url) {
        if (!url || url === '#' || url.startsWith('javascript:')) return;

        // Same-page hash navigation: don't fade, just let the browser handle it
        const isHashOnly = url.startsWith('#') ||
            (url.includes('#') && url.split('#')[0] === window.location.pathname);
        if (isHashOnly) {
            window.location.href = url;
            return;
        }

        fadeOutBody();
        setTimeout(() => {
            window.location.href = url;
        }, FADE_OUT_MS);
    }

    // ---------- Auto-bind nav links for page-to-page transitions ----------
    const PAGE_PATHS = ['/', '/nutrition', '/admin'];

    function isPageToPageLink(anchor) {
        const href = anchor.getAttribute('href');
        if (!href) return false;
        if (anchor.target && anchor.target !== '_self') return false;
        if (anchor.hasAttribute('download')) return false;
        if (href.startsWith('http://') || href.startsWith('https://')) {
            // External — skip
            try {
                const u = new URL(href);
                if (u.origin !== window.location.origin) return false;
            } catch (e) { return false; }
        }
        // Strip query/hash to get pure path
        const path = href.split('?')[0].split('#')[0];
        if (!path) return false;
        // Only fade if going to a different top-level page
        const currentPath = window.location.pathname.replace(/\/$/, '') || '/';
        const targetPath = path.replace(/\/$/, '') || '/';
        if (targetPath === currentPath) return false;
        return PAGE_PATHS.includes(targetPath);
    }

    function handleLinkClick(e) {
        const anchor = e.target.closest('a');
        if (!anchor) return;
        if (e.defaultPrevented) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        if (e.button !== 0) return;
        if (!isPageToPageLink(anchor)) return;

        e.preventDefault();
        smoothNavigate(anchor.getAttribute('href'));
    }

    // ---------- Background food icons (decorative) ----------
    const FOOD_ICONS = [
        { cls: 'fa-pizza-slice',  top: '8%',  left: '4%',  size: 42, rot: -15, dur: 18, delay: 0,   color: '#f59e0b' },
        { cls: 'fa-bowl-rice',    top: '16%', left: '92%', size: 50, rot: 12,  dur: 24, delay: -2,  color: '#22c55e' },
        { cls: 'fa-fish',         top: '30%', left: '3%',  size: 38, rot: -8,  dur: 20, delay: -4,  color: '#06b6d4' },
        { cls: 'fa-burger',       top: '42%', left: '95%', size: 46, rot: 18,  dur: 22, delay: -1,  color: '#ef4444' },
        { cls: 'fa-ice-cream',    top: '56%', left: '6%',  size: 36, rot: -20, dur: 19, delay: -5,  color: '#ec4899' },
        { cls: 'fa-apple-whole',  top: '70%', left: '94%', size: 38, rot: 10,  dur: 21, delay: -3,  color: '#ef4444' },
        { cls: 'fa-cookie',       top: '82%', left: '8%',  size: 42, rot: -12, dur: 23, delay: -6,  color: '#d97706' },
        { cls: 'fa-cake-candles', top: '10%', left: '46%', size: 32, rot: 5,   dur: 25, delay: -2.5,color: '#ec4899' },
        { cls: 'fa-mug-hot',      top: '88%', left: '52%', size: 36, rot: -5,  dur: 18, delay: -4.5,color: '#92400e' },
        { cls: 'fa-carrot',       top: '24%', left: '70%', size: 36, rot: 25,  dur: 22, delay: -1.5,color: '#f97316' },
        { cls: 'fa-egg',          top: '54%', left: '50%', size: 28, rot: -10, dur: 17, delay: -3.5,color: '#fbbf24' },
        { cls: 'fa-lemon',        top: '38%', left: '48%', size: 32, rot: 15,  dur: 20, delay: -5.5,color: '#facc15' },
        { cls: 'fa-pepper-hot',   top: '66%', left: '40%', size: 32, rot: -25, dur: 19, delay: -0.5,color: '#dc2626' },
        { cls: 'fa-cheese',       top: '6%',  left: '74%', size: 38, rot: 8,   dur: 24, delay: -2,  color: '#fbbf24' },
        { cls: 'fa-bread-slice',  top: '92%', left: '78%', size: 40, rot: -18, dur: 21, delay: -4,  color: '#d97706' }
    ];

    function injectBackgroundFoodIcons() {
        if (document.querySelector('.bg-food-icons')) return;
        if (document.body.dataset.noFoodIcons === 'true') return;

        const container = document.createElement('div');
        container.className = 'bg-food-icons';
        container.setAttribute('aria-hidden', 'true');

        const frag = document.createDocumentFragment();
        FOOD_ICONS.forEach((cfg, i) => {
            const span = document.createElement('span');
            span.className = `bg-food-icon bg-food-icon-${i + 1}`;
            span.style.top = cfg.top;
            span.style.left = cfg.left;
            span.style.fontSize = `${cfg.size}px`;
            span.style.color = cfg.color;
            span.style.setProperty('--icon-rot', `${cfg.rot}deg`);
            span.style.setProperty('--icon-dur', `${cfg.dur}s`);
            span.style.setProperty('--icon-delay', `${cfg.delay}s`);
            span.innerHTML = `<i class="fa-solid ${cfg.cls}"></i>`;
            frag.appendChild(span);
        });
        container.appendChild(frag);

        if (document.body.firstChild) {
            document.body.insertBefore(container, document.body.firstChild);
        } else {
            document.body.appendChild(container);
        }
    }

    // ---------- Page-load fade-in ----------
    // CSS animation `appBodyEnter` runs automatically on every page load.
    // No JS work needed for entry — keeping this for forward compatibility.

    // ---------- Restore body when coming back via bfcache ----------
    function handlePageShow(e) {
        if (e.persisted) {
            // Browser restored from back/forward cache — clear leaving state
            document.body.classList.remove('is-leaving');
        }
    }

    // ---------- Boot ----------
    function boot() {
        document.addEventListener('click', handleLinkClick, true);
        window.addEventListener('pageshow', handlePageShow);
        injectBackgroundFoodIcons();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

    // Expose API
    window.gracefulLogout = gracefulLogout;
    window.smoothNavigate = smoothNavigate;
    window.appToast = showToast;
})();
