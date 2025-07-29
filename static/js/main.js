document.addEventListener('DOMContentLoaded', function () {
    // Navbar 
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Scroll 
    const navbar = document.querySelector('.site-header');
    if (navbar) {
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            navbar.style.background = scrollTop > 100 ? 'rgba(255,255,255,0.98)' : 'rgba(255,255,255,0.95)';
            navbar.style.boxShadow = scrollTop > 100 ? '0 2px 20px rgba(0,0,0,0.1)' : 'none';
        });
    }

    // Cargar players
    fetch('/players')
        .then(res => res.json()) // Convierte la respuesta en JSON
        .then(players => { // `players` es un array de objetos jugador
            const container = document.getElementById('players-container');
            const count = document.getElementById('players-count'); //cuenta los elementos del array,cada elemento 3460 lineas aproxx

            if (!players || !players.length) {
                container.innerHTML = `
                    <div class="no-players">
                        <p><i class="fas fa-users"></i> No players available</p>
                    </div>`;
                return;
            }

            count.textContent = players.length;

            const cards = players.map(p => {
                const name = p.displayName || `${p.name || ''} ${p.lastName || ''}`.trim();
                const img =  'https://images.pexels.com/photos/274506/pexels-photo-274506.jpeg?auto=compress&cs=tinysrgb&w=400';
                const pos = p.position || p.role1?.join(', ') || 'N/A';
                const age = p.birthDateText
                const birthPlace = p.birthPlace
                const nationality = p.nationality || 'N/A';

                return `
                <div class="player-card">
                    <img src="${img}" alt="${name}" class="player-photo" />
                    <div class="player-info">
                        <h3 class="player-name">${name}</h3>
                        <p class="player-position"><i class="fas fa-user-tag"></i> ${pos}</p>
                        <p><i class="fas fa-flag"></i> ${nationality}</p>
                        <button onclick="viewPlayer('${p.id}')" class="btn-primary">
                            <i class="fas fa-eye"></i> View Profile
                        </button>
                    </div>
                </div>
                `;
            }).join('');

            container.innerHTML = cards;

            // animacion de tarjetas
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            document.querySelectorAll('.player-card, .feature').forEach((el, i) => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(30px)';
                el.style.transition = `opacity 0.6s ease ${i * 0.1}s, transform 0.6s ease ${i * 0.1}s`;
                observer.observe(el);
            });

        })
        .catch(err => {
            console.error('Error loading players:', err);
            document.getElementById('player-error').style.display = 'block';
        });
});

// Calcular edad con date
function calculateAge(dateString) {
    const birth = new Date(dateString);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
    return age;
}

// Detalle del jugador
function viewPlayer(playerId) {
    alert(`Viewing player with ID: ${playerId}`);
}
