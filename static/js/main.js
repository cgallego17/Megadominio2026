// Main JavaScript for Megadominio — Advanced Parallax & Interactions

(function () {
    'use strict';

    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const noEffects = isMobile || prefersReduced;

    // Smooth lerp helper
    function lerp(a, b, t) { return a + (b - a) * t; }

    document.addEventListener('DOMContentLoaded', function () {
        initSmoothScroll();
        initNavbar();
        if (!noEffects) {
            initScrollParallax();
            initHeroMouseParallax();
            initCard3DTilt();
            initRevealOnScroll();
            initMagneticButtons();
            initCounterAnimation();
            initCursorGlow();
            initFloatingParticles();
            initMobileHaptics();
        } else {
            // Make everything visible immediately on mobile
            document.querySelectorAll('[data-reveal]').forEach(function (el) {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
            initMobileHaptics();
        }
    });

    // ── Smooth Scroll ──────────────────────────────────────────────
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (link) {
            link.addEventListener('click', function (e) {
                var href = this.getAttribute('href');
                if (href === '#') return;
                var target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // ── Navbar ─────────────────────────────────────────────────────
    function initNavbar() {
        var navbar = document.querySelector('nav');
        if (!navbar) return;
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 60) {
                navbar.classList.add('nav-scrolled');
            } else {
                navbar.classList.remove('nav-scrolled');
            }
        }, { passive: true });
    }

    // ── Scroll-based Parallax (background blobs & cards) ──────────
    function initScrollParallax() {
        var els = document.querySelectorAll('[data-parallax-speed]');
        if (!els.length) return;

        var current = {};
        var target = {};

        els.forEach(function (el, i) {
            current[i] = 0;
            target[i] = 0;
        });

        function tick() {
            var scrolled = window.pageYOffset;
            var vh = window.innerHeight;

            els.forEach(function (el, i) {
                var speed = parseFloat(el.getAttribute('data-parallax-speed')) || 0.3;
                var rect = el.getBoundingClientRect();
                var elTop = rect.top + scrolled;

                if (scrolled + vh > elTop - 300 && scrolled < elTop + rect.height + 300) {
                    target[i] = (scrolled - elTop) * speed;
                }

                current[i] = lerp(current[i], target[i], 0.08);
                el.style.transform = 'translate3d(0,' + current[i].toFixed(2) + 'px,0)';
            });

            requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
    }

    // ── Hero Mouse Parallax (depth layers) ────────────────────────
    function initHeroMouseParallax() {
        var hero = document.querySelector('#hero-section');
        if (!hero) return;

        var cards = hero.querySelectorAll('[data-parallax-card]');
        var blobs = hero.querySelectorAll('[data-parallax-speed]');
        if (!cards.length && !blobs.length) return;

        var mx = { current: 0, target: 0 };
        var my = { current: 0, target: 0 };

        hero.addEventListener('mousemove', function (e) {
            var rect = hero.getBoundingClientRect();
            mx.target = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
            my.target = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
        }, { passive: true });

        hero.addEventListener('mouseleave', function () {
            mx.target = 0;
            my.target = 0;
        });

        function tick() {
            mx.current = lerp(mx.current, mx.target, 0.06);
            my.current = lerp(my.current, my.target, 0.06);

            cards.forEach(function (card, i) {
                var depth = 15 + i * 8;
                var rx = my.current * 6;
                var ry = -mx.current * 6;
                var tx = mx.current * depth;
                var ty = my.current * depth;
                card.style.transform =
                    'perspective(800px) translate3d(' + tx.toFixed(2) + 'px,' + ty.toFixed(2) + 'px,0) ' +
                    'rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg)';
            });

            blobs.forEach(function (blob) {
                var s = parseFloat(blob.getAttribute('data-parallax-speed')) || 0.2;
                var bx = mx.current * 40 * s;
                var by = my.current * 40 * s;
                blob.style.transform = 'translate3d(' + bx.toFixed(2) + 'px,' + by.toFixed(2) + 'px,0)';
            });

            requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
    }

    // ── 3D Card Tilt on Hover ─────────────────────────────────────
    function initCard3DTilt() {
        document.querySelectorAll('.group, [data-tilt]').forEach(function (card) {
            var shine = document.createElement('div');
            shine.className = 'tilt-shine';
            card.style.position = 'relative';
            card.style.overflow = 'hidden';
            card.appendChild(shine);

            card.addEventListener('mousemove', function (e) {
                var rect = card.getBoundingClientRect();
                var x = (e.clientX - rect.left) / rect.width;
                var y = (e.clientY - rect.top) / rect.height;
                var rx = (y - 0.5) * 14;
                var ry = (0.5 - x) * 14;

                card.style.transform =
                    'perspective(600px) rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg) scale(1.03)';
                shine.style.opacity = '1';
                shine.style.background =
                    'radial-gradient(circle at ' + (x * 100) + '% ' + (y * 100) + '%, rgba(255,255,255,0.15), transparent 60%)';
            });

            card.addEventListener('mouseleave', function () {
                card.style.transform = 'perspective(600px) rotateX(0) rotateY(0) scale(1)';
                shine.style.opacity = '0';
            });
        });
    }

    // ── Reveal on Scroll (staggered) ──────────────────────────────
    function initRevealOnScroll() {
        // Auto-tag elements
        var selectors = [
            'section > div > .text-center',
            '.grid > div',
            'section h2',
            'section p.text-xl',
            '.process-step',
            '.testimonial-card'
        ];

        var idx = 0;
        selectors.forEach(function (sel) {
            document.querySelectorAll(sel).forEach(function (el) {
                if (!el.hasAttribute('data-reveal')) {
                    el.setAttribute('data-reveal', '');
                    el.setAttribute('data-reveal-delay', (idx % 6) * 80);
                    idx++;
                }
            });
        });

        var revealEls = document.querySelectorAll('[data-reveal]');

        revealEls.forEach(function (el) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(40px)';
            el.style.transition = 'opacity 0.7s cubic-bezier(.16,1,.3,1), transform 0.7s cubic-bezier(.16,1,.3,1)';
        });

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var delay = parseInt(entry.target.getAttribute('data-reveal-delay')) || 0;
                    setTimeout(function () {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, delay);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        revealEls.forEach(function (el) { observer.observe(el); });
    }

    // ── Magnetic Buttons ──────────────────────────────────────────
    function initMagneticButtons() {
        document.querySelectorAll('a.bg-red-600, a.border-2, button.bg-red-600').forEach(function (btn) {
            btn.classList.add('magnetic-btn');

            btn.addEventListener('mousemove', function (e) {
                var rect = btn.getBoundingClientRect();
                var cx = rect.left + rect.width / 2;
                var cy = rect.top + rect.height / 2;
                var dx = (e.clientX - cx) * 0.25;
                var dy = (e.clientY - cy) * 0.25;
                btn.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px) scale(1.04)';
            });

            btn.addEventListener('mouseleave', function () {
                btn.style.transform = 'translate(0,0) scale(1)';
            });
        });
    }

    // ── Counter Animation (hero stats) ────────────────────────────
    function initCounterAnimation() {
        var statEls = document.querySelectorAll('[class*="text-4xl"][class*="font-bold"]');
        if (!statEls.length) return;

        statEls.forEach(function (el) {
            var text = el.textContent.trim();
            var match = text.match(/^(\d+)/);
            if (!match) return;

            var endVal = parseInt(match[1]);
            var suffix = text.replace(match[1], '');
            el.setAttribute('data-counter', endVal);
            el.setAttribute('data-suffix', suffix);
            el.textContent = '0' + suffix;
        });

        var counterObs = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                var end = parseInt(el.getAttribute('data-counter'));
                var suffix = el.getAttribute('data-suffix') || '';
                if (!end) return;

                var start = 0;
                var duration = 2000;
                var startTime = null;

                function step(ts) {
                    if (!startTime) startTime = ts;
                    var progress = Math.min((ts - startTime) / duration, 1);
                    var eased = 1 - Math.pow(1 - progress, 4);
                    var val = Math.floor(eased * end);
                    el.textContent = val + suffix;
                    if (progress < 1) requestAnimationFrame(step);
                }

                requestAnimationFrame(step);
                counterObs.unobserve(el);
            });
        }, { threshold: 0.5 });

        document.querySelectorAll('[data-counter]').forEach(function (el) {
            counterObs.observe(el);
        });
    }

    // ── Cursor Glow ───────────────────────────────────────────────
    function initCursorGlow() {
        var glow = document.createElement('div');
        glow.className = 'cursor-glow';
        document.body.appendChild(glow);

        var gx = { current: -100, target: -100 };
        var gy = { current: -100, target: -100 };

        document.addEventListener('mousemove', function (e) {
            gx.target = e.clientX;
            gy.target = e.clientY;
        }, { passive: true });

        function tick() {
            gx.current = lerp(gx.current, gx.target, 0.12);
            gy.current = lerp(gy.current, gy.target, 0.12);
            glow.style.left = gx.current + 'px';
            glow.style.top = gy.current + 'px';
            requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);

        // Enlarge glow on interactive elements
        document.querySelectorAll('a, button').forEach(function (el) {
            el.addEventListener('mouseenter', function () { glow.classList.add('glow-active'); });
            el.addEventListener('mouseleave', function () { glow.classList.remove('glow-active'); });
        });
    }

    // ── Floating Particles ────────────────────────────────────────
    function initFloatingParticles() {
        var hero = document.querySelector('#hero-section');
        if (!hero) return;

        var canvas = document.createElement('canvas');
        canvas.className = 'particles-canvas';
        hero.appendChild(canvas);

        var ctx = canvas.getContext('2d');
        var particles = [];
        var count = 40;

        function resize() {
            canvas.width = hero.offsetWidth;
            canvas.height = hero.offsetHeight;
        }

        resize();
        window.addEventListener('resize', resize);

        for (var i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: Math.random() * 2 + 0.5,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                alpha: Math.random() * 0.4 + 0.1
            });
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (var i = 0; i < particles.length; i++) {
                var p = particles[i];
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(220,38,38,' + p.alpha + ')';
                ctx.fill();

                // Draw connections
                for (var j = i + 1; j < particles.length; j++) {
                    var q = particles[j];
                    var dx = p.x - q.x;
                    var dy = p.y - q.y;
                    var dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(q.x, q.y);
                        ctx.strokeStyle = 'rgba(220,38,38,' + (0.08 * (1 - dist / 120)) + ')';
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }

            requestAnimationFrame(draw);
        }

        draw();
    }

    // ── Mobile Haptics (Vibration API) ────────────────────────────
    function initMobileHaptics() {
        if (!navigator.vibrate) return;

        // Browser blocks vibrate until user has tapped on the page
        var userTapped = false;
        document.addEventListener('pointerdown', function () { userTapped = true; }, { once: true });

        function vibrateLight() { if (userTapped) try { navigator.vibrate(12); } catch(e) {} }
        function vibrateMedium() { if (userTapped) try { navigator.vibrate(25); } catch(e) {} }

        // Vibrate on tap/click of service links and CTA buttons
        document.querySelectorAll(
            'a[href*="servicios"], a[href*="cotizar"], a.bg-red-600, button.bg-red-600'
        ).forEach(function (el) {
            el.addEventListener('click', vibrateMedium);
        });
    }

})();
