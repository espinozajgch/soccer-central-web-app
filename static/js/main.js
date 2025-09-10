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
                            <button onclick="viewPlayer('${p.id || p._id}')" class="btn-primary">
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

        // FUNCIÓN CORREGIDA: Cargar jugadores con cache
        async function loadPlayers() {
            try {
                console.log('[DEBUG] Starting to load players...');
                
                // Verificar si hay datos cacheados del login
                const cachedPlayersData = localStorage.getItem('playersData');
                const cachedTimestamp = localStorage.getItem('playersDataTimestamp');
                const currentTime = Date.now();
                const fiveMinutesInMs = 5 * 60 * 1000; // 5 minutos

                // VALIDACIÓN MEJORADA: Verificar que los datos sean válidos
                if (cachedPlayersData && 
                    cachedTimestamp && 
                    cachedPlayersData !== 'undefined' && 
                    cachedPlayersData !== 'null' && 
                    cachedPlayersData.length > 10) { // Al menos debe tener más de 10 caracteres para ser JSON válido
                    
                    const dataAge = currentTime - parseInt(cachedTimestamp);
                    
                    if (dataAge < fiveMinutesInMs && !isNaN(parseInt(cachedTimestamp))) {
                        try {
                            console.log('[DEBUG] Attempting to use cached players data from login');
                            const playersData = JSON.parse(cachedPlayersData);
                            
                            // Verificar que los datos parseados sean válidos
                            if (Array.isArray(playersData) && playersData.length > 0) {
                                console.log('[DEBUG] Successfully using cached players data from login');
                                
                                // Usar los datos cacheados
                                allPlayers = playersData;
                                filteredPlayers = [...allPlayers];
                                
                                console.log(`[DEBUG] Loaded ${allPlayers.length} players from cache`);
                                
                                // Continuar con la lógica de equipos usando datos cacheados
                                await loadTeamInfoForPlayers();
                                return; // Salir sin hacer llamada a API
                            } else {
                                console.log('[DEBUG] Cached data is not a valid array, fetching fresh data');
                            }
                        } catch (parseError) {
                            console.warn('[DEBUG] Error parsing cached data:', parseError);
                            // Limpiar datos corruptos
                            localStorage.removeItem('playersData');
                            localStorage.removeItem('playersDataTimestamp');
                        }
                    } else {
                        console.log('[DEBUG] Cached data is too old, fetching fresh data');
                        // Limpiar datos antiguos
                        localStorage.removeItem('playersData');
                        localStorage.removeItem('playersDataTimestamp');
                    }
                } else {
                    console.log('[DEBUG] No valid cached data found');
                    // Limpiar datos inválidos si existen
                    if (cachedPlayersData) {
                        localStorage.removeItem('playersData');
                        localStorage.removeItem('playersDataTimestamp');
                    }
                }

                // Si no hay datos cacheados válidos, hacer llamada a API
                console.log('[DEBUG] Fetching fresh players data from API');
                
                const response = await fetch('/api/players');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                const playersArray = data.users || data || [];
                
                // Validar que recibimos datos válidos
                if (!Array.isArray(playersArray)) {
                    throw new Error('API response is not an array');
                }
                
                allPlayers = playersArray;
                filteredPlayers = [...allPlayers];
                
                // Guardar datos frescos en cache SOLO si son válidos
                if (allPlayers.length > 0) {
                    try {
                        localStorage.setItem('playersData', JSON.stringify(allPlayers));
                        localStorage.setItem('playersDataTimestamp', Date.now().toString());
                        console.log(`[DEBUG] Cached ${allPlayers.length} players to localStorage`);
                    } catch (storageError) {
                        console.warn('[DEBUG] Could not cache players data:', storageError);
                    }
                }
                
                console.log(`[DEBUG] Loaded ${allPlayers.length} players from API`);
                
                // Continuar con la lógica de equipos
                await loadTeamInfoForPlayers();
                
            } catch (error) {
                console.error('[ERROR] Error loading players:', error);
                
                // Mostrar error en la UI
                const loadingContainer = document.getElementById('players-loading');
                const errorContainer = document.getElementById('player-error');
                const container = document.getElementById('players-container');
                
                if (loadingContainer) loadingContainer.style.display = 'none';
                if (errorContainer) {
                    errorContainer.style.display = 'block';
                    errorContainer.querySelector('p').textContent = `Error loading players: ${error.message}`;
                }
                if (container) container.style.display = 'none';
                
                // Intentar usar datos cacheados aunque sean antiguos como último recurso
                const fallbackData = localStorage.getItem('playersData');
                if (fallbackData && 
                    fallbackData !== 'undefined' && 
                    fallbackData !== 'null' && 
                    fallbackData.length > 10) {
                    
                    try {
                        console.log('[DEBUG] Attempting to use old cached data as fallback');
                        const parsedFallback = JSON.parse(fallbackData);
                        
                        if (Array.isArray(parsedFallback) && parsedFallback.length > 0) {
                            allPlayers = parsedFallback;
                            filteredPlayers = [...allPlayers];
                            
                            await loadTeamInfoForPlayers();
                            
                            if (errorContainer) {
                                errorContainer.innerHTML = '<p><i class="fas fa-exclamation-triangle"></i> Using cached data (connection error)</p>';
                            }
                            
                            console.log('[DEBUG] Successfully used fallback cached data');
                        }
                    } catch (fallbackError) {
                        console.error('[DEBUG] Error using fallback data:', fallbackError);
                        // Limpiar datos corruptos
                        localStorage.removeItem('playersData');
                        localStorage.removeItem('playersDataTimestamp');
                    }
                }
            }
        }


        // NUEVA FUNCIÓN: Cargar información de equipos
        async function loadTeamInfoForPlayers() {
            if (!allPlayers || !allPlayers.length) {
                displayPlayers([]);
                return;
            }

            // Get unique team IDs from players
            const uniqueTeamIds = [...new Set(allPlayers.map(p => p.teamId).filter(id => id))];
            
            try {
                // First try to fetch all teams at once (more efficient)
                const teamsResponse = await fetch('/teams');
                if (!teamsResponse.ok) {
                    throw new Error(`HTTP ${teamsResponse.status}`);
                }
                
                const allTeams = await teamsResponse.json();
                console.log('[DEBUG] All teams data:', allTeams);
                
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
                filteredPlayers = [...allPlayers];

                // Display players
                if (savedSearchTerm) {
                    filterPlayers(savedSearchTerm);
                } else {
                    displayPlayers(allPlayers);
                    updateSearchResultsInfo(allPlayers.length, allPlayers.length);
                }

            } catch (error) {
                console.error('[DEBUG] Error fetching all teams, falling back to individual requests:', error);
                
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
                            console.log(`[DEBUG] Team data for ${teamId}:`, team);
                            return { id: teamId, ...team };
                        })
                        .catch(error => {
                            console.error(`[DEBUG] Error fetching team ${teamId}:`, error);
                            return { id: teamId, name: `Team ${teamId.slice(-4)}` };
                        })
                );

                try {
                    const teams = await Promise.all(teamPromises);
                    
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
                    filteredPlayers = [...allPlayers];

                    // Display players
                    if (savedSearchTerm) {
                        filterPlayers(savedSearchTerm);
                    } else {
                        displayPlayers(allPlayers);
                        updateSearchResultsInfo(allPlayers.length, allPlayers.length);
                    }
                    
                } catch (err) {
                    console.error('[DEBUG] Error loading team data:', err);
                    // Fallback: display players without team info
                    if (savedSearchTerm) {
                        filterPlayers(savedSearchTerm);
                    } else {
                        displayPlayers(allPlayers);
                        updateSearchResultsInfo(allPlayers.length, allPlayers.length);
                    }
                }
            }
        }

        // LLAMAR A LA NUEVA FUNCIÓN EN LUGAR DE FETCH DIRECTO
        loadPlayers().catch(err => {
            console.error('Error in loadPlayers:', err);
            const loading = document.getElementById('players-loading');
            const error = document.getElementById('player-error');
            if (loading) loading.style.display = 'none';
            if (error) error.style.display = 'block';
        });
    }

    // ===============================
    // INICIALIZAR PDF FUNCTIONALITY
    // ===============================
    // Setup download button when page loads
    setupDownloadButton();
});

// Resto de tus funciones sin cambios...
function calculateAge(dateString) {
    const birth = new Date(dateString);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
    return age;
}

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

// ... resto de tus funciones PDF sin cambios ...

window.__charts = window.__charts || [];

function buildReportFileName() {
    const name = (document.getElementById('player-name')?.textContent || 'player')
        .trim().replace(/[^a-zA-Z0-9]/g, '_');
    const dt = new Date();
    const stamp = `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`;
    return `${name}_report_${stamp}.pdf`;
}

function getAllChartCanvases() {
    return Array.from(document.querySelectorAll('.athletic-performance-grid canvas, .chart-container canvas'));
}

function findChartInstanceByCanvas(canvas) {
    // Buscar instancia de Chart.js por canvas
    if (window.Chart && Chart.getChart) {
        const chart = Chart.getChart(canvas);
        if (chart) return chart;
    }

    // Buscar en el array global si existe
    if (window.__charts && Array.isArray(window.__charts)) {
        const found = window.__charts.find(ch => 
            ch?.canvas === canvas || ch?.ctx?.canvas === canvas);
        if (found) return found;
    }

    // Fallback para versiones antiguas
    if (window.Chart && window.Chart.instances) {
        for (let id in window.Chart.instances) {
            const chart = window.Chart.instances[id];
            if (chart.chart && chart.chart.canvas === canvas) {
                return chart;
            }
        }
    }
    return null;
}

function replaceChartsWithImages() {
    const canvases = getAllChartCanvases();
    const replacements = [];

    console.log(`[PDF] Found ${canvases.length} canvases to convert`);

    canvases.forEach((canvas, index) => {
        let dataUrl = null;
        const chart = findChartInstanceByCanvas(canvas);
        
        try {
            if (chart && typeof chart.toBase64Image === 'function') {
                dataUrl = chart.toBase64Image('image/png', 1.0);
                console.log(`[PDF] Canvas ${index + 1}: Using Chart.js toBase64Image`);
            } else if (canvas.toDataURL) {
                dataUrl = canvas.toDataURL('image/png', 1.0);
                console.log(`[PDF] Canvas ${index + 1}: Using canvas toDataURL`);
            }
        } catch (e) {
            console.warn(`[PDF] Error converting canvas ${index + 1}:`, e);
            try {
                if (canvas.toDataURL) {
                    dataUrl = canvas.toDataURL('image/png', 0.9);
                    console.log(`[PDF] Canvas ${index + 1}: Using fallback toDataURL`);
                }
            } catch (e2) {
                console.error(`[PDF] Failed to convert canvas ${index + 1}:`, e2);
            }
        }

        if (dataUrl && dataUrl.length > 100) {
            const img = new Image();
            img.src = dataUrl;
            img.style.cssText = canvas.style.cssText;
            img.style.width = canvas.offsetWidth + 'px';
            img.style.height = canvas.offsetHeight + 'px';
            img.style.display = 'block';
            
            const parent = canvas.parentNode;
            if (parent) {
                parent.replaceChild(img, canvas);
                replacements.push({ parent, img, canvas });
                console.log(`[PDF] Canvas ${index + 1}: Successfully replaced with image`);
            }
        } else {
            console.warn(`[PDF] Canvas ${index + 1}: Failed to generate valid data URL`);
        }
    });

    console.log(`[PDF] Successfully replaced ${replacements.length} canvases with images`);

    // Retornar función de restauración
    return function restore() {
        replacements.forEach(({ parent, img, canvas }, index) => {
            try {
                if (parent && img && canvas && parent.contains(img)) {
                    parent.replaceChild(canvas, img);
                }
            } catch (e) {
                console.warn(`[PDF] Error restoring canvas ${index + 1}:`, e);
            }
        });
        console.log(`[PDF] Restored ${replacements.length} canvases`);
    };
}

function waitForChartsReady(timeoutMs = 3000) {
    return new Promise(resolve => {
        setTimeout(resolve, timeoutMs);
    });
}

// Función para limpiar datos de Chart.js antes de conversión
function cleanChartData() {
    if (window.Chart && window.Chart.instances) {
        Object.keys(window.Chart.instances).forEach(key => {
            const chart = window.Chart.instances[key];
            if (chart && chart.data && chart.data.datasets) {
                chart.data.datasets.forEach(dataset => {
                    if (dataset.data) {
                        dataset.data = dataset.data.map(value => {
                            if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) {
                                return 0;
                            }
                            return value;
                        });
                    }
                });
                chart.update('none');
            }
        });
    }
    
    if (window.__charts && Array.isArray(window.__charts)) {
        window.__charts.forEach(chart => {
            if (chart && chart.data && chart.data.datasets) {
                chart.data.datasets.forEach(dataset => {
                    if (dataset.data) {
                        dataset.data = dataset.data.map(value => {
                            if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) {
                                return 0;
                            }
                            return value;
                        });
                    }
                });
                chart.update('none');
            }
        });
    }
}

async function exportElementToPDF(element, filename) {
    // Opción A: html2pdf.js (descarga directa)
    if (window.html2pdf) {
        const opt = {
            margin: 10,
            filename: filename,
            image: { type: 'png', quality: 1.0 },
            html2canvas: { 
                scale: 2,
                useCORS: true,
                backgroundColor: '#ffffff',
                logging: false,
                height: element.scrollHeight,
                width: element.scrollWidth,
                allowTaint: true,
                foreignObjectRendering: false
            },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        await window.html2pdf().from(element).set(opt).save();
        console.log('[PDF] Generated using html2pdf');
        return;
    }

    // Opción B: jsPDF + html2canvas
    if (window.jsPDF && window.html2canvas) {
        const { jsPDF } = window.jsPDF;
        
        const canvas = await window.html2canvas(element, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff',
            logging: false,
            height: element.scrollHeight,
            width: element.scrollWidth,
            allowTaint: true
        });

        const imgData = canvas.toDataURL('image/png', 1.0);
        const pdf = new jsPDF('p', 'mm', 'a4');
        
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 10;
        
        const imgWidth = pageWidth - (margin * 2);
        const imgHeight = (imgWidth / canvas.width) * canvas.height;

        if (imgHeight <= pageHeight - (margin * 2)) {
            pdf.addImage(imgData, 'PNG', margin, margin, imgWidth, imgHeight);
        } else {
            // Múltiples páginas
            let remaining = imgHeight;
            let srcY = 0;
            const ratio = canvas.width / imgWidth;
            
            while (remaining > 0) {
                const pageCanvasHeight = (pageHeight - (margin * 2)) * ratio;
                const sliceHeight = Math.min(remaining * ratio, pageCanvasHeight);
                
                const pageCanvas = document.createElement('canvas');
                pageCanvas.width = canvas.width;
                pageCanvas.height = sliceHeight;
                
                const ctx = pageCanvas.getContext('2d');
                ctx.drawImage(canvas, 0, srcY, canvas.width, sliceHeight, 0, 0, canvas.width, sliceHeight);
                
                const pageImgData = pageCanvas.toDataURL('image/png', 1.0);
                const drawHeight = sliceHeight / ratio;
                
                if (srcY > 0) pdf.addPage();
                pdf.addImage(pageImgData, 'PNG', margin, margin, imgWidth, drawHeight);
                
                remaining -= drawHeight;
                srcY += sliceHeight;
            }
        }

        pdf.save(filename);
        console.log('[PDF] Generated using jsPDF + html2canvas');
        return;
    }

    // Fallback
    console.warn('[PDF] Libraries not available, falling back to print dialog');
    window.print();
}

function setupDownloadButton() {
    const downloadBtn = document.getElementById('download-report-btn');
    if (!downloadBtn) return;
    
    downloadBtn.addEventListener('click', async function () {
        // Obtener el ID del jugador para abrir el reporte en nueva pestaña
        const urlParams = new URLSearchParams(window.location.search);
        const playerId = urlParams.get('id');
        
        if (playerId) {
            // Abrir directamente la página de reporte en nueva pestaña
            window.open(`/player-report/${playerId}`, '_blank');
        } else {
            alert('No se pudo obtener el ID del jugador');
        }
    });
}

// Función simplificada que genera PDF directamente
async function generatePDFDirectly(element) {
    // Ocultar elementos que no deben aparecer en el PDF (pero NO el botón)
    const elementsToHide = [
        document.querySelector('.site-header'),
        document.querySelector('.site-footer'),
        document.querySelector('.back-button-container')
        // NO ocultar .player-actions para mantener el botón visible
    ].filter(el => el); // Filtrar elementos que realmente existen
    
    // Guardar estados originales
    const originalStates = elementsToHide.map(el => ({
        element: el,
        display: el.style.display
    }));
    
    // Ocultar elementos temporalmente
    elementsToHide.forEach(el => {
        el.style.display = 'none';
    });
    
    // Esperar un momento
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    try {
        const filename = buildReportFileName();
        
        // Intentar con html2pdf primero
        if (window.html2pdf) {
            const opt = {
                margin: [10, 10, 10, 10],
                filename: filename,
                image: { type: 'jpeg', quality: 0.95 },
                html2canvas: { 
                    scale: 1,
                    useCORS: true,
                    backgroundColor: '#ffffff',
                    logging: true,
                    letterRendering: true,
                    allowTaint: true,
                    scrollX: 0,
                    scrollY: -window.scrollY,
                    width: element.scrollWidth,
                    height: element.scrollHeight
                },
                jsPDF: { 
                    unit: 'mm', 
                    format: 'a4', 
                    orientation: 'portrait'
                },
                pagebreak: { 
                    mode: ['avoid-all', 'css'],
                    avoid: ['img', '.chart-container']
                }
            };
            
            await window.html2pdf().from(element).set(opt).save();
            console.log('[PDF] Successfully generated with html2pdf');
        }
        // Fallback con jsPDF + html2canvas
        else if (window.jsPDF && window.html2canvas) {
            const { jsPDF } = window.jsPDF;
            
            const canvas = await window.html2canvas(element, {
                scale: 1,
                useCORS: true,
                backgroundColor: '#ffffff',
                logging: true,
                letterRendering: true,
                allowTaint: true,
                scrollX: 0,
                scrollY: -window.scrollY,
                width: element.scrollWidth,
                height: element.scrollHeight
            });
            
            const imgData = canvas.toDataURL('image/jpeg', 0.95);
            const pdf = new jsPDF('p', 'mm', 'a4');
            
            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();
            const margin = 10;
            
            const imgWidth = pageWidth - (margin * 2);
            const imgHeight = (imgWidth / canvas.width) * canvas.height;
            
            if (imgHeight <= pageHeight - (margin * 2)) {
                pdf.addImage(imgData, 'JPEG', margin, margin, imgWidth, imgHeight);
            } else {
                // Múltiples páginas
                let remaining = imgHeight;
                let srcY = 0;
                const ratio = canvas.width / imgWidth;
                
                while (remaining > 0) {
                    const pageCanvasHeight = (pageHeight - (margin * 2)) * ratio;
                    const sliceHeight = Math.min(remaining * ratio, pageCanvasHeight);
                    
                    const pageCanvas = document.createElement('canvas');
                    pageCanvas.width = canvas.width;
                    pageCanvas.height = sliceHeight;
                    
                    const ctx = pageCanvas.getContext('2d');
                    ctx.fillStyle = '#ffffff';
                    ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height);
                    ctx.drawImage(canvas, 0, srcY, canvas.width, sliceHeight, 0, 0, canvas.width, sliceHeight);
                    
                    const pageImgData = pageCanvas.toDataURL('image/jpeg', 0.95);
                    const drawHeight = sliceHeight / ratio;
                    
                    if (srcY > 0) pdf.addPage();
                    pdf.addImage(pageImgData, 'JPEG', margin, margin, imgWidth, drawHeight);
                    
                    remaining -= drawHeight;
                    srcY += sliceHeight;
                }
            }
            
            pdf.save(filename);
            console.log('[PDF] Successfully generated with jsPDF + html2canvas');
        } else {
            throw new Error('No PDF libraries available');
        }
        
    } finally {
        // Restaurar elementos ocultos
        originalStates.forEach(({ element, display }) => {
            element.style.display = display;
        });
    }
}

function buildReportFileName() {
    let name = 'player_report';
    
    // Intentar obtener el nombre del jugador
    const playerNameElement = document.getElementById('player-name');
    if (playerNameElement && playerNameElement.textContent) {
        name = playerNameElement.textContent
            .trim()
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '_')
            .replace(/_+/g, '_');
    }
    
    const dt = new Date();
    const stamp = `${dt.getFullYear()}${String(dt.getMonth()+1).padStart(2,'0')}${String(dt.getDate()).padStart(2,'0')}`;
    
    return `${name}_report_${stamp}.pdf`;
}
