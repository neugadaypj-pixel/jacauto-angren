/* ============================================
   JAC MOTORS ANGREN - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initPreloader();
    initCustomCursor();
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

/* ---------- Preloader ---------- */
function initPreloader() {
    const preloader = document.getElementById('preloader');
    if (!preloader) return;
    
    window.addEventListener('load', () => {
        setTimeout(() => {
            preloader.classList.add('hidden');
            // Remove from DOM after animation
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }, 600);
    });
}

/* ---------- Custom Cursor ---------- */
function initCustomCursor() {
    const cursor = document.getElementById('customCursor');
    const dot = document.getElementById('cursorDot');
    if (!cursor || !dot) return;
    
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Dot follows instantly
        dot.style.left = mouseX + 'px';
        dot.style.top = mouseY + 'px';
    });
    
    // Smooth follow for ring cursor
    function animateCursor() {
        cursorX += (mouseX - cursorX) * 0.15;
        cursorY += (mouseY - cursorY) * 0.15;
        
        cursor.style.left = cursorX + 'px';
        cursor.style.top = cursorY + 'px';
        
        requestAnimationFrame(animateCursor);
    }
    animateCursor();
    
    // Hover effects
    const hoverTargets = document.querySelectorAll('a, button, .hamburger, .step-header, input, select, textarea');
    
    hoverTargets.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.classList.add('hover');
            dot.classList.add('hidden');
        });
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('hover');
            dot.classList.remove('hidden');
        });
    });
    
    // Hide default cursor
    document.body.style.cursor = 'none';
    
    // Hide custom cursor when leaving window
    document.addEventListener('mouseleave', () => {
        cursor.classList.add('hidden');
        dot.classList.add('hidden');
    });
    
    document.addEventListener('mouseenter', () => {
        cursor.classList.remove('hidden');
        dot.classList.remove('hidden');
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
        rootMargin: '0px 0px -80px 0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.aosDelay || 0;
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
                    <h3 style="margin-bottom:8px;">Заявка отправлена!</h3>
                    <p style="color:#8890A4;">Мы свяжемся с вами в ближайшее время</p>
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

/* ---------- Counter Animation ---------- */
function animateCounter(el, target, duration = 2000) {
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out cubic
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (target - start) * easeProgress);
        
        el.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = target;
        }
    }
    
    requestAnimationFrame(update);
}

// Observe counter badge
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const numberEl = entry.target.querySelector('.badge-number');
            if (numberEl) {
                const text = numberEl.textContent;
                const match = text.match(/(\d+)/);
                if (match) {
                    const target = parseInt(match[1]);
                    // Clear existing and animate
                    numberEl.innerHTML = '<span class="count-num">0</span><span>+</span>';
                    const numSpan = numberEl.querySelector('.count-num');
                    animateCounter(numSpan, target);
                }
            }
            counterObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const badge = document.querySelector('.about-badge');
if (badge) {
    counterObserver.observe(badge);
}