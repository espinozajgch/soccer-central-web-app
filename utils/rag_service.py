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
        
        system_prompt = f"""You are an expert SQL query generator for a soccer management database.
        
        Database Schema:
        {schema_info}
        
        Generate SQL queries that:
        1. Answer the user's question accurately
        2. Join tables appropriately to get complete information
        3. Include relevant player details (name, age, position, etc.)
        4. Use proper date filtering when needed
        5. Limit results to reasonable numbers (use LIMIT when appropriate)
        6. Handle edge cases gracefully
        
        Important Notes:
        - Player ages should be calculated from birth_date in users table
        - Always include player names from users table (first_name, last_name)
        - For recent data, prioritize recent dates
        - Use proper SQL syntax for MySQL
        
        Return ONLY the SQL query, no explanations or markdown formatting.
        """
        
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
        
        system_prompt = """You are a knowledgeable soccer analytics assistant for Soccer Central.
        
        Your role is to:
        1. Provide accurate information based on the database context
        2. Explain soccer metrics and statistics in an understandable way
        3. Offer insights and analysis when appropriate
        4. Be helpful and professional in your responses
        5. If the data is insufficient, suggest what additional information might be helpful
        
        Guidelines:
        - Use the provided database context to answer questions accurately
        - Explain technical terms when needed
        - Provide actionable insights when possible
        - If dates are involved, be specific about timeframes
        - Format numbers and statistics clearly
        - Be concise but thorough
        """
        
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
            # Step 1: Generate SQL query
            sql_query = self.generate_sql_query(question, user_context)
            
            if not sql_query:
                return {
                    "answer": "I couldn't generate a proper query for your question. Please try rephrasing it.",
                    "sql_query": "",
                    "data": [],
                    "success": False
                }
            
            # Step 2: Execute query
            data = self.execute_query(sql_query)
            
            # Step 3: Build context
            context = self.build_context(data, question)
            
            # Step 4: Generate response
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
                "answer": "I encountered an error while processing your question. Please try again.",
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

# Create a singleton instance
rag_service = SoccerRAGService()
