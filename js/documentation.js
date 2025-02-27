document.addEventListener('DOMContentLoaded', function() {
    // Получаем все секции и ссылки навигации
    const sections = document.querySelectorAll('.content section');
    const navLinks = document.querySelectorAll('.doc-navigation a');

    // Функция для определения активного раздела
    function setActiveSection() {
        let currentSection = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 100) {
                currentSection = section.getAttribute('id');
            }
        });

        // Обновляем активную ссылку
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').substring(1) === currentSection) {
                link.classList.add('active');
            }
        });
    }

    // Слушаем событие скролла
    window.addEventListener('scroll', setActiveSection);
    
    // Устанавливаем начальное состояние
    setActiveSection();
}); 