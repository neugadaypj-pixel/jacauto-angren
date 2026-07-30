/* ============================================
   JAC MOTORS ANGREN - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initHeroTypewriter();
    initPreloader();
    initHeader();
    initHeroSlider();
    initModelsSlider();
    initMobileMenu();
    initAccordion();
    initAOS();
    initSmoothScroll();
    initForm();
    initScrollNavHighlight();
});

/* ---------- Hero Typewriter (letter-by-letter reveal) ---------- */
function initHeroTypewriter() {
    const lines = document.querySelectorAll('.hero-title-line');
    const subtitle = document.querySelector('.hero-subtitle');
    const buttons = document.querySelector('.hero-buttons');
    const social = document.querySelector('.hero-social');
    
    // Hide subtitle/buttons/social initially
    if (subtitle) { subtitle.style.opacity = '0'; subtitle.style.transform = 'translateY(30px)'; }
    if (buttons) { buttons.style.opacity = '0'; buttons.style.transform = 'translateY(30px)'; }
    if (social) { social.style.opacity = '0'; social.style.transform = 'translateY(30px)'; }
    
    let totalDuration = 0;
    
    // Animate each title line letter by letter
    lines.forEach((line, lineIndex) => {
        const text = line.textContent;
        line.textContent = '';
        line.style.opacity = '1';
        
        [...text].forEach((char, i) => {
            const span = document.createElement('span');
            span.className = 'hero-char';
            span.textContent = char === ' ' ? '\u00A0' : char;
            span.style.cssText = `
                opacity:0;
                display:inline-block;
                transform:translateY(40px) rotateX(-90deg);
                transition:opacity 0.3s ease,transform 0.45s cubic-bezier(0.22,1,0.36,1);
            `;
            line.appendChild(span);
            
            const delay = lineIndex * 1200 + i * 45;
            totalDuration = Math.max(totalDuration, delay);
            
            setTimeout(() => {
                span.style.opacity = '1';
                span.style.transform = 'translateY(0) rotateX(0)';
            }, delay);
        });
    });
    
    // Reveal subtitle, buttons, social after title animation
    const fadeIn = (el, delay) => {
        setTimeout(() => {
            if (el) {
                el.style.transition = 'opacity 0.6s ease,transform 0.6s cubic-bezier(0.22,1,0.36,1)';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }
        }, delay);
    };
    
    fadeIn(subtitle, totalDuration - 200);
    fadeIn(buttons, totalDuration + 100);
    fadeIn(social, totalDuration + 400);
}

/* ---------- Preloader ---------- */
function initPreloader() {
    const preloader = document.getElementById('preloader');
    if (!preloader) return;
    
    window.addEventListener('load', () => {
        setTimeout(() => {
            preloader.classList.add('hidden');
            // Remove from DOM after animation
            setTimeout(() => {
                if (preloader) preloader.style.display = 'none';
            }, 500);
        }, 600);
    });
}

/* ---------- Header Scroll Effect ---------- */
function initHeader() {
    const header = document.getElementById('header');
    if (!header) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

/* ---------- Hero Slider ---------- */
function initHeroSlider() {
    const sliderEl = document.getElementById('heroSlider');
    if (!sliderEl) return;
    
    new Swiper(sliderEl, {
        slidesPerView: 1,
        loop: true,
        effect: 'fade',
        fadeEffect: { crossFade: true },
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
        speed: 800,
        allowTouchMove: false,
    });
}

/* ---------- Models Slider ---------- */
function initModelsSlider() {
    const sliderEl = document.getElementById('modelsSlider');
    if (!sliderEl) return;
    
    new Swiper(sliderEl, {
        slidesPerView: 1,
        spaceBetween: 24,
        loop: true,
        autoplay: {
            delay: 3500,
            disableOnInteraction: false,
        },
        speed: 600,
        navigation: {
            prevEl: '.swiper-button-prev',
            nextEl: '.swiper-button-next',
        },
        breakpoints: {
            640: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
        }
    });
}

/* ---------- Mobile Menu ---------- */
function initMobileMenu() {
    const hamburger = document.getElementById('hamburger');
    const nav = document.getElementById('nav');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (!hamburger || !nav) return;
    
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        nav.classList.toggle('active');
        document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
    });
    
    // Close menu on link click
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            nav.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
    
    // Close menu on Escape
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
    const stepHeaders = document.querySelectorAll('.step-header');
    
    stepHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const step = header.parentElement;
            const isActive = step.classList.contains('active');
            
            // Close all
            document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
            
            // Open clicked (if wasn't already active)
            if (!isActive) {
                step.classList.add('active');
            }
        });
    });
}

/* ---------- AOS (Animate On Scroll) ---------- */
function initAOS() {
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -50px 0px',
        threshold: 0.05
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.dataset.aosDelay) || 0;
                setTimeout(() => {
                    entry.target.classList.add('aos-animate');
                }, delay);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('[data-aos]').forEach(el => {
        observer.observe(el);
    });
    
    // Fallback: if any elements are already in view after 800ms, reveal them
    setTimeout(() => {
        document.querySelectorAll('[data-aos]:not(.aos-animate)').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight + 100) {
                const delay = parseInt(el.dataset.aosDelay) || 0;
                setTimeout(() => {
                    el.classList.add('aos-animate');
                }, delay);
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
            
            const headerHeight = 80;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
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
        const scrollPos = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

/* ---------- Contact Form ---------- */
function initForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Simple validation
        const inputs = form.querySelectorAll('input[required]');
        let valid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                valid = false;
                input.style.borderColor = '#FF3600';
                setTimeout(() => {
                    input.style.borderColor = '';
                }, 2000);
            }
        });
        
        if (!valid) return;
        
        // Simulate submission
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';
        btn.disabled = true;
        
        setTimeout(() => {
            // Success state
            form.innerHTML = `
                <div class="form-success" style="text-align:center;padding:40px 20px;">
                    <div style="width:80px;height:80px;background:rgba(255,54,0,0.1);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
                        <i class="fas fa-check" style="color:#FF3600;font-size:32px;"></i>
                    </div>
                    <h3>Заявка отправлена!</h3>
                    <p style="color:#6b7280;">Мы свяжемся с вами в ближайшее время</p>
                </div>
            `;
            
            // Reset after 5 seconds
            setTimeout(() => {
                window.location.reload();
            }, 5000);
        }, 1500);
    });
}

/* ---------- Parallax Effect on Hero ---------- */
window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const heroContent = document.querySelector('.hero-content');
    
    if (heroContent && scrollY < window.innerHeight) {
        heroContent.style.transform = `translateY(${scrollY * 0.3}px)`;
        heroContent.style.opacity = 1 - scrollY / (window.innerHeight * 0.8);
    }
});
