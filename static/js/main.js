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
            container.style.display = 'block';

            if (!players || !players.length) {
                container.innerHTML = `
                    <div class="no-players">
                        <p><i class="fas fa-users"></i> No players found</p>
                    </div>`;
                return;
            }

            count.textContent = players.length;

            // Group players by team
            const teamsMap = {};
            players.forEach(p => {
                const teamName = p.teamInfo?.name || (p.teamId ? `Team ${p.teamId.slice(-4)}` : 'Unknown Team');
                if (!teamsMap[teamName]) {
                    teamsMap[teamName] = [];
                }
                teamsMap[teamName].push(p);
            });

            // Create accordion structure
            const accordionHTML = Object.entries(teamsMap).map(([teamName, teamPlayers], teamIndex) => {
                const teamId = `team-${teamIndex}`;
                const playerCards = teamPlayers.map(p => {
                    const name = p.displayName || `${p.name || ''} ${p.lastName || ''}`.trim();
                    const img = 'https://images.pexels.com/photos/274506/pexels-photo-274506.jpeg?auto=compress&cs=tinysrgb&w=400';
                    const pos = p.position || p.role1?.join(', ') || 'N/A';
                    const nationality = p.nationality || 'N/A';
                    const teamBadge = p.teamInfo?.badge || p.teamInfo?.logo || p.teamInfo?.crest || null;

                    return `
                    <div class="player-card">
                        <img src="${img}" alt="${name}" class="player-photo" />
                        <div class="player-info">
                            <h3 class="player-name">${name}</h3>
                            <div class="player-details-row">
                                <span class="player-position"><i class="fas fa-user-tag"></i> ${pos}</span>
                                <span class="player-nationality"><i class="fas fa-flag"></i> ${nationality}</span>
                                <span class="player-jersey-card"><i class="fas fa-tshirt"></i> ${p.jersey ? `#${p.jersey}` : 'N/A'}</span>
                            </div>
                            <button onclick="viewPlayer('${p.id}')" class="btn-primary">
                                <i class="fas fa-eye"></i> View Profile
                            </button>
                        </div>
                    </div>`;
                }).join('');

                return `
                <div class="team-accordion">
                    <div class="team-header" onclick="toggleTeam('${teamId}')">
                        <div class="team-header-content">
                            <div class="team-info-header">
                                ${teamPlayers[0]?.teamInfo?.badge ? `<img src="${teamPlayers[0].teamInfo.badge}" alt="${teamName}" class="team-badge-header" />` : ''}
                                <span class="team-name-header">${teamName}</span>
                            </div>
                            <div class="team-stats">
                                <span class="player-count">${teamPlayers.length} player${teamPlayers.length !== 1 ? 's' : ''}</span>
                                <i class="fas fa-chevron-down accordion-icon" id="icon-${teamId}"></i>
                            </div>
                        </div>
                    </div>
                    <div class="team-content" id="${teamId}">
                        <div class="players-grid">
                            ${playerCards}
                        </div>
                    </div>
                </div>`;
            }).join('');

            container.innerHTML = accordionHTML;
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

function toggleTeam(teamId) {
    const teamContent = document.getElementById(teamId);
    const icon = document.getElementById(`icon-${teamId}`);
    
    if (teamContent.style.display === 'none' || teamContent.style.display === '') {
        teamContent.style.display = 'block';
        icon.style.transform = 'rotate(180deg)';
        teamContent.style.opacity = '1';
        teamContent.style.maxHeight = teamContent.scrollHeight + 'px';
    } else {
        teamContent.style.display = 'none';
        icon.style.transform = 'rotate(0deg)';
        teamContent.style.opacity = '0';
        teamContent.style.maxHeight = '0';
    }
}
