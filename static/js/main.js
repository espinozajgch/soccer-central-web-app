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
            navbar.style.background = scrollTop > 100 ? 'rgba(26, 26, 26, 0.98)' : 'rgba(26, 26, 26, 0.95)';
            navbar.style.boxShadow = scrollTop > 100 ? '0 2px 20px rgba(0,0,0,0.3)' : 'none';
        });
    }

    // Global variables for search functionality
    let allPlayers = [];
    let filteredPlayers = [];

    // Search functionality
    const searchInput = document.getElementById('player-search');
    const clearSearchBtn = document.getElementById('clear-search');
    const searchResultsCount = document.getElementById('search-results-count');

    // Load saved search term from localStorage
    const savedSearchTerm = localStorage.getItem('playerSearchTerm') || '';
    if (savedSearchTerm) {
        searchInput.value = savedSearchTerm;
        clearSearchBtn.style.display = 'block';
    }

    // Search input event listener
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        
        // Save search term to localStorage
        if (searchTerm) {
            localStorage.setItem('playerSearchTerm', searchTerm);
        } else {
            localStorage.removeItem('playerSearchTerm');
        }
        
        if (searchTerm === '') {
            clearSearch();
        } else {
            filterPlayers(searchTerm);
        }
        
        // Show/hide clear button
        clearSearchBtn.style.display = searchTerm ? 'block' : 'none';
    });

    // Clear search button event listener
    clearSearchBtn.addEventListener('click', function() {
        searchInput.value = '';
        localStorage.removeItem('playerSearchTerm');
        clearSearch();
        this.style.display = 'none';
    });

    // Filter players function
    function filterPlayers(searchTerm) {
        // Show brief loading state for search
        const container = document.getElementById('players-container');
        const loadingContainer = document.getElementById('players-loading');
        
        container.style.display = 'none';
        loadingContainer.style.display = 'block';
        loadingContainer.querySelector('p').textContent = 'Searching players...';
        
        // Small delay to show loading state
        setTimeout(() => {
            filteredPlayers = allPlayers.filter(player => {
                const name = (player.displayName || `${player.name || ''} ${player.lastName || ''}`.trim()).toLowerCase();
                const position = (player.position || '').toLowerCase();
                const nationality = (player.nationality || '').toLowerCase();
                
                return name.includes(searchTerm) || 
                       position.includes(searchTerm) || 
                       nationality.includes(searchTerm);
            });
            
            displayPlayers(filteredPlayers);
            updateSearchResultsInfo(filteredPlayers.length, allPlayers.length);
        }, 150);
    }

    // Clear search function
    function clearSearch() {
        // Reset loading text
        const loadingContainer = document.getElementById('players-loading');
        loadingContainer.querySelector('p').textContent = 'Loading players...';
        
        filteredPlayers = allPlayers;
        displayPlayers(allPlayers);
        updateSearchResultsInfo(allPlayers.length, allPlayers.length);
    }

    // Update search results info
    function updateSearchResultsInfo(filteredCount, totalCount) {
        if (filteredCount === totalCount) {
            searchResultsCount.textContent = `Showing all ${totalCount} players`;
        } else {
            searchResultsCount.textContent = `Showing ${filteredCount} of ${totalCount} players`;
        }
    }

    // Display players function
    function displayPlayers(players) {
        const container = document.getElementById('players-container');
        const loadingContainer = document.getElementById('players-loading');
        const count = document.getElementById('players-count');

        // Hide loading, show container
        loadingContainer.style.display = 'none';
        container.style.display = 'grid';

        if (!players || !players.length) {
            container.innerHTML = `
                <div class="no-players">
                    <p><i class="fas fa-users"></i> No players found</p>
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

        // Animate cards
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
    }

    // Cargar players
    fetch('/players')
        .then(res => res.json()) // Convierte la respuesta en JSON
        .then(players => { // `players` es un array de objetos jugador
            allPlayers = players;
            filteredPlayers = players;
            
            if (!players || !players.length) {
                displayPlayers([]);
                return;
            }

            // Apply saved search filter if exists
            if (savedSearchTerm) {
                filterPlayers(savedSearchTerm);
            } else {
                displayPlayers(players);
                updateSearchResultsInfo(players.length, players.length);
            }

        })
        .catch(err => {
            console.error('Error loading players:', err);
            document.getElementById('players-loading').style.display = 'none';
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

// Detalle del jugador - navegar a la página de detalles
function viewPlayer(playerId) {
    window.location.href = `/player?id=${playerId}`;
}
