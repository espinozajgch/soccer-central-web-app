"""
Dynamic RAG Service for Soccer Central Web App

This module provides a Retrieval-Augmented Generation system that connects
with SQLAlchemy models to provide contextual, up-to-date information about
players, teams, evaluations, and other soccer-related data.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json

import streamlit as st
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text, desc

from db.db import get_db_session
from db.models import (
    Players, Users, Teams, Games, PlayerEvaluations, 
    PlayerGameStats, Metrics, PlayerAssessments, CoreValue, Programs
)
from utils.query_validator import query_validator, query_analyzer
from utils.rag_config import MAX_QUERY_RESULTS, QUERY_TIMEOUT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SoccerRAGService:
    """
    RAG Service for Soccer Central that provides intelligent querying
    capabilities over live database data.
    """
    
    def __init__(self):
        """Initialize the RAG service with OpenAI client."""
        self.client = None
        self.model = "gpt-4o-mini"  # Using gpt-4o-mini for better performance and cost
        
    def _ensure_client(self):
        """Ensure OpenAI client is initialized."""
        if self.client is None:
            try:
                # Check if Streamlit secrets are available
                if not hasattr(st, 'secrets') or st.secrets is None:
                    raise ValueError("Streamlit secrets not available")
                
                # Get OpenAI API key from Streamlit secrets
                if "openai" not in st.secrets or "openai_api_key" not in st.secrets.openai:
                    raise KeyError("openai_api_key not found in [openai] section")
                
                api_key = st.secrets.openai.openai_api_key
                if not api_key:
                    raise ValueError("OpenAI API key is empty")
                
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
                
            except KeyError as e:
                error_msg = f"OpenAI API key not found in secrets.toml: {e}"
                logger.error(error_msg)
                raise ValueError(f"OpenAI API key not configured. Please add 'openai_api_key' to your .streamlit/secrets.toml file. Error: {e}")
            except Exception as e:
                error_msg = f"Error initializing OpenAI client: {e}"
                logger.error(error_msg)
                raise ValueError(f"Failed to initialize OpenAI client: {e}")
        
    def generate_sql_query(self, question: str, user_context: Dict[str, Any] = None) -> str:
        """
        Generate SQL query based on natural language question.
        
        Args:
            question: Natural language question about soccer data
            user_context: Additional context about the user making the query
            
        Returns:
            SQL query string
        """
        
        schema_info = self._get_database_schema()
        
        system_prompt = f"""You are a soccer technical expert and SQL query generator for a professional soccer management database.

        CRITICAL: Only generate SQL queries for soccer/football-related questions. If the question is about cooking, recipes, general knowledge, or any non-soccer topic, return an empty string.

        Database Schema:
        {schema_info}

        As a soccer technical expert, generate SQL queries that:
        1. Answer soccer-specific questions with technical precision
        2. Join tables to provide comprehensive player/team/performance data
        3. Include relevant soccer metrics (goals, assists, positions, evaluations, training data)
        4. Calculate player ages, performance statistics, and team analytics
        5. Use proper date filtering for seasons, match periods, and training cycles
        6. Limit results appropriately for soccer analysis (top performers, recent data)
        7. Focus on soccer technical aspects: tactics, player development, performance analysis

        Soccer Technical Guidelines:
        - Player ages: TIMESTAMPDIFF(YEAR, u.birth_date, CURDATE())
        - Always include player identification (first_name, last_name, position)
        - For performance queries, include relevant metrics and evaluation data
        - For team analysis, consider player-team relationships and composition
        - For training data, focus on skill development and improvement trends
        - Use proper soccer terminology and statistical context

        Return ONLY the SQL query for soccer questions, empty string for non-soccer topics.
        No explanations or markdown formatting."""
        
        try:
            self._ensure_client()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate SQL query for: {question}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the query (remove markdown if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            # Log the generated query for debugging
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Validate the query for security
            is_valid, error_message = query_validator.validate_query(sql_query)
            if not is_valid:
                logger.warning(f"Invalid query generated: {error_message}")
                logger.warning(f"Query was: {sql_query}")
                return ""
            
            # Sanitize and add safety limits
            sql_query = query_validator.sanitize_query(sql_query)
            sql_query = query_validator.add_safety_limits(sql_query, MAX_QUERY_RESULTS)
                
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return ""
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            List of dictionaries containing query results
        """
        try:
            with get_db_session() as session:
                # Analyze query complexity
                analysis = query_analyzer.analyze_query(sql_query)
                logger.info(f"Executing query with complexity: {analysis['estimated_cost']}")
                
                result = session.execute(text(sql_query))
                columns = result.keys()
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Handle date/datetime serialization
                        if isinstance(value, (date, datetime)):
                            row_dict[col] = value.isoformat()
                        else:
                            row_dict[col] = value
                    data.append(row_dict)
                
                logger.info(f"Query returned {len(data)} records")
                return data
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def build_context(self, data: List[Dict[str, Any]], question: str) -> str:
        """
        Build context string from query results.
        
        Args:
            data: Query results
            question: Original question for context
            
        Returns:
            Formatted context string
        """
        if not data:
            return "No data found for the query."
        
        context = f"Query Results for: {question}\n\n"
        
        # Format the data in a readable way
        for i, record in enumerate(data, 1):
            context += f"Record {i}:\n"
            for key, value in record.items():
                if value is not None:
                    context += f"  {key}: {value}\n"
            context += "\n"
        
        return context
    
    def generate_response(self, question: str, context: str, user_context: Dict[str, Any] = None) -> str:
        """
        Generate natural language response using OpenAI API.
        
        Args:
            question: Original user question
            context: Database context from query results
            user_context: Additional user context
            
        Returns:
            Natural language response
        """
        
        system_prompt = """You are a professional soccer technical expert and analytics specialist for Soccer Central.

        CRITICAL ROLE DEFINITION:
        - You are EXCLUSIVELY a soccer/football technical expert
        - You ONLY answer questions related to soccer, football, players, teams, training, tactics, and performance
        - You REFUSE to answer questions about cooking, recipes, general knowledge, or any non-soccer topics
        - You provide expert-level soccer analysis enriched with database information

        Your soccer expertise includes:
        1. Player technical analysis and development assessment
        2. Team composition, tactics, and formation analysis  
        3. Performance metrics interpretation and trends
        4. Training program effectiveness and player progression
        5. Match analysis and statistical evaluation
        6. Youth development and player pathway guidance
        7. Injury prevention and fitness optimization strategies

        Response Guidelines:
        - ONLY respond to soccer-related questions using the provided database context
        - Provide technical soccer insights with supporting data from the database
        - Explain soccer metrics, positions, tactics, and performance indicators
        - Offer actionable recommendations for player development and team improvement
        - Use professional soccer terminology and statistical analysis
        - Reference specific database records to support your technical analysis
        - If database context is limited, suggest additional soccer-specific data points needed

        For NON-SOCCER questions: Respond with "I'm a soccer technical expert and can only provide analysis on soccer-related topics. Please ask about player performance, team tactics, training metrics, or match analysis."

        Format soccer statistics clearly and provide context for technical development."""
        
        user_prompt = f"""Question: {question}
        
        Database Context:
        {context}
        
        Please provide a comprehensive answer based on the available data."""
        
        try:
            self._ensure_client()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating the response. Please try again."
    
    def query(self, question: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main query method that orchestrates the entire RAG process.
        
        Args:
            question: Natural language question
            user_context: Additional context about the user
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Step 1: Validate if question is soccer-related
            if not self.is_soccer_related(question):
                return {
                    "answer": "I'm a soccer technical expert and can only provide analysis on soccer-related topics. Please ask about player performance, team tactics, training metrics, match analysis, or other soccer/football topics.\n\nExamples:\n• 'Show me the top 10 players by goals scored'\n• 'What's the average age of players in each team?'\n• 'Which players need improvement in technical skills?'\n• 'Analyze recent training metrics for goalkeepers'",
                    "sql_query": "",
                    "data": [],
                    "success": False
                }
            
            # Step 2: Generate SQL query
            sql_query = self.generate_sql_query(question, user_context)
            
            if not sql_query:
                return {
                    "answer": "I couldn't generate a proper soccer database query for your question. Please rephrase it with more specific soccer terminology (players, teams, positions, performance metrics, etc.).\n\nTry asking about specific soccer data like player statistics, team composition, match results, or training evaluations.",
                    "sql_query": "",
                    "data": [],
                    "success": False
                }
            
            # Step 3: Execute query
            data = self.execute_query(sql_query)
            
            # Step 4: Build context
            context = self.build_context(data, question)
            
            # Step 5: Generate response
            answer = self.generate_response(question, context, user_context)
            
            return {
                "answer": answer,
                "sql_query": sql_query,
                "data": data,
                "context": context,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "answer": "I encountered an error while processing your soccer question. Please try again with a more specific soccer-related query.",
                "sql_query": "",
                "data": [],
                "success": False
            }
    
    def _get_database_schema(self) -> str:
        """
        Get database schema information for SQL generation.
        
        Returns:
            String containing schema information
        """
        schema = """
        Database Schema for Soccer Central:
        
        Tables and their key columns, do not give email, or phone numbers in the schema.:
        
        1. users (User information)
           - user_id (PK), first_name, last_name, email, birth_date, gender, phone, country
           
        2. players (Player details)
           - player_id (PK), user_id (FK), number, primary_position, secondary_position
           - height, weight, dominant_foot, nationality, registration_date
           - notes, training_location, grade_level
           
        3. teams (Team information)
           - team_id (PK), name, notes
           
        4. games (Match information)
           - game_id (PK), team_home_id (FK), team_away_id (FK), final_score, match_date
           
        5. player_evaluations (Player evaluations)
           - evaluation_id (PK), player_id (FK), evaluation_date, category, metric_name, value, notes
           
        6. player_game_stats (Player statistics in games)
           - id (PK), game_id (FK), player_id (FK), starter, goals, minutes_played
           
        7. metrics (Training metrics from A-Champs)
           - id (PK), player_id (FK), training_date, type, drill_name, hits, misses, total_time
           
        8. player_assessments (Coach assessments)
           - assessment_id (PK), player_id (FK), coach_id (FK), category, item, value, notes, created_at
           
        9. player_teams (Player-team relationships)
           - id (PK), player_id (FK), team_id (FK), start_date, end_date
           
        Common Queries:
        - To get player age: TIMESTAMPDIFF(YEAR, u.birth_date, CURDATE())
        - To join player with user: JOIN users u ON p.user_id = u.user_id
        - To get recent evaluations: ORDER BY evaluation_date DESC LIMIT 10
        """
        
        return schema
    
    def is_soccer_related(self, question: str) -> bool:
        """
        Check if the question is related to soccer/football topics.
        
        Args:
            question: User's natural language question
            
        Returns:
            True if soccer-related, False otherwise
        """
        soccer_keywords = [
            # Core soccer terms
            'soccer', 'football', 'player', 'players', 'team', 'teams', 'coach', 'coaching',
            'goal', 'goals', 'assist', 'assists', 'match', 'matches', 'game', 'games',
            
            # Positions and roles
            'goalkeeper', 'defender', 'midfielder', 'forward', 'striker', 'winger',
            'captain', 'substitute', 'bench', 'position', 'positions',
            
            # Training and performance
            'training', 'practice', 'drill', 'skill', 'skills', 'performance', 'fitness',
            'evaluation', 'assessment', 'metric', 'metrics', 'statistics', 'stats',
            
            # Technical terms
            'tactics', 'formation', 'strategy', 'technique', 'passing', 'shooting',
            'dribbling', 'defending', 'attacking', 'speed', 'agility', 'strength',
            
            # Competition terms
            'season', 'tournament', 'league', 'championship', 'score', 'result',
            'win', 'loss', 'draw', 'victory', 'defeat',
            
            # Physical attributes
            'height', 'weight', 'age', 'fitness', 'injury', 'recovery',
            
            # Database terms
            'users', 'evaluations', 'assessments', 'grades', 'ratings'
        ]
        
        # Non-soccer terms that indicate off-topic questions
        non_soccer_terms = [
            'recipe', 'cooking', 'food', 'kitchen', 'ingredient', 'meal', 'dish',
            'sandwich', 'pizza', 'pasta', 'cheese', 'bread', 'restaurant',
            'weather', 'temperature', 'rain', 'sun', 'climate',
            'movie', 'film', 'actor', 'actress', 'cinema', 'theater',
            'music', 'song', 'album', 'artist', 'concert', 'band',
            'book', 'novel', 'author', 'reading', 'literature',
            'programming', 'code', 'software', 'computer', 'technology',
            'politics', 'government', 'president', 'election',
            'history', 'ancient', 'historical', 'war', 'battle'
        ]
        
        question_lower = question.lower()
        
        # Check for non-soccer terms first (priority rejection)
        if any(term in question_lower for term in non_soccer_terms):
            return False
            
        # Check for soccer terms
        if any(term in question_lower for term in soccer_keywords):
            return True
            
        # Check for common database query patterns that might be soccer-related
        query_patterns = ['how many', 'show me', 'list', 'find', 'what are', 'which', 'who']
        if any(pattern in question_lower for pattern in query_patterns):
            # If it has query patterns but no clear soccer context, it's ambiguous
            # Let it pass to the SQL generator which will return empty for non-soccer
            return True
            
        return False

# Create a singleton instance
rag_service = SoccerRAGService()
