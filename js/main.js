/* ============================================
   JAC MOTORS ANGREN — Premium JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initPreloader();
    initHeader();
    initRevealAnimations();
    initCounters();
    initModelTabs();
    initModelCarousel();
    initModelCardClicks();
    initMobileMenu();
    initSmoothScroll();
    initForm();
    initNavHighlight();
});

/* --- Preloader --- */
function initPreloader() {
    const p = document.getElementById('preloader');
    if (!p) return;
    window.addEventListener('load', () => {
        setTimeout(() => p.classList.add('hidden'), 500);
        setTimeout(() => { if(p) p.remove(); }, 1000);
    });
}

/* --- Header scroll --- */
function initHeader() {
    const header = document.getElementById('header');
    if (!header) return;
    window.addEventListener('scroll', () => {
        header.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
}

/* --- Reveal animations --- */
function initRevealAnimations() {
    const reveals = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');
    if (!reveals.length) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => entry.target.classList.add('revealed'), Math.min(i * 80, 400));
                observer.unobserve(entry.target);
            }
        });
    }, { rootMargin: '0px 0px -40px 0px', threshold: 0.1 });
    reveals.forEach(el => observer.observe(el));
}

/* --- Counter animation --- */
function initCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    if (!counters.length) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.dataset.count);
                const duration = 2000;
                const start = performance.now();
                function update(now) {
                    const p = Math.min((now - start) / duration, 1);
                    const ease = 1 - Math.pow(1 - p, 4);
                    el.textContent = Math.floor(ease * target);
                    if (p < 1) requestAnimationFrame(update);
                    else el.textContent = target;
                }
                requestAnimationFrame(update);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });
    counters.forEach(c => observer.observe(c));
}

/* --- Model filter tabs --- */
function initModelTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const cards = document.querySelectorAll('.model-card');
    if (!tabs.length || !cards.length) return;
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const filter = tab.dataset.filter;
            cards.forEach((card, i) => {
                if (filter === 'all' || card.dataset.cat === filter) {
                    card.classList.remove('hidden-card');
                    card.style.animation = `fadeIn 0.4s ease ${i * 0.06}s both`;
                } else {
                    card.classList.add('hidden-card');
                    card.style.animation = '';
                }
            });
            // Rebuild carousel dots after filtering
            if (window.rebuildCarouselDots) window.rebuildCarouselDots();
        });
    });
}

/* --- Model carousel (mobile swipe) --- */
function initModelCarousel() {
    const grid = document.getElementById('modelsGrid');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');
    const dotsContainer = document.getElementById('carouselDots');
    if (!grid || !prevBtn || !nextBtn || !dotsContainer) return;

    const isCarouselActive = () => window.innerWidth <= 768;

    function getVisibleCards() {
        return Array.from(grid.querySelectorAll('.model-card')).filter(c => !c.classList.contains('hidden-card'));
    }

    function scrollToCard(index) {
        const cards = getVisibleCards();
        if (index < 0 || index >= cards.length) return;
        const card = cards[index];
        const gridRect = grid.getBoundingClientRect();
        const cardRect = card.getBoundingClientRect();
        const scrollOffset = grid.scrollLeft + cardRect.left - gridRect.left - (grid.clientWidth - card.offsetWidth) / 2;
        grid.scrollTo({ left: scrollOffset, behavior: 'smooth' });
    }

    function getCurrentIndex() {
        const cards = getVisibleCards();
        if (!cards.length) return 0;
        const gridCenter = grid.scrollLeft + grid.clientWidth / 2;
        let closest = 0;
        let closestDist = Infinity;
        cards.forEach((card, i) => {
            const cardCenter = card.offsetLeft + card.offsetWidth / 2;
            const dist = Math.abs(gridCenter - cardCenter);
            if (dist < closestDist) { closest = i; closestDist = dist; }
        });
        return closest;
    }

    function updateDots() {
        const cards = getVisibleCards();
        const dots = dotsContainer.querySelectorAll('.carousel-dot');
        const current = getCurrentIndex();
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === current);
        });
        prevBtn.disabled = current === 0;
        nextBtn.disabled = current >= cards.length - 1;
    }

    var _rebuildLock = false;
    function rebuildCarouselDots() {
        if (!isCarouselActive()) return;
        if (_rebuildLock) return;
        _rebuildLock = true;
        // Triple-clear to guarantee no ghost nodes survive
        dotsContainer.innerHTML = '';
        dotsContainer.textContent = '';
        var child;
        while ((child = dotsContainer.firstChild)) { child.remove(); }
        
        const cards = getVisibleCards();
        cards.forEach(function(_, i) {
            var dot = document.createElement('button');
            dot.className = 'carousel-dot';
            dot.setAttribute('aria-label', 'Модель ' + (i + 1));
            dot.addEventListener('click', (function(idx) { return function(e) { e.preventDefault(); scrollToCard(idx); }; })(i));
            dotsContainer.appendChild(dot);
        });
        updateDots();
        _rebuildLock = false;
    }

    // Expose to global scope so model tabs can call it
    window.rebuildCarouselDots = rebuildCarouselDots;

    // Arrow buttons
    prevBtn.addEventListener('click', function() {
        var idx = getCurrentIndex();
        if (idx > 0) scrollToCard(idx - 1);
    });
    nextBtn.addEventListener('click', function() {
        var idx = getCurrentIndex();
        var cards = getVisibleCards();
        if (idx < cards.length - 1) scrollToCard(idx + 1);
    });

    // Scroll listener to update dots
    grid.addEventListener('scroll', updateDots, { passive: true });

    // Only show/hide dots on resize — don't rebuild
    window.addEventListener('resize', function() {
        if (isCarouselActive()) {
            dotsContainer.style.display = 'flex';
        } else {
            dotsContainer.style.display = 'none';
        }
    });

    // Initial build if mobile
    if (isCarouselActive()) {
        console.log('[DOTS] initial build on page load');
        rebuildCarouselDots();
    }
}

/* --- Clickable model cards — entire card navigates to car page --- */
function initModelCardClicks() {
    const grid = document.getElementById('modelsGrid');
    if (!grid) return;

    grid.addEventListener('click', function(e) {
        // Find the closest .model-card ancestor
        const card = e.target.closest('.model-card');
        if (!card) return;

        // If user clicked the explicit link, let it handle natively
        if (e.target.closest('.model-link')) return;

        // Otherwise navigate via the card's inner link href
        const link = card.querySelector('.model-link');
        if (link) {
            window.location.href = link.getAttribute('href');
        }
    });
}

/* --- Mobile menu --- */
function initMobileMenu() {
    const hamburger = document.getElementById('hamburger');
    const nav = document.getElementById('nav');
    if (!hamburger || !nav) return;

    const overlay = document.createElement('div');
    overlay.className = 'nav-overlay';
    document.body.appendChild(overlay);

    // Prevent scroll-through on the underlay while menu is open
    function preventScroll(e) {
        e.preventDefault();
    }

    const closeMenu = () => {
        hamburger.classList.remove('active');
        nav.classList.remove('active');
        overlay.classList.remove('active');
        document.documentElement.classList.remove('menu-open');
        document.removeEventListener('touchmove', preventScroll, { passive: false });
    };

    const openMenu = () => {
        hamburger.classList.add('active');
        nav.classList.add('active');
        overlay.classList.add('active');
        document.documentElement.classList.add('menu-open');
        document.addEventListener('touchmove', preventScroll, { passive: false });
    };

    hamburger.addEventListener('click', (e) => {
        e.preventDefault();
        nav.classList.contains('active') ? closeMenu() : openMenu();
    });

    overlay.addEventListener('click', closeMenu);
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', closeMenu);
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && nav.classList.contains('active')) closeMenu();
    });
    window.addEventListener('resize', () => {
        if (window.innerWidth > 1024 && nav.classList.contains('active')) closeMenu();
    });
}

/* --- Smooth scroll --- */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const id = this.getAttribute('href');
            if (id === '#') return;
            const target = document.querySelector(id);
            if (!target) return;
            e.preventDefault();
            window.scrollTo({ top: target.offsetTop - 80, behavior: 'smooth' });
        });
    });
}

/* --- Contact form --- */
function initForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const nameInput = form.querySelector('input[type="text"]');
        const phoneInput = form.querySelector('input[type="tel"]');
        const modelSelect = form.querySelector('select');
        const commentInput = form.querySelector('textarea');

        const name = nameInput ? nameInput.value.trim() : '';
        const phone = phoneInput ? phoneInput.value.trim() : '';
        const model = modelSelect ? modelSelect.value : '';
        const comment = commentInput ? commentInput.value.trim() : '';

        // Validate
        let valid = true;
        if (!name) { nameInput.style.borderColor = '#E0311A'; valid = false; }
        if (!phone) { phoneInput.style.borderColor = '#E0311A'; valid = false; }
        if (!valid) return;

        const btn = form.querySelector('button[type="submit"]');
        const origText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';
        btn.disabled = true;

        // Send to backend
        try {
            const API_URL = 'https://jacauto-angren-bot.onrender.com/api/submit';
            const res = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, phone, model, comment })
            });

            const data = await res.json();

            if (data.ok) {
                form.innerHTML = '<div style="text-align:center;padding:40px 0"><i class="fas fa-check-circle" style="font-size:48px;color:#E0311A;margin-bottom:16px"></i><h3>Заявка отправлена!</h3><p style="color:#8A8A8A;margin-top:8px">Мы свяжемся с вами в ближайшее время</p></div>';
            } else {
                btn.innerHTML = origText;
                btn.disabled = false;
                alert(data.error || 'Ошибка отправки. Позвоните нам: 71 200 77 11');
            }
        } catch (err) {
            btn.innerHTML = origText;
            btn.disabled = false;
            alert('Сервер временно недоступен. Позвоните нам: 71 200 77 11');
        }
    });
}

/* --- Nav highlight --- */
function initNavHighlight() {
    const sections = document.querySelectorAll('section[id]');
    const links = document.querySelectorAll('.nav-link');
    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(s => { if (window.scrollY + 150 >= s.offsetTop && window.scrollY + 150 < s.offsetTop + s.offsetHeight) current = s.id; });
        links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + current));
    }, { passive: true });
}

/* --- Parallax orbs --- */
window.addEventListener('scroll', () => {
    const y = window.scrollY;
    document.querySelectorAll('.hero-orb').forEach((orb, i) => {
        const speed = (i + 1) * 0.01;
        orb.style.transform = `translate(${y * speed}px, ${-y * speed * 1.5}px)`;
    });
}, { passive: true });

/* --- Inject card animation --- */
const style = document.createElement('style');
style.textContent = '@keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}';
document.head.appendChild(style);
