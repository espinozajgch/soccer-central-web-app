// login.js
class AuthenticationService {
    constructor() {
        this.playersEndpoint = '/api/players';
        this.usersData = null;
    }

    async fetchAllUsers() {
        try {
            console.log('[DEBUG] Fetching players from iterpro API:', this.playersEndpoint);
            
            const response = await fetch(this.playersEndpoint, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('[DEBUG] API Response structure:', {
                has_users: !!data.users,
                users_count: data.users ? data.users.length : 0,
                total_users: data.total_users,
                first_user_sample: data.users && data.users.length > 0 ? Object.keys(data.users[0]) : []
            });
            
            this.usersData = data.users || [];
            
            if (this.usersData.length === 0) {
                throw new Error('No se encontraron jugadores en la API');
            }
            
            console.log('[DEBUG] Players loaded from iterpro:', this.usersData.length);
            console.log('[DEBUG] Sample player fields:', this.usersData.length > 0 ? Object.keys(this.usersData[0]) : []);
            
            return this.usersData;
        } catch (error) {
            console.error('[ERROR] Error fetching players from iterpro:', error);
            throw error;
        }
    }

    extractNameFromEmail(email) {
        const emailRegex = /^([^@]+)@soccercentralsa\.com$/i;
        const match = email.match(emailRegex);
        
        if (!match) {
            throw new Error('El formato del email debe ser: nombre@soccercentralsa.com');
        }
        
        return match[1].toLowerCase().trim();
    }

    findPlayerByName(name) {
        if (!this.usersData || !Array.isArray(this.usersData)) {
            throw new Error('Datos de jugadores no disponibles');
        }

        console.log('[DEBUG] Searching for player with name:', name);
        console.log('[DEBUG] Available players sample:', this.usersData.slice(0, 3).map(p => ({
            _id: p._id,
            name: p.name,
            displayName: p.displayName,
            firstName: p.firstName,
            lastName: p.lastName
        })));

        let foundPlayer = null;

        // 1. Buscar por displayName exacto
        foundPlayer = this.usersData.find(player => 
            player.displayName && player.displayName.toLowerCase() === name
        );

        if (foundPlayer) {
            console.log('[DEBUG] Found player by displayName:', foundPlayer.displayName);
            return foundPlayer;
        }

        // 2. Buscar por name exacto
        foundPlayer = this.usersData.find(player => 
            player.name && player.name.toLowerCase() === name
        );

        if (foundPlayer) {
            console.log('[DEBUG] Found player by name:', foundPlayer.name);
            return foundPlayer;
        }

        // 3. Buscar por firstName exacto
        foundPlayer = this.usersData.find(player => 
            player.firstName && player.firstName.toLowerCase() === name
        );

        if (foundPlayer) {
            console.log('[DEBUG] Found player by firstName:', foundPlayer.firstName);
            return foundPlayer;
        }

        // 4. Buscar por lastName exacto
        foundPlayer = this.usersData.find(player => 
            player.lastName && player.lastName.toLowerCase() === name
        );

        if (foundPlayer) {
            console.log('[DEBUG] Found player by lastName:', foundPlayer.lastName);
            return foundPlayer;
        }

        // 5. Buscar coincidencias parciales en cualquier campo de nombre
        foundPlayer = this.usersData.find(player => {
            const searchableFields = [
                player.displayName,
                player.name,
                player.firstName,
                player.lastName
            ].filter(field => field && typeof field === 'string');
            
            return searchableFields.some(field => {
                const fieldLower = field.toLowerCase();
                // Buscar coincidencia exacta o parcial
                return fieldLower.includes(name) || 
                       name.includes(fieldLower) ||
                       fieldLower.replace(/[^a-z0-9]/g, '') === name.replace(/[^a-z0-9]/g, '');
            });
        });

        if (foundPlayer) {
            console.log('[DEBUG] Found player by partial match:', 
                foundPlayer.displayName || foundPlayer.name || foundPlayer.firstName);
            return foundPlayer;
        }

        // 6. Buscar en nombre completo (firstName + lastName)
        foundPlayer = this.usersData.find(player => {
            if (player.firstName && player.lastName) {
                const fullName = `${player.firstName} ${player.lastName}`.toLowerCase();
                const fullNameReversed = `${player.lastName} ${player.firstName}`.toLowerCase();
                return fullName.includes(name) || 
                       fullNameReversed.includes(name) ||
                       name.includes(fullName) ||
                       name.includes(fullNameReversed);
            }
            return false;
        });

        console.log('[DEBUG] Final search result:', foundPlayer ? 
            (foundPlayer.displayName || foundPlayer.name || foundPlayer.firstName) : 'Not found');
        
        return foundPlayer;
    }

    // Método para generar contraseña por defecto o validarla
    validatePlayerPassword(player, inputPassword) {
        // Opción 1: Usar contraseña por defecto
        const defaultPassword = 'iterpro123';
        
        // Opción 2: Usar algún campo del jugador como contraseña
        // const playerPassword = player.birthDate || player._id || defaultPassword;
        
        // Opción 3: Usar los últimos 4 dígitos del ID + año de nacimiento
        // const playerId = player._id || '';
        // const playerPassword = playerId.slice(-4) + '2024';
        
        return inputPassword === defaultPassword;
    }

    async authenticate(emailInput, passwordInput) {
        try {
            if (!this.usersData) {
                console.log('[DEBUG] Loading players data from iterpro...');
                await this.fetchAllUsers();
            }

            const nameFromEmail = this.extractNameFromEmail(emailInput);
            console.log('[DEBUG] Extracted name from email:', nameFromEmail);
            
            const foundPlayer = this.findPlayerByName(nameFromEmail);
            
            if (!foundPlayer) {
                throw new Error(`Jugador no encontrado con el nombre: "${nameFromEmail}".
                
Verifica que el nombre antes del @ coincida con:
• displayName
• firstName  
• lastName
• name

Ejemplo: si el jugador se llama "John Smith", prueba con:
• john@soccercentralsa.com
• smith@soccercentralsa.com  
• johnsmith@soccercentralsa.com`);
            }

            console.log('[DEBUG] Found player:', {
                _id: foundPlayer._id,
                displayName: foundPlayer.displayName,
                name: foundPlayer.name,
                firstName: foundPlayer.firstName,
                lastName: foundPlayer.lastName
            });

            // Validar contraseña
            const isPasswordValid = this.validatePlayerPassword(foundPlayer, passwordInput);
            
            if (!isPasswordValid) {
                throw new Error('Contraseña incorrecta. Usa: iterpro123');
            }

            console.log('[DEBUG] Authentication successful for player:', 
                foundPlayer.displayName || foundPlayer.name || foundPlayer.firstName);

            // Enriquecer los datos del jugador para el sistema
            const enrichedPlayer = {
                ...foundPlayer,
                // Agregar campos necesarios para tu sistema
                username: foundPlayer.displayName || foundPlayer.name || foundPlayer.firstName,
                role: 'player', // Todos los de iterpro son jugadores
                name: foundPlayer.displayName || `${foundPlayer.firstName || ''} ${foundPlayer.lastName || ''}`.trim(),
                email: emailInput
            };

            return {
                success: true,
                user: enrichedPlayer,
                message: 'Inicio de sesión exitoso'
            };

        } catch (error) {
            console.error('[DEBUG] Authentication error:', error.message);
            return {
                success: false,
                message: error.message
            };
        }
    }
}

// Función específica para tu formulario
function initializeLogin() {
    const authService = new AuthenticationService();
    
    const form = document.querySelector('form');
    const usernameInput = document.querySelector('#username');
    const passwordInput = document.querySelector('#password');
    const submitBtn = document.querySelector('.login-btn');

    if (!form || !usernameInput || !passwordInput) {
        console.error('[ERROR] No se encontraron los elementos del formulario');
        return;
    }

    // Configurar input de email
    usernameInput.type = 'email';
    usernameInput.placeholder = 'nombre@soccercentralsa.com';
    
    const usernameLabel = document.querySelector('label[for="username"]');
    if (usernameLabel) {
        usernameLabel.textContent = 'Email';
    }

    // Actualizar las credenciales demo
    const demoCredentials = document.querySelector('.demo-credentials');
    if (demoCredentials) {
        demoCredentials.innerHTML = `
            <h4>Instrucciones:</h4>
            <div class="role">
                <strong>Email:</strong> nombre@soccercentralsa.com
            </div>
            <div class="role">
                <strong>Contraseña:</strong> iterpro123
            </div>
        `;
    }

    function showMessage(message, isError = false) {
        let existingMessages = document.querySelectorAll('.error-message, .success-message');
        existingMessages.forEach(msg => msg.remove());

        const msgDiv = document.createElement('div');
        msgDiv.className = isError ? 'error-message' : 'success-message';
        
        if (!isError) {
            msgDiv.style.cssText = `
                background: rgba(40, 167, 69, 0.1);
                color: #28a745;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                border: 1px solid rgba(40, 167, 69, 0.3);
                backdrop-filter: blur(10px);
                white-space: pre-line;
            `;
        } else {
            msgDiv.style.whiteSpace = 'pre-line';
        }
        
        msgDiv.textContent = message;
        form.parentNode.insertBefore(msgDiv, form);
        
        setTimeout(() => {
            if (msgDiv && msgDiv.parentNode) {
                msgDiv.remove();
            }
        }, isError ? 10000 : 5000);
    }

    function setLoadingState(isLoading) {
        submitBtn.disabled = isLoading;
        usernameInput.disabled = isLoading;
        passwordInput.disabled = isLoading;
        
        if (isLoading) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validando...';
        } else {
            submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
        }
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            showMessage('Por favor, completa todos los campos', true);
            return;
        }

        setLoadingState(true);

        try {
            const result = await authService.authenticate(email, password);
            
            if (result.success) {
                localStorage.setItem('currentUser', JSON.stringify(result.user));
                localStorage.setItem('isAuthenticated', 'true');

                // NUEVO: Guardar también los datos de jugadores para reutilizar
                localStorage.setItem('playersData', JSON.stringify(this.usersData));
                localStorage.setItem('playersDataTimestamp', Date.now().toString());
                
                showMessage(`¡Bienvenido ${result.user.name}! Estableciendo sesión...`);
                
                // Establecer sesión en Flask
                try {
                    await fetch('/auth/set_session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: result.user._id,
                            name: result.user.name,
                            username: result.user.username,
                            role: result.user.role
                        })
                    });
                } catch (e) {
                    console.warn('[DEBUG] Could not set Flask session, but continuing...');
                }
                
                setTimeout(() => {
                    const indexUrl = window.FLASK_URLS?.index || '/';
                    window.location.href = indexUrl;
                }, 2000);
            }
            else {
                showMessage(result.message, true);
            }
        } catch (error) {
            console.error('[ERROR] Authentication error:', error);
            showMessage('Error durante la autenticación. Verifica tu conexión e inténtalo de nuevo.', true);
        } finally {
            setLoadingState(false);
        }
    });

    // Pre-cargar jugadores al inicializar
    console.log('[DEBUG] Initializing login with iterpro players...');
    authService.fetchAllUsers()
        .then(() => {
            console.log('[DEBUG] Iterpro players loaded successfully');
            //showMessage(`Sistema listo. Conectado con ${authService.usersData.length} jugadores de iterpro.Usa: nombre@soccercentralsa.com / iterpro123`);
        })
        .catch(error => {
            console.error('[DEBUG] Could not load iterpro players:', error);
            showMessage(`Error cargando jugadores de iterpro: ${error.message}
            
Verifica que tu API esté funcionando.`, true);
        });
}

document.addEventListener('DOMContentLoaded', initializeLogin);
