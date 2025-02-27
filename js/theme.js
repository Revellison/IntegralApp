document.addEventListener('DOMContentLoaded', function() {
    // Ждем загрузки header
    const headerCheck = setInterval(() => {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            clearInterval(headerCheck);
            initTheme(themeToggle);
        }
    }, 100);
});

function initTheme(themeToggle) {
    const icon = themeToggle.querySelector('i');
    
    // Загружаем сохраненную тему
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateIcon(icon, savedTheme);
    updateParticlesColor(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        updateIcon(icon, newTheme);
        updateParticlesColor(newTheme);
    });
}

function updateIcon(icon, theme) {
    icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

function updateParticlesColor(theme) {
    if (window.pJSDom && window.pJSDom[0]) {
        const pJS = window.pJSDom[0].pJS;
        const color = getComputedStyle(document.documentElement)
            .getPropertyValue('--text-primary').trim();

        // Обновляем цвет частиц
        pJS.particles.color.value = color;
        pJS.particles.line_linked.color = color;

        // Пересоздаем все частицы с новым цветом
        pJS.fn.particlesEmpty();
        pJS.fn.particlesCreate();
        pJS.fn.particlesDraw();
    }
} 