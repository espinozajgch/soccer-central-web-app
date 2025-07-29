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

    // Global variables for search functionality and pagination
    let allPlayers = [];
    let filteredPlayers = [];
    let currentPage = 1;
    const playersPerPage = 12;
    
    // Load saved search term from localStorage (global scope)
    const savedSearchTerm = localStorage.getItem('playerSearchTerm') || '';

    // Search functionality
    const searchInput = document.getElementById('player-search');
    const clearSearchBtn = document.getElementById('clear-search');
    const searchResultsCount = document.getElementById('search-results-count');

    // Only add search functionality if elements exist (main page)
    if (searchInput && clearSearchBtn && searchResultsCount) {
        // Set saved search term if exists
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

                currentPage = 1; // Reset to first page when filtering
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
            currentPage = 1; // Reset to first page when clearing search
            displayPlayers(allPlayers);
            updateSearchResultsInfo(allPlayers.length, allPlayers.length);
        }

        // Update search results info
        function updateSearchResultsInfo(filteredCount, totalCount) {
            const startIndex = (currentPage - 1) * playersPerPage + 1;
            const endIndex = Math.min(currentPage * playersPerPage, filteredCount);
            
            if (filteredCount === totalCount) {
                searchResultsCount.textContent = `Showing ${startIndex}-${endIndex} of ${totalCount} players`;
            } else {
                searchResultsCount.textContent = `Showing ${startIndex}-${endIndex} of ${filteredCount} filtered players (${totalCount} total)`;
            }
        }
    } // Close the if statement for search functionality

    // Display players function with pagination
    function displayPlayers(players) {
        const container = document.getElementById('players-container');
        const loadingContainer = document.getElementById('players-loading');
        const count = document.getElementById('players-count');

        // Hide loading, show container
        if (loadingContainer) loadingContainer.style.display = 'none';
        if (container) container.style.display = 'grid';

        if (!players || !players.length) {
            if (container) {
                container.innerHTML = `
                    <div class="no-players">
                        <p><i class="fas fa-users"></i> No players found</p>
                    </div>`;
            }
            return;
        }

        if (count) count.textContent = players.length;

        // Calculate pagination
        const totalPages = Math.ceil(players.length / playersPerPage);
        const startIndex = (currentPage - 1) * playersPerPage;
        const endIndex = startIndex + playersPerPage;
        const currentPlayers = players.slice(startIndex, endIndex);

        const cards = currentPlayers.map(p => {
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

        // Set the player cards in the grid container
        container.innerHTML = cards;

        // Handle pagination separately - create or update pagination element
        let paginationContainer = document.getElementById('pagination-container');
        if (!paginationContainer) {
            paginationContainer = document.createElement('div');
            paginationContainer.id = 'pagination-container';
            container.parentNode.insertBefore(paginationContainer, container.nextSibling);
        }

        // Add pagination controls
        if (totalPages > 1) {
            paginationContainer.innerHTML = `
                <div class="pagination">
                    <button class="pagination-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
                        <i class="fas fa-chevron-left"></i> Previous
                    </button>
                    <span class="pagination-info">Page ${currentPage} of ${totalPages}</span>
                    <button class="pagination-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
                        Next <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            `;
            paginationContainer.style.display = 'block';
        } else {
            paginationContainer.style.display = 'none';
        }
    }

    // Change page function for pagination (moved inside DOMContentLoaded scope)
    window.changePage = function(newPage) {
        const totalPages = Math.ceil(filteredPlayers.length / playersPerPage);
        
        if (newPage >= 1 && newPage <= totalPages) {
            currentPage = newPage;
            displayPlayers(filteredPlayers);
            
            // Update search results info if search elements exist
            const searchResultsCount = document.getElementById('search-results-count');
            if (searchResultsCount) {
                updateSearchResultsInfo(filteredPlayers.length, allPlayers.length);
            }
            
            // Scroll to top of players section
            const playersSection = document.querySelector('.players-section');
            if (playersSection) {
                playersSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    };

    // Cargar players - only if we're on the main page
    const playersContainer = document.getElementById('players-container');
    const playersLoading = document.getElementById('players-loading');
    const playerError = document.getElementById('player-error');
    
    if (playersContainer && playersLoading) {
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
            if (playersLoading) playersLoading.style.display = 'none';
            if (playerError) playerError.style.display = 'block';
        });
    }
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
