/* ============================================
   PREMIUM LOADING SCREEN
   ============================================ */

(function () {
    const preloader = document.getElementById('preloader');

    if (!preloader) return;

    // Function to hide preloader
    function hidePreloader() {
        preloader.classList.add('hidden');

        // Remove from DOM after animation completes
        setTimeout(() => {
            if (preloader.parentNode) {
                preloader.style.display = 'none';
            }
        }, 600);
    }

    // Hide preloader after page loads
    window.addEventListener('load', function () {
        // Add 1 second delay for better UX
        setTimeout(hidePreloader, 1000);
    });

    // Fallback: hide after 5 seconds maximum (in case something doesn't load)
    setTimeout(hidePreloader, 5000);
})();
/* ============================================
   DARK / LIGHT MODE TOGGLE
   ============================================ */
(function () {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    const icon = themeToggle.querySelector('i');
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateIcon(savedTheme);
    }

    themeToggle.addEventListener('click', function () {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateIcon(newTheme);
    });

    function updateIcon(theme) {
        icon.className = theme === 'light' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }
})();

/* ============================================
   AYAT AL-KURSI - INFINITE SLIDER (RIGHT TO LEFT)
   ============================================ */
(function () {
    const track = document.querySelector('.ayat-track');
    const item = document.querySelector('.ayat-item');
    const sliderContainer = document.querySelector('.ayat-slider');

    if (!track || !item || !sliderContainer) return;

    let isPaused = false;
    let animationId = null;
    const speed = 1.8;

    let itemWidth = item.offsetWidth;
    let containerWidth = sliderContainer.offsetWidth;

    /* يبدأ بحيث أول كلمة "الله" تظهر من أقصى الشمال */
    let position = -itemWidth;

    function animate() {
        if (!isPaused) {
            position += speed;

            /* لما يخرج كله من اليمين يرجع يبدأ من الشمال */
            if (position > containerWidth) {
                position = -itemWidth;
            }

            track.style.transform = `translateX(${position}px)`;
        }

        animationId = requestAnimationFrame(animate);
    }

    animate();

    sliderContainer.addEventListener('mouseenter', () => {
        isPaused = true;
    });

    sliderContainer.addEventListener('mouseleave', () => {
        isPaused = false;
    });

    let resizeTimeout;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            itemWidth = item.offsetWidth;
            containerWidth = sliderContainer.offsetWidth;

            if (position > containerWidth) {
                position = -itemWidth;
            }

            track.style.transform = `translateX(${position}px)`;
        }, 150);
    });
})();

// تتبع مشاهدات المشاريع
document.querySelectorAll('.project-card').forEach((card, index) => {
    const projectId = index + 1; // تأكد من ربطها بالـ ID الصحيح

    fetch(`/project/${projectId}/view`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
});

// عرض إحصائيات (اختياري)
async function loadStats() {
    const response = await fetch('/api/stats');
    const stats = await response.json();
    console.log('Page Views:', stats.page_views);
    console.log('Project Views:', stats.project_views);
}

