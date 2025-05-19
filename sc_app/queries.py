

#***********************Preparación de Consulta de Datos Personalizada y Elementos a Visualizar*************************************************************
    # Se seleccionan campos de la tabla "users" y la tabla "players".
    # Si se requieren otros campos o de otras tablas, se pueden agregar al SELECT y al JOIN.
player_q = """
    SELECT 
        u.user_id,
        u.first_name,
        u.last_name,
        u.birth_date,
        u.gender,
        u.photo_url,
        u.phone,
        p.player_id,
        p.nationality,
        p.city,
        p.number,
        p.dominant_foot,
        p.primary_position,
        p.secondary_position,
        p.height,
        s.goals,
        s.minutes_played
    FROM 
        users AS u
    JOIN 
        players AS p ON u.user_id = p.user_id
    JOIN
        player_game_stats AS s ON p.player_id = s.player_id
    WHERE
        p.player_id = :player_id
    """

#***********************Consulta de Datos 360° del Jugador*************************************************************
player_360 = """
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    u.birth_date,
    u.gender,
    u.photo_url,
    u.phone,
    p.player_id,
    p.nationality,
    p.city,
    p.number,
    p.dominant_foot,
    p.primary_position,
    p.secondary_position,
    p.height,
    s.goals,
    SUM(s.minutes_played) AS total_minutes_played,
    SUM(CASE WHEN s.starter = 1 THEN 1 ELSE 0 END) AS starter_games,
    ts.team_id,
    ts.name,
    ts.games_played,
    ts.games_at_home,
    ts.games_away
FROM 
    users AS u
JOIN 
    players AS p ON u.user_id = p.user_id
JOIN
    player_game_stats AS s ON p.player_id = s.player_id
LEFT JOIN (
    SELECT 
         pt.player_id,
         t.team_id,
         t.name,
         COUNT(g.game_id) AS games_played,
         SUM(CASE WHEN t.team_id = g.team_home_id THEN 1 ELSE 0 END) AS games_at_home,
         SUM(CASE WHEN t.team_id = g.team_away_id THEN 1 ELSE 0 END) AS games_away
    FROM 
         player_teams pt
    JOIN 
         teams t ON pt.team_id = t.team_id
    LEFT JOIN 
         games g ON (t.team_id = g.team_home_id OR t.team_id = g.team_away_id)
    GROUP BY 
         pt.player_id, t.team_id, t.name
) AS ts ON p.player_id = ts.player_id
WHERE
    p.player_id = :player_id
GROUP BY 
    u.user_id,
    u.first_name,
    u.last_name,
    u.birth_date,
    u.gender,
    u.photo_url,
    u.phone,
    p.player_id,
    p.nationality,
    p.city,
    p.number,
    p.dominant_foot,
    p.primary_position,
    p.secondary_position,
    p.height,
    s.goals,
    ts.team_id,
    ts.name,
    ts.games_played,
    ts.games_at_home,
    ts.games_away
"""

#Determinar en cuántos equipos ha jugado el jugador.
player_teams = """
    SELECT DISTINCT
        t.team_id,
        t.name,
        pt.start_date,
        pt.end_date
    FROM player_teams pt
    JOIN teams t ON pt.team_id = t.team_id
    WHERE pt.player_id = :player_id;
"""