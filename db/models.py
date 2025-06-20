from typing import List, Optional

from sqlalchemy import DECIMAL, Date, DateTime, ForeignKey, ForeignKeyConstraint, Index, Integer, String, Text, Enum as SqlEnum
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class Classes(Base):
    __tablename__ = 'classes'
    __table_args__ = {'comment': 'Entidad de A-Champs'}

    class_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Identificador único de la clase o grupo de entrenamiento (A-CHAMPS)')
    name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre de la clase')
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='Notas adicionales sobre la clase')

    metrics: Mapped[List['Metrics']] = relationship('Metrics', back_populates='class_')


class Roles(Base):
    __tablename__ = 'roles'

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID del rol del sistema')
    role_name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre del rol (Admin, Coach, Manager, Player)')

    users: Mapped[List['Users']] = relationship('Users', back_populates='role')


class Teams(Base):
    __tablename__ = 'teams'
    __table_args__ = {'comment': 'Entidad de BYGA y A-Champs'}

    team_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Identificador único del equipo (todas las plataformas)')
    name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre del equipo')
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='Observaciones adicionales sobre el equipo')

    games: Mapped[List['Games']] = relationship('Games', foreign_keys='[Games.team_away_id]', back_populates='team_away')
    games_: Mapped[List['Games']] = relationship('Games', foreign_keys='[Games.team_home_id]', back_populates='team_home')
    metrics: Mapped[List['Metrics']] = relationship('Metrics', back_populates='team')
    player_teams: Mapped[List['PlayerTeams']] = relationship('PlayerTeams', back_populates='team')


class Games(Base):
    __tablename__ = 'games'
    __table_args__ = (
        ForeignKeyConstraint(['team_away_id'], ['teams.team_id'], name='games_ibfk_2'),
        ForeignKeyConstraint(['team_home_id'], ['teams.team_id'], name='games_ibfk_1'),
        Index('team_away_id', 'team_away_id'),
        Index('team_home_id', 'team_home_id'),
        {'comment': 'Tabla de partidos de TAKA'}
    )

    game_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Identificador único del partido (TAKA.io)')
    team_home_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Equipo local')
    team_away_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Equipo visitante')
    final_score: Mapped[Optional[str]] = mapped_column(String(255), comment='Resultado final del partido')
    match_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha del partido')

    team_away: Mapped[Optional['Teams']] = relationship('Teams', foreign_keys=[team_away_id], back_populates='games')
    team_home: Mapped[Optional['Teams']] = relationship('Teams', foreign_keys=[team_home_id], back_populates='games_')
    videos: Mapped[List['Videos']] = relationship('Videos', back_populates='game')
    player_game_stats: Mapped[List['PlayerGameStats']] = relationship('PlayerGameStats', back_populates='game')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.role_id'], name='users_ibfk_1'),
        Index('role_id', 'role_id')
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='ID único del usuario del sistema')
    role_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Rol del usuario en el sistema')
    first_name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre')
    last_name: Mapped[Optional[str]] = mapped_column(String(255), comment='Apellido')
    email: Mapped[Optional[str]] = mapped_column(String(255), comment='Correo electrónico de acceso')
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), comment='Contraseña cifrada')
    birth_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(255))
    country: Mapped[Optional[str]] = mapped_column(String(255))
    photo_url: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Fecha de creación')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Fecha de última modificación')

    role: Mapped[Optional['Roles']] = relationship('Roles', back_populates='users')
    players: Mapped[List['Players']] = relationship('Players', back_populates='user')


class Players(Base):
    __tablename__ = 'players'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], name='players_ibfk_1'),
        Index('user_id', 'user_id'),
        {'comment': 'Entidad que unifica información básica, escolar, médica, '
                'deportiva y de contacto del jugador desde TAKA, BYGA y A-Champs'}
    )

    player_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Identificador único del jugador (ID común entre plataformas)')
    user_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Rol: Admin, Coach, Manager, Player')
    number: Mapped[Optional[int]] = mapped_column(Integer, comment='Dorsal o número de camiseta del jugador (BYGA)')
    school_name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre de la escuela del jugador (BYGA)')
    primary_position: Mapped[Optional[str]] = mapped_column(String(255), comment='Posición principal del jugador (BYGA)')
    secondary_position: Mapped[Optional[str]] = mapped_column(String(255), comment='Posición secundaria del jugador (BYGA)')
    birth_certificate_on_file: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Certificado de nacimiento registrado (BYGA)')
    birthdate_verified: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Verificación de fecha de nacimiento (BYGA)')
    training_location: Mapped[Optional[str]] = mapped_column(String(255), comment='Lugar habitual de entrenamiento (BYGA)')
    grade_level: Mapped[Optional[str]] = mapped_column(String(255), comment='Nivel de grado escolar (BYGA)')
    phone: Mapped[Optional[str]] = mapped_column(String(255), comment='Teléfono del jugador (BYGA)')
    shirt_size: Mapped[Optional[str]] = mapped_column(String(255), comment='Talla de camiseta (BYGA)')
    short_size: Mapped[Optional[str]] = mapped_column(String(255), comment='Talla de pantalón corto (BYGA)')
    country_of_birth: Mapped[Optional[str]] = mapped_column(String(255), comment='País de nacimiento (BYGA)')
    country_of_citizenship: Mapped[Optional[str]] = mapped_column(String(255), comment='País de nacionalidad legal (BYGA)')
    nationality: Mapped[Optional[str]] = mapped_column(String(255), comment='Nacionalidad deportiva o pasaporte secundario (TAKA.io)')
    city: Mapped[Optional[str]] = mapped_column(String(255), comment='Ciudad de residencia (BYGA)')
    registration_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha en la que fue registrado en la academia (BYGA)')
    education_level: Mapped[Optional[str]] = mapped_column(String(255), comment='Nivel educativo actual (BYGA)')
    last_team: Mapped[Optional[str]] = mapped_column(String(255), comment='Último equipo anterior (BYGA)')
    dominant_foot: Mapped[Optional[str]] = mapped_column(String(255), comment='Pie dominante: izquierdo/derecho (TAKA.io / A-CHAMPS)')
    height: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 0), comment='Altura en centímetros (TAKA.io)')
    athlete_number: Mapped[Optional[str]] = mapped_column(String(255), comment='Número de atleta (A-CHAMPS)')
    social_security_number: Mapped[Optional[str]] = mapped_column(String(255), comment='Número de seguro social (solo admin) (BYGA)')
    graduation_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha de graduación estimada de secundaria (BYGA)')
    insurance_company: Mapped[Optional[str]] = mapped_column(String(255), comment='Compañía aseguradora (admin only) (BYGA)')
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(255), comment='Número de póliza de seguro (admin only) (BYGA)')
    insurance_group_number: Mapped[Optional[str]] = mapped_column(String(255), comment='Número de grupo del seguro (admin only) (BYGA)')
    sanctioned_outside_us: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='¿Ha jugado fútbol sancionado fuera de EE.UU.? (BYGA)')
    physician_name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre del médico de cabecera (BYGA)')
    physician_phone: Mapped[Optional[str]] = mapped_column(String(255), comment='Teléfono del médico (BYGA)')
    health_notes: Mapped[Optional[str]] = mapped_column(Text, comment='Alergias u observaciones médicas relevantes (BYGA)')
    player_activity_history: Mapped[Optional[str]] = mapped_column(Text, comment='Pestaña Activity de Player BYGA: Historial de actividad del jugador: registros de inscripciones, bajas, eventos o movimientos internos')
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='Observaciones generales del jugador (A-CHAMPS / BYGA)')

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='players')
    metrics: Mapped[List['Metrics']] = relationship('Metrics', back_populates='player')
    player_documents: Mapped[List['PlayerDocuments']] = relationship('PlayerDocuments', back_populates='player')
    player_evaluations: Mapped[List['PlayerEvaluations']] = relationship('PlayerEvaluations', back_populates='player')
    player_game_stats: Mapped[List['PlayerGameStats']] = relationship('PlayerGameStats', back_populates='player')
    player_teams: Mapped[List['PlayerTeams']] = relationship('PlayerTeams', back_populates='player')
    player_videos: Mapped[List['PlayerVideos']] = relationship('PlayerVideos', back_populates='player')
    player_assessments: Mapped[list['PlayerAssessments']] = relationship('PlayerAssessments', back_populates='player')


class Videos(Base):
    __tablename__ = 'videos'
    __table_args__ = (
        ForeignKeyConstraint(['game_id'], ['games.game_id'], name='videos_ibfk_1'),
        Index('game_id', 'game_id')
    )

    video_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID del video (TAKA.io)')
    game_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Partido al que corresponde el video (TAKA.io)')
    url: Mapped[Optional[str]] = mapped_column(String(255), comment='Enlace al video (puede ser una URL en TAKA.io o una ruta en cloud storage)')

    game: Mapped[Optional['Games']] = relationship('Games', back_populates='videos')
    player_videos: Mapped[List['PlayerVideos']] = relationship('PlayerVideos', back_populates='video')


class Metrics(Base):
    __tablename__ = 'metrics'
    __table_args__ = (
        ForeignKeyConstraint(['class_id'], ['classes.class_id'], name='metrics_ibfk_3'),
        ForeignKeyConstraint(['player_id'], ['players.player_id'], name='metrics_ibfk_1'),
        ForeignKeyConstraint(['team_id'], ['teams.team_id'], name='metrics_ibfk_2'),
        Index('class_id', 'class_id'),
        Index('player_id', 'player_id'),
        Index('team_id', 'team_id'),
        {'comment': 'Excel de métricas de A-Champs'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único del registro de métricas del jugador en una sesión')
    player_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Jugador evaluado')
    index_training_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Sesión de entrenamiento asociada del excel')
    team_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Equipo que participa en la sesión')
    class_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Clase asociada, si aplica')
    coach_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Entrenador que dirigió la sesión')
    training_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha de la sesión')
    type: Mapped[Optional[str]] = mapped_column(String(255), comment='Tipo de entrenamiento (táctico, físico, técnico...)')
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='Observaciones adicionales')
    drill_name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre del ejercicio o prueba')
    level: Mapped[Optional[str]] = mapped_column(String(255), comment='Nivel o dificultad del ejercicio')
    program: Mapped[Optional[str]] = mapped_column(String(255), comment='Programa o plan de entrenamiento')
    goal: Mapped[Optional[str]] = mapped_column(String(255), comment='Objetivo del ejercicio')
    total_time: Mapped[Optional[int]] = mapped_column(Integer, comment='Tiempo total en segundos')
    round: Mapped[Optional[int]] = mapped_column(Integer, comment='Ronda o repetición')
    hits: Mapped[Optional[int]] = mapped_column(Integer, comment='Aciertos')
    misses: Mapped[Optional[int]] = mapped_column(Integer, comment='Fallos')
    drops: Mapped[Optional[int]] = mapped_column(Integer, comment='Pérdidas')
    correct: Mapped[Optional[int]] = mapped_column(Integer, comment='Respuestas correctas')
    wrong: Mapped[Optional[int]] = mapped_column(Integer, comment='Respuestas incorrectas')
    distraction: Mapped[Optional[int]] = mapped_column(Integer, comment='Número de distracciones registradas')
    avg_reaction_time: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 0), comment='Tiempo de reacción promedio')
    split_times: Mapped[Optional[str]] = mapped_column(Text, comment='Tiempos intermedios separados por comas')

    class_: Mapped[Optional['Classes']] = relationship('Classes', back_populates='metrics')
    player: Mapped[Optional['Players']] = relationship('Players', back_populates='metrics')
    team: Mapped[Optional['Teams']] = relationship('Teams', back_populates='metrics')


class PlayerDocuments(Base):
    __tablename__ = 'player_documents'
    __table_args__ = (
        ForeignKeyConstraint(['player_id'], ['players.player_id'], name='player_documents_ibfk_1'),
        Index('player_id', 'player_id')
    )

    document_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único del documento')
    player_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Jugador al que pertenece el documento')
    document_type: Mapped[Optional[str]] = mapped_column(String(255), comment='Tipo de documento (Ej. US Club Waiver, Registration Form, etc.)')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='Descripción del documento o instrucciones para subirlo')
    status: Mapped[Optional[str]] = mapped_column(String(255), comment='Estado del documento (Ej. uploaded, pending, not uploaded)')
    file_url: Mapped[Optional[str]] = mapped_column(String(255), comment='URL del archivo si ha sido subido')
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Fecha en la que fue subido el documento')

    player: Mapped[Optional['Players']] = relationship('Players', back_populates='player_documents')


class PlayerEvaluations(Base):
    __tablename__ = 'player_evaluations'
    __table_args__ = (
        ForeignKeyConstraint(['player_id'], ['players.player_id'], name='player_evaluations_ibfk_1'),
        Index('player_id', 'player_id'),
        {'comment': 'BYGA (evaluations de jugador)y métricas de A-Champs'}
    )

    evaluation_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único de la evaluación')
    player_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Jugador evaluado')
    evaluation_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha de la evaluación')
    category: Mapped[Optional[str]] = mapped_column(String(255), comment='Categoría: physical, technical, academic, mental...')
    metric_name: Mapped[Optional[str]] = mapped_column(String(255), comment='Nombre del indicador evaluado')
    value: Mapped[Optional[str]] = mapped_column(String(255), comment='Resultado de la evaluación')
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='Notas adicionales del evaluador')

    player: Mapped[Optional['Players']] = relationship('Players', back_populates='player_evaluations')


class PlayerGameStats(Base):
    __tablename__ = 'player_game_stats'
    __table_args__ = (
        ForeignKeyConstraint(['game_id'], ['games.game_id'], name='player_game_stats_ibfk_1'),
        ForeignKeyConstraint(['player_id'], ['players.player_id'], name='player_game_stats_ibfk_2'),
        Index('game_id', 'game_id'),
        Index('player_id', 'player_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único del registro de estadísticas de partido por jugador')
    game_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Partido jugado')
    player_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Jugador evaluado')
    starter: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='¿Fue titular en el partido?')
    goals: Mapped[Optional[int]] = mapped_column(Integer, comment='Goles anotados')
    minutes_played: Mapped[Optional[int]] = mapped_column(Integer, comment='Minutos jugados')

    game: Mapped[Optional['Games']] = relationship('Games', back_populates='player_game_stats')
    player: Mapped[Optional['Players']] = relationship('Players', back_populates='player_game_stats')


class PlayerTeams(Base):
    __tablename__ = 'player_teams'
    __table_args__ = (
        ForeignKeyConstraint(['player_id'], ['players.player_id'], name='player_teams_ibfk_1'),
        ForeignKeyConstraint(['team_id'], ['teams.team_id'], name='player_teams_ibfk_2'),
        Index('player_id', 'player_id'),
        Index('team_id', 'team_id'),
        {'comment': 'Historial de equipos por jugador, permite múltiples etapas en '
                'distintos clubes o temporadas'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único de la relación entre jugador y equipo')
    player_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Jugador vinculado al equipo')
    team_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Equipo en el que juega o ha jugado el jugador')
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha de inicio de su pertenencia al equipo')
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha de salida del equipo, si aplica')

    player: Mapped[Optional['Players']] = relationship('Players', back_populates='player_teams')
    team: Mapped[Optional['Teams']] = relationship('Teams', back_populates='player_teams')


class PlayerVideos(Base):
    __tablename__ = 'player_videos'
    __table_args__ = (
        ForeignKeyConstraint(['player_id'], ['players.player_id'], name='player_videos_ibfk_1'),
        ForeignKeyConstraint(['video_id'], ['videos.video_id'], name='player_videos_ibfk_2'),
        Index('player_id', 'player_id'),
        Index('video_id', 'video_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único de la relación jugador-video')
    player_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Jugador que aparece en el video')
    video_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Video en el que participa el jugador')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='Breve descripción del contenido o tipo de jugada (opcional)')

    player: Mapped[Optional['Players']] = relationship('Players', back_populates='player_videos')
    video: Mapped[Optional['Videos']] = relationship('Videos', back_populates='player_videos')

class CoreValue(Base):
    __tablename__ = 'core_values'
    __table_args__ = (
        Index('ix_core_values_id', 'id'),
        {'comment': 'Valores fundamentales evaluados en los jugadores'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='ID único del valor fundamental')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Nombre del valor fundamental')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='Descripción del valor fundamental')

    assessments: Mapped[List['PlayerAssessments']] = relationship('PlayerAssessments', back_populates='core_value')

class Programs(Base):
    __tablename__ = 'programs'
    __table_args__ = (
        Index('ix_programs_id', 'id'),
        {'comment': 'Programas de entrenamiento asociados a las evaluaciones'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único del programa')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Nombre del programa de entrenamiento')

    assessments: Mapped[List['PlayerAssessments']] = relationship('PlayerAssessments', back_populates='program')

class PlayerAssessments(Base):
    __tablename__ = 'player_assessments'
    __table_args__ = (
        ForeignKeyConstraint(['player_id'], ['players.player_id'], name='player_assessments_ibfk_1'),
        ForeignKeyConstraint(['coach_id'], ['users.user_id'], name='player_assessments_ibfk_2'),
        ForeignKeyConstraint(['core_value_id'], ['core_values.id'], name='player_assessments_ibfk_3'),
        ForeignKeyConstraint(['program_id'], ['programs.id'], name='player_assessments_ibfk_4'),
        Index('player_id', 'player_id'),
        Index('coach_id', 'coach_id'),
        Index('core_value_id', 'core_value_id'),
        Index('program_id', 'program_id'),
        {'comment': 'Evaluaciones cualitativas realizadas por los entrenadores a los jugadores'}
    )

    assessment_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID único de la evaluación')
    player_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='Jugador evaluado')
    coach_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='Entrenador que realiza la evaluación')
    category: Mapped[str] = mapped_column(SqlEnum("Técnico", "Físico", "Mental", "Táctico", "Colectivo", "Valores", name="category_enum"), nullable=False)
    core_value_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Valor fundamental asociado')
    program_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Programa relacionado con la evaluación')
    item: Mapped[str] = mapped_column(String(255), nullable=False, comment='Ítem o aspecto evaluado')
    value: Mapped[int] = mapped_column(Integer, nullable=False, comment='Valor numérico asignado')
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='Observaciones del entrenador')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, comment='Fecha de creación del registro')

    core_value: Mapped[Optional['CoreValue']] = relationship('CoreValue', back_populates='assessments')
    program: Mapped[Optional['Programs']] = relationship('Programs', back_populates='assessments')
    player: Mapped['Players'] = relationship('Players', back_populates='player_assessments')
    coach: Mapped['Users'] = relationship('Users', backref='coach_assessments')

