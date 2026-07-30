/* ============================================
   JAC MOTORS ANGREN - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initHeroReveal();
    initHeadingAnimations();
    initPreloader();
    initHeader();
    initModelsSlider();
    initMobileMenu();
    initAccordion();
    initAOS();
    initSmoothScroll();
    initForm();
    initScrollNavHighlight();
});

/* ---------- Hero Reveal (at-heading-animation-style-3 style — slide-up reveal) ---------- */
function initHeroReveal() {
    const lines = document.querySelectorAll('.hero-title-line');
    const subtitle = document.querySelector('.hero-subtitle');
    const buttons = document.querySelector('.hero-buttons');
    const social = document.querySelector('.hero-social');

    // Set initial state: hidden, translated down
    lines.forEach(line => {
        line.style.opacity = '0';
        line.style.transform = 'translateY(60px)';
        line.style.transition = 'opacity 0.8s cubic-bezier(0.22,1,0.36,1),transform 0.8s cubic-bezier(0.22,1,0.36,1)';
    });
    if (subtitle) { subtitle.style.opacity = '0'; subtitle.style.transform = 'translateY(40px)'; subtitle.style.transition = 'opacity 0.7s cubic-bezier(0.22,1,0.36,1),transform 0.7s cubic-bezier(0.22,1,0.36,1)'; }
    if (buttons) { buttons.style.opacity = '0'; buttons.style.transform = 'translateY(40px)'; buttons.style.transition = 'opacity 0.7s cubic-bezier(0.22,1,0.36,1),transform 0.7s cubic-bezier(0.22,1,0.36,1)'; }
    if (social) { social.style.opacity = '0'; social.style.transform = 'translateY(40px)'; social.style.transition = 'opacity 0.7s cubic-bezier(0.22,1,0.36,1),transform 0.7s cubic-bezier(0.22,1,0.36,1)'; }

    // Reveal line 1 immediately
    setTimeout(() => {
        if (lines[0]) { lines[0].style.opacity = '1'; lines[0].style.transform = 'translateY(0)'; }
    }, 200);

    // Reveal line 2
    setTimeout(() => {
        if (lines[1]) { lines[1].style.opacity = '1'; lines[1].style.transform = 'translateY(0)'; }
    }, 500);

    // Reveal line 3
    setTimeout(() => {
        if (lines[2]) { lines[2].style.opacity = '1'; lines[2].style.transform = 'translateY(0)'; }
    }, 800);

    // Reveal subtitle
    setTimeout(() => {
        if (subtitle) { subtitle.style.opacity = '1'; subtitle.style.transform = 'translateY(0)'; }
    }, 1100);

    // Reveal buttons
    setTimeout(() => {
        if (buttons) { buttons.style.opacity = '1'; buttons.style.transform = 'translateY(0)'; }
    }, 1300);

    // Reveal social links
    setTimeout(() => {
        if (social) { social.style.opacity = '1'; social.style.transform = 'translateY(0)'; }
    }, 1500);
}

/* ---------- All Section Heading Animations (at-heading-animation-style-3, fadeInUp) ---------- */
function initHeadingAnimations() {
    // Handle at-heading-animation-style-3 (section titles with red tag)
    const heading3s = document.querySelectorAll('.section-title, .section-tag, .at-heading-animation-style-3 .elementor-heading-title');
    heading3s.forEach(h => {
        h.style.opacity = '0';
        h.style.transform = 'translateY(60px)';
        h.style.transition = 'opacity 0.8s cubic-bezier(0.22,1,0.36,1),transform 0.8s cubic-bezier(0.22,1,0.36,1)';
    });

    // Handle fadeInUp elements (text blocks, about features, service cards)
    const fadeUps = document.querySelectorAll('.fadeInUp');
    fadeUps.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translate3d(0,40px,0)';
        el.style.transition = 'opacity 0.6s cubic-bezier(0.22,1,0.36,1),transform 0.6s cubic-bezier(0.22,1,0.36,1)';
    });

    // Observer that reveals elements when they scroll into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const delay = parseInt(el.dataset.animDelay) || 0;

                setTimeout(() => {
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0) translate3d(0,0,0)';
                }, delay);
                observer.unobserve(el);
            }
        });
    }, { rootMargin: '0px 0px -60px 0px', threshold: 0.1 });

    [...heading3s, ...fadeUps].forEach(el => observer.observe(el));
}

/* ---------- Preloader ---------- */
function initPreloader() {
    const preloader = document.getElementById('preloader');
    if (!preloader) return;

    window.addEventListener('load', () => {
        setTimeout(() => {
            preloader.classList.add('hidden');
            setTimeout(() => { if (preloader) preloader.style.display = 'none'; }, 500);
        }, 600);
    });
}

/* ---------- Header Scroll Effect ---------- */
function initHeader() {
    const header = document.getElementById('header');
    if (!header) return;
    window.addEventListener('scroll', () => {
        header.classList.toggle('scrolled', window.scrollY > 50);
    });
}

/* ---------- Models Slider ---------- */
function initModelsSlider() {
    const sliderEl = document.getElementById('modelsSlider');
    if (!sliderEl) return;
    new Swiper(sliderEl, {
        slidesPerView: 1, spaceBetween: 24, loop: true,
        autoplay: { delay: 3500, disableOnInteraction: false },
        speed: 600,
        navigation: { prevEl: '.swiper-button-prev', nextEl: '.swiper-button-next' },
        breakpoints: { 640: { slidesPerView: 2 }, 1024: { slidesPerView: 3 } }
    });
}

/* ---------- Mobile Menu ---------- */
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

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && nav.classList.contains('active')) {
            hamburger.classList.remove('active');
            nav.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

/* ---------- How We Work Accordion ---------- */
function initAccordion() {
    document.querySelectorAll('.step-header').forEach(header => {
        header.addEventListener('click', () => {
            const step = header.parentElement;
            const wasActive = step.classList.contains('active');
            document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
            if (!wasActive) step.classList.add('active');
        });
    });
}

/* ---------- AOS (Animate On Scroll) — for data-aos elements ---------- */
function initAOS() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.dataset.aosDelay) || 0;
                setTimeout(() => entry.target.classList.add('aos-animate'), delay);
                observer.unobserve(entry.target);
            }
        });
    }, { rootMargin: '0px 0px -50px 0px', threshold: 0.05 });

    document.querySelectorAll('[data-aos]').forEach(el => observer.observe(el));

    // Fallback
    setTimeout(() => {
        document.querySelectorAll('[data-aos]:not(.aos-animate)').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight + 100) {
                const delay = parseInt(el.dataset.aosDelay) || 0;
                setTimeout(() => el.classList.add('aos-animate'), delay);
            }
        });
    }, 800);
}

/* ---------- Smooth Scroll ---------- */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const target = document.querySelector(targetId);
            if (!target) return;
            e.preventDefault();
            window.scrollTo({ top: target.getBoundingClientRect().top + window.pageYOffset - 80, behavior: 'smooth' });
        });
    });
}

/* ---------- Scroll Nav Highlight ---------- */
function initScrollNavHighlight() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    if (!sections.length || !navLinks.length) return;

    window.addEventListener('scroll', () => {
        let current = '';
        const scrollPos = window.scrollY + 120;
        sections.forEach(section => {
            const top = section.offsetTop;
            if (scrollPos >= top && scrollPos < top + section.offsetHeight) current = section.getAttribute('id');
        });
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) link.classList.add('active');
        });
    });
}

/* ---------- Contact Form ---------- */
function initForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const inputs = form.querySelectorAll('input[required]');
        let valid = true;
        inputs.forEach(input => { if (!input.value.trim()) { valid = false; input.style.borderColor = '#FF3600'; setTimeout(() => input.style.borderColor = '', 2000); } });
        if (!valid) return;

        const btn = form.querySelector('button[type="submit"]');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';
        btn.disabled = true;

        setTimeout(() => {
            form.innerHTML = `
                <div class="form-success" style="text-align:center;padding:40px 20px;">
                    <div style="width:80px;height:80px;background:rgba(255,54,0,0.1);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
                        <i class="fas fa-check" style="color:#FF3600;font-size:32px;"></i>
                    </div>
                    <h3>Заявка отправлена!</h3>
                    <p style="color:#6b7280;">Мы свяжемся с вами в ближайшее время</p>
                </div>`;
            setTimeout(() => window.location.reload(), 5000);
        }, 1500);
    });
}

/* ---------- Parallax on Hero ---------- */
window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const heroContent = document.querySelector('.hero-content');
    if (heroContent && scrollY < window.innerHeight) {
        heroContent.style.transform = 'translateY(' + (scrollY * 0.3) + 'px)';
        heroContent.style.opacity = 1 - scrollY / (window.innerHeight * 0.8);
    }
});
