"""
Soccer Central RAG Chat Interface

This page provides an interactive chat interface where users can ask questions
about players, teams, evaluations, and other soccer data using natural language.
The system uses RAG (Retrieval-Augmented Generation) to provide accurate,
contextual responses based on live database data.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json

from utils.util import setup_page, login_if_needed
from utils.login import get_logged_in_user
from utils.rag_service import SoccerRAGService

# Page configuration
setup_page("Soccer Central - AI Assistant")
login_if_needed()

# Get current user context
current_user = get_logged_in_user()

# Check OpenAI API key configuration
try:
    # Try to access the API key to verify it's available
    api_key = st.secrets.openai.openai_api_key
    if not api_key or not api_key.startswith("sk-"):
        st.error("""
        🔑 **Invalid OpenAI API Key**
        
        The OpenAI API key appears to be invalid. Please check your API key in `.streamlit/secrets.toml`:
        
        ```toml
        [openai]
        openai_api_key = "sk-proj-your-actual-key-here"
        ```
        
        Get your API key from: https://platform.openai.com/api-keys
        """)
        st.stop()
except KeyError:
    st.error("""
    🔑 **OpenAI API Key Required**
    
    The AI Assistant requires an OpenAI API key to function. Please add your API key to `.streamlit/secrets.toml`:
    
    ```toml
    [openai]
    openai_api_key = "sk-proj-your-actual-key-here"
    ```
    
    Get your API key from: https://platform.openai.com/api-keys
    """)
    st.stop()
except Exception as e:
    st.error(f"""
    🔑 **Configuration Error**
    
    Error accessing OpenAI API key: {str(e)}
    
    Please check your `.streamlit/secrets.toml` configuration.
    """)
    st.stop()

st.header("🤖 Soccer Central AI Assistant", divider=True)

# Enhanced info banner
st.info("""
🚀 **Enhanced with OpenAI** | 🔒 **Secure Read-Only Access** | ⚡ **Real-Time Database Queries** | 🧠 **Intelligent Responses**
""")

st.markdown("""
**Ask me anything about your soccer data!** I'm powered by advanced AI and can help you with:

🏃‍♂️ **Player Analytics:** Performance metrics, evaluations, progress tracking  
⚽ **Team Insights:** Roster analysis, team comparisons, formation data  
📊 **Training Data:** Drill results, skill assessments, improvement trends  
🏆 **Game Statistics:** Match results, player stats, performance analysis  
📈 **Progress Reports:** Individual development, team growth patterns  

*🔥 **NEW**: Enhanced security, better query understanding, and conversational memory for follow-up questions!*

💡 **Try asking:** *"Show me players who improved their speed in the last month"* or *"Compare the top scorers across all teams"*
""")

# Initialize chat history
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []

# Chat interface
with st.container():
    # Display chat messages
    for message in st.session_state.rag_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show additional info for assistant messages (but only as collapsed expanders)
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                
                # Show SQL query in expander (collapsed by default)
                if metadata.get("sql_query"):
                    with st.expander("🔍 View SQL Query", expanded=False):
                        st.code(metadata["sql_query"], language="sql")
                
                # Show raw data in expander if available (collapsed by default)
                if metadata.get("data") and len(metadata["data"]) > 0:
                    with st.expander("📊 View Raw Data", expanded=False):
                        df = pd.DataFrame(metadata["data"])
                        st.dataframe(df, use_container_width=True)
                        
                        # Provide download option for historical data too
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download data as CSV",
                            data=csv,
                            file_name=f"soccer_data_{metadata.get('timestamp', 'unknown')}.csv",
                            mime="text/csv",
                            key=f"download_{hash(str(metadata))}"  # Unique key for each download button
                        )

# Chat input
if prompt := st.chat_input("Ask about your soccer data..."):
    # Display user message immediately (but don't add to history yet)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process the query
    process_query = True
    query_to_process = prompt

# Check for pending query from example buttons
elif "pending_query" in st.session_state:
    query_to_process = st.session_state.pending_query
    del st.session_state.pending_query
    
    # Display user message immediately (but don't add to history yet)
    with st.chat_message("user"):
        st.markdown(query_to_process)
    
    # Process the query
    process_query = True
else:
    process_query = False

# Process the query if needed
if process_query:
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question and querying the database..."):
            
            # Prepare user context with more details
            user_context = {
                "user_id": current_user.user_id if current_user else None,
                "name": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() if current_user else "Guest",
                "role": getattr(current_user.role, 'role_name', 'guest') if current_user and hasattr(current_user, 'role') and current_user.role else "guest",
                "timestamp": datetime.now().isoformat()
            }
            
            # Query the RAG service with streaming callback
            try:
                # Create RAG service instance
                rag_service = SoccerRAGService()
                
                result = rag_service.query(
                    query_to_process, 
                    user_context
                )
                
                if result["success"]:
                    # Display the response
                    st.markdown(result["answer"])
                    
                    # NOW add both user and assistant messages to chat history
                    st.session_state.rag_messages.append({"role": "user", "content": query_to_process})
                    st.session_state.rag_messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "metadata": {
                            "sql_query": result["sql_query"],
                            "data": result["data"],
                            "timestamp": datetime.now().isoformat()
                        }
                    })
                    
                    # Show SQL query in expander
                    if result["sql_query"]:
                        with st.expander("🔍 View SQL Query"):
                            st.code(result["sql_query"], language="sql")
                    
                    # Show raw data in expander if available
                    if result["data"] and len(result["data"]) > 0:
                        with st.expander("📊 View Raw Data"):
                            df = pd.DataFrame(result["data"])
                            st.dataframe(df, use_container_width=True)
                            
                            # Provide download option
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download data as CSV",
                                data=csv,
                                file_name=f"soccer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                else:
                    error_message = result["answer"]
                    st.error(error_message)
                    
                    # Add both user and error messages to chat history
                    st.session_state.rag_messages.append({"role": "user", "content": query_to_process})
                    st.session_state.rag_messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
                    
            except ValueError as e:
                if "OpenAI API key" in str(e):
                    error_msg = """
🔑 **OpenAI API Configuration Required**

The AI Assistant requires an OpenAI API key to function. Please:

1. Get an API key from https://platform.openai.com/api-keys
2. Add it to your `.streamlit/secrets.toml` file:
```toml
[openai]
openai_api_key = "sk-proj-your-actual-key-here"
```
3. Restart the application

Contact your administrator if you need help setting this up.
                    """
                    st.error(error_msg)
                else:
                    st.error(f"Configuration Error: {str(e)}")
                    
                # Add both user and error messages to chat history
                st.session_state.rag_messages.append({"role": "user", "content": query_to_process})
                st.session_state.rag_messages.append({
                    "role": "assistant", 
                    "content": f"❌ Configuration Error: {str(e)}"
                })
                
            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}"
                st.error(error_msg)
                
                # Add both user and error messages to chat history
                st.session_state.rag_messages.append({"role": "user", "content": query_to_process})
                st.session_state.rag_messages.append({
                    "role": "assistant",
                    "content": f"❌ {error_msg}"
                })

# Sidebar with helpful information
with st.sidebar:
    st.header("💡 Smart Query Examples")
    
    # Use static suggested queries since we don't have a service method for this
    suggested_queries = [
        "Show me the top 10 players by goals scored",
        "What are the recent evaluations for players in the U16 team?",
        "Which players have the highest training metrics this month?",
        "Show me players who need improvement in technical skills",
        "What's the average age of players in each team?"
    ]
    
    # Add some enhanced examples
    enhanced_queries = [
        "📊 How many players are in the database?",
        "⭐ Show me the top 5 players by recent evaluation scores",
        "🏃‍♂️ Find players under 18 years old with good speed metrics",
        "🥅 Which goalkeepers have the best reaction times?",
        "📈 Show me improvement trends for players over the last 3 months",
        "🏆 What teams have the highest average player ratings?",
        "⚽ List recent games and their outcomes",
        "📋 What evaluation criteria are most commonly used?",
        "🎯 Show me players with the best technical skill scores",
        "👥 Which coaches have evaluated the most players?"
    ]
    
    # Combine and limit to 8 examples
    all_queries = enhanced_queries[:8]
    
    for query in all_queries:
        if st.button(query, key=f"example_{hash(query)}", use_container_width=True):
            # Set the query to be processed
            st.session_state.pending_query = query.split(" ", 1)[1] if query.startswith(("📊", "⭐", "🏃‍♂️", "🥅", "📈", "🏆", "⚽", "📋", "🎯", "👥")) else query
            st.rerun()
    
    st.divider()
    
    # Memory and system status
    st.subheader("🧠 Session Info")
    st.write(f"**Chat messages:** {len(st.session_state.rag_messages)}")
    
    # Clear chat button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.rag_messages = []
            st.rerun()
    
    with col2:
        if st.button("🧠 Clear Memory", use_container_width=True):
            st.session_state.rag_messages = []
            st.success("Memory cleared!")
            st.rerun()
    
    st.divider()
    
    # Current user info
    if current_user:
        st.subheader("👤 Current User")
        full_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip()
        st.write(f"**Name:** {full_name or 'Unknown'}")
        role_name = getattr(current_user.role, 'role_name', 'Unknown') if hasattr(current_user, 'role') and current_user.role else 'Unknown'
        st.write(f"**Role:** {role_name}")
        
        # Add user context to queries
        if role_name.lower() in ['coach', 'trainer', 'admin']:
            st.info("🎯 As a " + role_name + ", you can ask about all players and detailed analytics.")
        elif role_name.lower() == 'player':
            st.info("⚽ As a player, focus on questions about your own progress and team performance.")
    
    st.divider()
    
    # Enhanced system info
    st.subheader("ℹ️ System Info")
    st.write("**🤖 AI Framework:** OpenAI GPT-4o-mini")
    st.write("**📊 Data Source:** Live Soccer Database")
    st.write("**🔒 Security:** Secure Read-only SQL Agent")
    st.write("**⚡ Performance:** Optimized query execution")
    st.write("**🔄 Last Updated:** Real-time")
    
    # Show database schema info
    with st.expander("📋 View Database Schema", expanded=False):
        schema_info = """
Database Schema for Soccer Central:

Tables and their key columns:

1. users - User information (user_id, first_name, last_name, birth_date, gender)
2. players - Player details (player_id, user_id, primary_position, height, weight)
3. teams - Team information (team_id, name, notes)
4. games - Match information (game_id, team_home_id, team_away_id, final_score)
5. player_evaluations - Player evaluations (evaluation_id, player_id, evaluation_date, category)
6. player_game_stats - Player statistics in games (id, game_id, player_id, goals)
7. metrics - Training metrics (id, player_id, training_date, type, drill_name)
8. player_assessments - Coach assessments (assessment_id, player_id, coach_id, category)
        """
        st.text(schema_info)
    
    # Enhanced tips
    st.subheader("� Pro Tips")
    st.markdown("""
    **🎯 For Better Results:**
    - Be specific with player/team names
    - Include time periods ("last 30 days", "this season")
    - Ask for comparisons ("compare X vs Y")
    - Request specific metrics or categories
    
    **📊 Analytics Questions:**
    - "Show trends over time"
    - "Find correlations between metrics"
    - "Identify improvement opportunities"
    - "Compare performance across teams"
    
    **🔍 Search Tips:**
    - Use exact names when possible
    - Try different phrasings if needed
    - Ask follow-up questions for details
    - Request explanations of results
    """)
