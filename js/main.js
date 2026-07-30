/* ============================================
   JAC MOTORS ANGREN — Premium JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initPreloader();
    initHeader();
    initRevealAnimations();
    initCounters();
    initModelTabs();
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
        });
    });
}

/* --- Mobile menu --- */
function initMobileMenu() {
    const hamburger = document.getElementById('hamburger');
    const nav = document.getElementById('nav');
    if (!hamburger || !nav) return;
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        nav.classList.toggle('active');
        document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
    });
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            nav.classList.remove('active');
            document.body.style.overflow = '';
        });
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
                alert(data.error || 'Ошибка отправки. Позвоните нам: 78 113 10 08');
            }
        } catch (err) {
            btn.innerHTML = origText;
            btn.disabled = false;
            alert('Сервер временно недоступен. Позвоните нам: 78 113 10 08');
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
