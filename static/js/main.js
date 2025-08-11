document.addEventListener('DOMContentLoaded', function () {
    // Auto-clear flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-messages .alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.classList.add('fade-out');
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Navbar smooth scroll
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

    // Scroll Navbar background
    const navbar = document.querySelector('.site-header');
    if (navbar) {
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            navbar.style.background = scrollTop > 100 ? 'rgba(26, 26, 26, 0.98)' : 'rgba(26, 26, 26, 0.95)';
            navbar.style.boxShadow = scrollTop > 100 ? '0 2px 20px rgba(0,0,0,0.3)' : 'none';
        });
    }

    // Search functionality
    const searchInput = document.getElementById('player-search');
    const clearSearchBtn = document.getElementById('clear-search');
    const searchResultsCount = document.getElementById('search-results-count');

    if (searchInput && clearSearchBtn && searchResultsCount) {
        let allPlayers = [];
        let filteredPlayers = [];

        const savedSearchTerm = localStorage.getItem('playerSearchTerm') || '';
        if (savedSearchTerm) {
            searchInput.value = savedSearchTerm;
            clearSearchBtn.style.display = 'block';
        }

        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase().trim();

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

            clearSearchBtn.style.display = searchTerm ? 'block' : 'none';
        });

        clearSearchBtn.addEventListener('click', function () {
            searchInput.value = '';
            localStorage.removeItem('playerSearchTerm');
            clearSearch();
            this.style.display = 'none';
        });

        function filterPlayers(searchTerm) {
            const container = document.getElementById('players-container');
            const loadingContainer = document.getElementById('players-loading');

            container.style.display = 'none';
            loadingContainer.style.display = 'block';
            loadingContainer.querySelector('p').textContent = 'Searching players...';

            setTimeout(() => {
                filteredPlayers = allPlayers.filter(player => {
                    const name = (player.displayName || `${player.name || ''} ${player.lastName || ''}`.trim()).toLowerCase();
                    const position = (player.position || '').toLowerCase();
                    const nationality = (player.nationality || '').toLowerCase();
                    const teamName = (player.teamInfo?.name || '').toLowerCase();

                    return name.includes(searchTerm) ||
                        position.includes(searchTerm) ||
                        nationality.includes(searchTerm) ||
                        teamName.includes(searchTerm);
                });

                displayPlayers(filteredPlayers);
                updateSearchResultsInfo(filteredPlayers.length, allPlayers.length);
            }, 150);
        }

        function clearSearch() {
            const loadingContainer = document.getElementById('players-loading');
            loadingContainer.querySelector('p').textContent = 'Loading players...';

            filteredPlayers = allPlayers;
            displayPlayers(allPlayers);
            updateSearchResultsInfo(allPlayers.length, allPlayers.length);
        }

        function updateSearchResultsInfo(filteredCount, totalCount) {
            if (filteredCount === totalCount) {
                searchResultsCount.textContent = `Showing all ${totalCount} players`;
            } else {
                searchResultsCount.textContent = `Showing ${filteredCount} of ${totalCount} players`;
            }
        }

        function displayPlayers(players) {
            const container = document.getElementById('players-container');
            const loadingContainer = document.getElementById('players-loading');
            const count = document.getElementById('players-count');

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
                const img = 'https://images.pexels.com/photos/274506/pexels-photo-274506.jpeg?auto=compress&cs=tinysrgb&w=400';
                const pos = p.position || p.role1?.join(', ') || 'N/A';
                const nationality = p.nationality || 'N/A';
                
                // Team information
                const teamName = p.teamInfo?.name || (p.teamId ? `Team ${p.teamId.slice(-4)}` : 'Unknown Team');
                const teamBadge = p.teamInfo?.badge || p.teamInfo?.logo || p.teamInfo?.crest || null;
                const teamId = p.teamId || 'N/A';

                return `
                <div class="player-card">
                    <img src="${img}" alt="${name}" class="player-photo" />
                    <div class="player-info">
                        <h3 class="player-name">${name}</h3>
                        <p class="player-position"><i class="fas fa-user-tag"></i> ${pos}</p>
                        <p><i class="fas fa-flag"></i> ${nationality}</p>
                        <div class="team-info">
                            ${teamBadge ? `<img src="${teamBadge}" alt="${teamName}" class="team-badge" />` : ''}
                            <span class="team-name"><i class="fas fa-users"></i> ${teamName}</span>
                            ${teamId !== 'N/A' ? `<small class="team-id">ID: ${teamId.slice(-6)}</small>` : ''}
                        </div>
                        <button onclick="viewPlayer('${p.id}')" class="btn-primary">
                            <i class="fas fa-eye"></i> View Profile
                        </button>
                    </div>
                </div>`;
            }).join('');

            container.innerHTML = cards;

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

        // Fetch players data and get team information
        fetch('/players')
            .then(res => res.json())
            .then(players => {
                allPlayers = players;
                filteredPlayers = players;

                if (!players || !players.length) {
                    displayPlayers([]);
                    return;
                }

                // Get unique team IDs from players
                const uniqueTeamIds = [...new Set(players.map(p => p.teamId).filter(id => id))];
                
                // First try to fetch all teams at once (more efficient)
                fetch('/teams')
                    .then(res => {
                        if (!res.ok) {
                            throw new Error(`HTTP ${res.status}`);
                        }
                        return res.json();
                    })
                    .then(allTeams => {
                        console.log('All teams data:', allTeams);
                        
                        // Create a map of team information from all teams
                        const teamsMap = {};
                        if (Array.isArray(allTeams)) {
                            allTeams.forEach(team => {
                                if (team._id) {
                                    teamsMap[team._id] = team;
                                }
                            });
                        }
                        
                        // Add team information to players
                        allPlayers = allPlayers.map(player => ({
                            ...player,
                            teamInfo: teamsMap[player.teamId] || { name: `Team ${player.teamId?.slice(-4) || 'Unknown'}` }
                        }));
                        filteredPlayers = allPlayers;

                        if (savedSearchTerm) {
                            filterPlayers(savedSearchTerm);
                        } else {
                            displayPlayers(allPlayers);
                            updateSearchResultsInfo(allPlayers.length, allPlayers.length);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching all teams, falling back to individual requests:', error);
                        
                        // Fallback: fetch team information for each unique team ID individually
                        const teamPromises = uniqueTeamIds.map(teamId => 
                            fetch(`/teams/${teamId}`)
                                .then(res => {
                                    if (!res.ok) {
                                        throw new Error(`HTTP ${res.status}`);
                                    }
                                    return res.json();
                                })
                                .then(team => {
                                    console.log(`Team data for ${teamId}:`, team);
                                    return { id: teamId, ...team };
                                })
                                .catch(error => {
                                    console.error(`Error fetching team ${teamId}:`, error);
                                    return { id: teamId, name: `Team ${teamId.slice(-4)}` };
                                })
                        );

                        Promise.all(teamPromises)
                            .then(teams => {
                                // Create a map of team information
                                const teamsMap = {};
                                teams.forEach(team => {
                                    teamsMap[team.id] = team;
                                });

                                // Add team information to players
                                allPlayers = allPlayers.map(player => ({
                                    ...player,
                                    teamInfo: teamsMap[player.teamId] || { name: `Team ${player.teamId?.slice(-4) || 'Unknown'}` }
                                }));
                                filteredPlayers = allPlayers;

                                if (savedSearchTerm) {
                                    filterPlayers(savedSearchTerm);
                                } else {
                                    displayPlayers(allPlayers);
                                    updateSearchResultsInfo(allPlayers.length, allPlayers.length);
                                }
                            })
                            .catch(err => {
                                console.error('Error loading team data:', err);
                                // Fallback: display players without team info
                                if (savedSearchTerm) {
                                    filterPlayers(savedSearchTerm);
                                } else {
                                    displayPlayers(allPlayers);
                                    updateSearchResultsInfo(allPlayers.length, allPlayers.length);
                                }
                            });
                    });
            })
            .catch(err => {
                console.error('Error loading players:', err);
                const loading = document.getElementById('players-loading');
                const error = document.getElementById('player-error');
                if (loading) loading.style.display = 'none';
                if (error) error.style.display = 'block';
            });
    }
});

// Calcular edad
function calculateAge(dateString) {
    const birth = new Date(dateString);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
    return age;
}

// Navegar a detalle de jugador
function viewPlayer(playerId) {
    window.location.href = `/player?id=${playerId}`;
}
