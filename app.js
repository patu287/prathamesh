/* ============================================
   LITTLE OWL CAFE — Dynamic JavaScript
   Premium interactions & animations
   ============================================ */

// --- Preloader ---
window.addEventListener('load', () => {
    setTimeout(() => {
        document.getElementById('preloader')?.classList.add('done');
    }, 1600);
});

// Fallback: force-hide preloader after 4 seconds no matter what
setTimeout(() => {
    document.getElementById('preloader')?.classList.add('done');
}, 4000);

// --- Custom Cursor ---
const cursorDot = document.querySelector('.cursor-dot');
const cursorRing = document.querySelector('.cursor-ring');

if (cursorDot && cursorRing && window.matchMedia('(pointer: fine)').matches) {
    let mouseX = 0, mouseY = 0;
    let ringX = 0, ringY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        cursorDot.style.left = mouseX + 'px';
        cursorDot.style.top = mouseY + 'px';
    });

    function animateRing() {
        ringX += (mouseX - ringX) * 0.15;
        ringY += (mouseY - ringY) * 0.15;
        cursorRing.style.left = ringX + 'px';
        cursorRing.style.top = ringY + 'px';
        requestAnimationFrame(animateRing);
    }
    animateRing();

    // Hover effect on interactive elements
    const hoverables = document.querySelectorAll('a, button, .menu-card, .g-item, .test-card, .menu-item, input, textarea, select');
    hoverables.forEach(el => {
        el.addEventListener('mouseenter', () => cursorRing.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursorRing.classList.remove('hover'));
    });
}

// --- Scroll Progress Bar ---
const scrollProgress = document.querySelector('.scroll-progress');
if (scrollProgress) {
    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        scrollProgress.style.width = scrollPercent + '%';
    });
}

// --- Sticky Navbar ---
const navbar = document.getElementById('navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
    navbar.classList.toggle('scrolled', window.scrollY > 50);
}

// --- Mobile Navigation ---
const navBurger = document.getElementById('navBurger');
const navLinks = document.getElementById('navLinks');

if (navBurger && navLinks) {
    navBurger.addEventListener('click', () => {
        navBurger.classList.toggle('open');
        navLinks.classList.toggle('open');
    });

    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navBurger.classList.remove('open');
            navLinks.classList.remove('open');
        });
    });

    document.addEventListener('click', (e) => {
        if (!navBurger.contains(e.target) && !navLinks.contains(e.target)) {
            navBurger.classList.remove('open');
            navLinks.classList.remove('open');
        }
    });
}

// --- Smooth Scroll for anchor links ---
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80;
            window.scrollTo({
                top: target.offsetTop - offset,
                behavior: 'smooth'
            });
        }
    });
});

// --- Scroll Reveal Animations ---
// Progressive enhancement: only hide elements if JS + IntersectionObserver work
if ('IntersectionObserver' in window) {
    document.documentElement.classList.add('js-ready');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0,
        rootMargin: '100px 0px -30px 0px'
    });

    document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => {
        revealObserver.observe(el);
    });

    // Safety net: force-reveal everything after 5 seconds no matter what
    setTimeout(() => {
        document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => {
            el.classList.add('show');
        });
    }, 5000);
}

// --- Back to Top Button ---
const toTop = document.getElementById('toTop');
if (toTop) {
    window.addEventListener('scroll', () => {
        toTop.classList.toggle('show', window.scrollY > 500);
    });

    toTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// --- Menu Page: Category Tabs ---
const menuTabs = document.getElementById('menuTabs');
if (menuTabs) {
    const tabs = menuTabs.querySelectorAll('.menu-tab');
    const categories = document.querySelectorAll('.menu-category');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const cat = tab.dataset.cat;
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show/hide categories with animation
            categories.forEach(c => {
                c.classList.remove('active');
                c.style.opacity = '0';
                c.style.transform = 'translateY(20px)';
            });

            const target = document.getElementById('cat-' + cat);
            if (target) {
                setTimeout(() => {
                    target.classList.add('active');
                    setTimeout(() => {
                        target.style.opacity = '1';
                        target.style.transform = 'translateY(0)';
                        target.style.transition = 'all 0.4s cubic-bezier(0, 0, 0.2, 1)';
                    }, 50);
                }, 200);
            }
        });
    });
}

// --- Gallery Lightbox ---
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');
const lightboxClose = document.getElementById('lightboxClose');

if (lightbox && lightboxImg && lightboxClose) {
    document.querySelectorAll('.g-item').forEach(item => {
        item.addEventListener('click', () => {
            const img = item.querySelector('img');
            if (img) {
                lightboxImg.src = img.src;
                lightboxImg.alt = img.alt;
                lightbox.classList.add('open');
                document.body.style.overflow = 'hidden';
            }
        });
    });

    const closeLightbox = () => {
        lightbox.classList.remove('open');
        document.body.style.overflow = '';
    };

    lightboxClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeLightbox();
    });
}

// --- Contact Form ---
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const btn = contactForm.querySelector('button[type="submit"]');
        const originalHTML = btn.innerHTML;
        
        btn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            Message Sent!
        `;
        btn.style.background = '#059669';
        btn.disabled = true;

        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = '';
            btn.disabled = false;
            contactForm.reset();
        }, 3000);
    });
}

// --- Parallax Hero ---
const heroImg = document.querySelector('.hero-bg img');
if (heroImg) {
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        if (scrolled < window.innerHeight) {
            heroImg.style.transform = `scale(1.1) translateY(${scrolled * 0.3}px)`;
        }
    });
}

// --- Magnetic Buttons ---
document.querySelectorAll('.btn-primary, .btn-dark, .nav-cta').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });

    btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
    });
});

// --- Menu Item Hover Animation ---
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('mouseenter', () => {
        const emoji = item.querySelector('.menu-item-emoji');
        if (emoji) {
            emoji.style.transform = 'scale(1.1) rotate(-5deg)';
            emoji.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
        }
    });

    item.addEventListener('mouseleave', () => {
        const emoji = item.querySelector('.menu-item-emoji');
        if (emoji) {
            emoji.style.transform = '';
        }
    });
});

// --- Counter Animation for About Badge ---
const aboutBadge = document.querySelector('.about-badge-num');
if (aboutBadge) {
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                let count = 0;
                const target = 1000;
                const increment = target / 60;
                const timer = setInterval(() => {
                    count += increment;
                    if (count >= target) {
                        aboutBadge.textContent = '1K+';
                        clearInterval(timer);
                    } else {
                        aboutBadge.textContent = Math.floor(count);
                    }
                }, 16);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counterObserver.observe(aboutBadge);
}

// --- Staggered Gallery Load ---
document.querySelectorAll('.g-item img').forEach((img, i) => {
    img.style.opacity = '0';
    img.style.transform = 'scale(0.9)';
    img.style.transition = `all 0.6s cubic-bezier(0, 0, 0.2, 1) ${i * 0.1}s`;

    const imgObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    img.style.opacity = '1';
                    img.style.transform = 'scale(1)';
                }, 100);
                imgObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    imgObserver.observe(img);
});

// --- Easter Egg: Owl Click ---
document.querySelectorAll('.nav-brand-icon').forEach(owl => {
    owl.addEventListener('click', (e) => {
        e.preventDefault();
        owl.style.animation = 'none';
        owl.offsetHeight;
        owl.style.animation = 'owlBounce 0.6s ease-in-out 3';

        const hoot = document.createElement('span');
        hoot.textContent = 'Hoo! 🦉';
        hoot.style.cssText = `
            position: fixed; top: 80px; left: 50%; transform: translateX(-50%);
            font-family: var(--ff-display, Georgia); font-size: 1.5rem; color: var(--c-accent, #C4622D);
            z-index: 9999; pointer-events: none;
            animation: hootAnim 1.5s ease forwards;
        `;

        const hootStyle = document.createElement('style');
        hootStyle.textContent = `
            @keyframes hootAnim {
                0% { opacity: 0; transform: translateX(-50%) translateY(0); }
                30% { opacity: 1; transform: translateX(-50%) translateY(-20px); }
                100% { opacity: 0; transform: translateX(-50%) translateY(-60px); }
            }
        `;
        document.head.appendChild(hootStyle);
        document.body.appendChild(hoot);

        setTimeout(() => {
            document.body.removeChild(hoot);
            document.head.removeChild(hootStyle);
        }, 1500);
    });
});

// --- Console Easter Egg ---
console.log('%c🦉 Little Owl Cafe', 'font-size: 24px; font-weight: bold; color: #C4622D;');
console.log('%cYour Neighbourhood Boutique Cafe — Nagpur', 'font-size: 14px; color: #C89F6D;');
