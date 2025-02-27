document.addEventListener('DOMContentLoaded', function() {
    particlesJS('particles-js', {
        "particles": {
            "number": {
                "value": 80,
                "density": {
                    "enable": true,
                    "value_area": 800
                }
            },
            "color": {
                "value": getComputedStyle(document.documentElement)
                         .getPropertyValue('--text-primary').trim()
            },
            "shape": {
                "type": "circle",
                "stroke": {
                    "width": 0,
                    "color": "#000000"
                }
            },
            "opacity": {
                "value": 0.1,
                "random": true,
                "anim": {
                    "enable": true,
                    "speed": 1,
                    "opacity_min": 0.05,
                    "sync": false
                }
            },
            "size": {
                "value": 3,
                "random": true,
                "anim": {
                    "enable": true,
                    "speed": 2,
                    "size_min": 0.3,
                    "sync": false
                }
            },
            "line_linked": {
                "enable": true,
                "distance": 150,
                "color": "#000000",
                "opacity": 0.1,
                "width": 1
            },
            "move": {
                "enable": true,
                "speed": 1,
                "direction": "none",
                "random": true,
                "straight": false,
                "out_mode": "out",
                "bounce": false,
                "attract": {
                    "enable": true,
                    "rotateX": 600,
                    "rotateY": 1200
                }
            }
        },
        "interactivity": {
            "detect_on": "canvas",
            "events": {
                "onhover": {
                    "enable": true,
                    "mode": "bubble"
                },
                "onclick": {
                    "enable": true,
                    "mode": "push"
                },
                "resize": true
            },
            "modes": {
                "grab": {
                    "distance": 400,
                    "line_linked": {
                        "opacity": 0.5
                    }
                },
                "bubble": {
                    "distance": 200,
                    "size": 6,
                    "duration": 0.3,
                    "opacity": 0.3,
                    "speed": 3
                },
                "repulse": {
                    "distance": 200,
                    "duration": 0.4
                },
                "push": {
                    "particles_nb": 4
                },
                "remove": {
                    "particles_nb": 2
                }
            }
        },
        "retina_detect": true
    });

    // Добавляем параллакс эффект
    document.addEventListener('mousemove', function(e) {
        const particles = document.getElementById('particles-js');
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        
        // Вычисляем смещение от центра
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        const deltaX = (mouseX - centerX) / centerX;
        const deltaY = (mouseY - centerY) / centerY;

        // Применяем трансформацию с небольшой задержкой
        requestAnimationFrame(() => {
            particles.style.transform = `translate(${deltaX * 20}px, ${deltaY * 20}px)`;
        });
    });

    // Добавляем эффект при скролле
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const particles = document.getElementById('particles-js');
        const st = window.pageYOffset || document.documentElement.scrollTop;
        const scrollDirection = st > lastScrollTop ? 'down' : 'up';
        
        // Изменяем скорость частиц в зависимости от направления скролла
        const pJS = window.pJSDom[0].pJS;
        if (pJS && pJS.particles && pJS.particles.move) {
            if (scrollDirection === 'down') {
                pJS.particles.move.speed = 3;
                pJS.particles.move.direction = 'bottom';
            } else {
                pJS.particles.move.speed = 3;
                pJS.particles.move.direction = 'top';
            }
        }
        
        lastScrollTop = st <= 0 ? 0 : st;
    });

    // Добавляем эффект волны при клике
    document.addEventListener('click', function(e) {
        const particles = document.getElementById('particles-js');
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        ripple.style.left = e.clientX + 'px';
        ripple.style.top = e.clientY + 'px';
        particles.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 1000);
    });
}); 