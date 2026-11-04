// Shared behaviour for every page: navigation, scroll effects,
// wishlist hearts and the image viewer.

const Chitrabaddh = (function () {

    const WISHLIST_KEY = "chitrabaddhWishlist";


    // =====================================
    // WISHLIST (saved in this browser only)
    // =====================================

    function getWishlist() {
        try {
            const saved = JSON.parse(localStorage.getItem(WISHLIST_KEY) || "[]");
            return Array.isArray(saved) ? saved : [];
        } catch (error) {
            return [];
        }
    }

    function saveWishlist(list) {
        try {
            localStorage.setItem(WISHLIST_KEY, JSON.stringify(list));
        } catch (error) {
            // Private mode or storage blocked: the wishlist just won't persist
        }
    }

    function refreshHearts() {
        const list = getWishlist();

        document.querySelectorAll(".wishlist-heart").forEach(button => {
            const active = list.includes(button.dataset.id);
            button.classList.toggle("active", active);
            button.setAttribute("aria-label", active ? "Remove from wishlist" : "Add to wishlist");
        });

        const count = document.getElementById("wishlistCount");
        if (count) count.textContent = list.length;
    }

    function toggleWishlist(id) {
        let list = getWishlist();
        list = list.includes(id) ? list.filter(item => item !== id) : list.concat(id);
        saveWishlist(list);
        refreshHearts();
        document.dispatchEvent(new CustomEvent("chitrabaddh:wishlist"));
    }


    // =====================================
    // NAVIGATION
    // =====================================

    function setupNavigation() {
        const header = document.getElementById("siteHeader");
        const toggle = document.querySelector(".nav-toggle");
        const nav = document.getElementById("siteNav");

        if (!header || !toggle || !nav) return;

        function closeMenu() {
            header.classList.remove("menu-open");
            toggle.setAttribute("aria-expanded", "false");
            toggle.setAttribute("aria-label", "Open menu");
        }

        toggle.addEventListener("click", function () {
            const open = header.classList.toggle("menu-open");
            toggle.setAttribute("aria-expanded", String(open));
            toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        });

        // Close the mobile menu after choosing a link
        nav.querySelectorAll("a").forEach(link => link.addEventListener("click", closeMenu));

        document.addEventListener("keydown", event => {
            if (event.key === "Escape") closeMenu();
        });

        // Shadow under the header once the page is scrolled
        function onScroll() {
            header.classList.toggle("scrolled", window.scrollY > 10);
        }

        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }


    // Home page: highlight the menu link of the section on screen
    function setupScrollSpy() {
        if (!document.body.classList.contains("home-page")) return;
        if (!("IntersectionObserver" in window)) return;

        const links = document.querySelectorAll(".nav-links a[data-section]");
        const sections = Array.from(links)
            .map(link => document.getElementById(link.dataset.section))
            .filter(Boolean);

        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;

                links.forEach(link => {
                    link.classList.toggle("active", link.dataset.section === entry.target.id);
                });
            });
        }, { rootMargin: "-45% 0px -50% 0px" });

        sections.forEach(section => observer.observe(section));
    }


    // =====================================
    // FADE-IN WHILE SCROLLING
    // =====================================

    function setupReveal() {
        const items = document.querySelectorAll(".reveal");
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        if (reduceMotion || !("IntersectionObserver" in window)) return;

        document.documentElement.classList.add("reveal-ready");

        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        items.forEach(item => observer.observe(item));
    }


    // =====================================
    // IMAGE VIEWER
    // =====================================

    function setupImageModal() {
        const modal = document.getElementById("imageModal");
        const modalImage = document.getElementById("modalImage");

        if (!modal || !modalImage) return;

        function close() {
            modal.classList.remove("open");
            modal.setAttribute("aria-hidden", "true");
            modalImage.src = "";
        }

        document.addEventListener("click", event => {
            const image = event.target.closest(".card img, img.zoomable");

            if (image) {
                modalImage.src = image.src;
                modalImage.alt = image.alt;
                modal.classList.add("open");
                modal.setAttribute("aria-hidden", "false");
                return;
            }

            if (event.target === modal || event.target.closest(".close-modal")) close();
        });

        document.addEventListener("keydown", event => {
            if (event.key === "Escape") close();
        });
    }


    // =====================================
    // START
    // =====================================

    function init() {
        setupNavigation();
        setupScrollSpy();
        setupReveal();
        setupImageModal();

        document.addEventListener("click", event => {
            const heart = event.target.closest(".wishlist-heart");
            if (heart) toggleWishlist(heart.dataset.id);
        });

        refreshHearts();

        // Hide the "welcome" message after a few seconds
        const toast = document.querySelector(".site-toast");
        if (toast) setTimeout(() => toast.classList.add("hide"), 4000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    return { getWishlist, refreshHearts };

})();
