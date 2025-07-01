"""
Configuration for RAG Service

This file manages configuration settings for the RAG service including
OpenAI API settings, query limits, and other parameters.
"""

# OpenAI Configuration
OPENAI_MODEL = "gpt-4o-mini"  # Cost-effective model with good performance
OPENAI_TEMPERATURE = 0.1      # Low temperature for consistent SQL generation
OPENAI_MAX_TOKENS = 1000      # Maximum tokens for responses

# Query Configuration
MAX_QUERY_RESULTS = 100       # Maximum number of results to return from database
QUERY_TIMEOUT = 30           # Query timeout in seconds

# RAG Configuration
CONTEXT_WINDOW_SIZE = 4000   # Maximum context size for OpenAI
MAX_RETRIES = 3              # Maximum number of retries for failed API calls

# Cache Configuration
ENABLE_QUERY_CACHE = True    # Enable caching for frequent queries
CACHE_TTL = 300             # Cache time-to-live in seconds (5 minutes)

# Security Configuration
ALLOWED_SQL_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
    "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "DISTINCT", "AS", "AND", "OR",
    "IN", "NOT IN", "LIKE", "BETWEEN", "IS NULL", "IS NOT NULL", "COUNT",
    "SUM", "AVG", "MAX", "MIN", "TIMESTAMPDIFF", "CURDATE", "NOW", "YEAR",
    "MONTH", "DAY", "DATE", "CASE", "WHEN", "THEN", "ELSE", "END", "CONCAT",
    "SUBSTRING", "LENGTH", "UPPER", "LOWER", "TRIM", "ROUND", "FLOOR", "CEIL"
]

FORBIDDEN_SQL_KEYWORDS = [
    # Data Modification
    "INSERT", "UPDATE", "DELETE", "REPLACE", "MERGE", "UPSERT",
    
    # Schema Modification
    "CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME",
    
    # Administrative
    "GRANT", "REVOKE", "FLUSH", "RESET", "PURGE", "OPTIMIZE",
    
    # Execution & Procedures
    "EXEC", "EXECUTE", "CALL", "DECLARE", "SET", "USE",
    
    # File Operations
    "LOAD", "OUTFILE", "INFILE", "IMPORT", "EXPORT",
    
    # System Functions
    "SYSTEM", "SHELL", "BENCHMARK", "SLEEP",
    
    # Transaction Control
    "START", "COMMIT", "ROLLBACK", "SAVEPOINT",
    
    # User/Security
    "CREATE USER", "DROP USER", "ALTER USER", "SET PASSWORD",
    
    # Database Control
    "LOCK", "UNLOCK", "KILL", "SHOW PROCESSLIST"
]

# Additional Security Patterns (regex patterns for more complex checks)
FORBIDDEN_PATTERNS = [
    r"INTO\s+OUTFILE",          # File writing
    r"INTO\s+DUMPFILE",         # File writing
    r"LOAD_FILE\s*\(",          # File reading
    r"LOAD\s+DATA",             # Data loading
    r";\s*\w+",                 # Multiple statements
    r"--",                      # SQL comments
    r"/\*.*?\*/",               # Block comments
    r"@@\w+",                   # System variables
    r"INFORMATION_SCHEMA",      # System schema access
    r"MYSQL\.",                 # MySQL system database
    r"PERFORMANCE_SCHEMA",      # Performance schema
    r"SYS\.",                   # System schema
]

# Read-only database user configuration (recommended)
ENFORCE_READ_ONLY_USER = True  # Use a read-only database user if possible

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_QUERIES = True           # Log all SQL queries for debugging
LOG_RESPONSES = False        # Log OpenAI responses (disable in production)

# Example Queries for User Interface
EXAMPLE_QUERIES = [
    {
        "category": "Player Information",
        "queries": [
            "Show me the top 10 players by goals scored this season",
            "What are the recent evaluations for John Smith?",
            "Which players are over 18 years old?",
            "Show me all goalkeepers in the database"
        ]
    },
    {
        "category": "Team Analysis",
        "queries": [
            "What's the average age of players in each team?",
            "Which team has the most players?",
            "Show me teams and their recent game results"
        ]
    },
    {
        "category": "Performance Metrics",
        "queries": [
            "Which players have the highest training metrics this month?",
            "Show me players with the best reaction times",
            "What are the most common training drill types?"
        ]
    },
    {
        "category": "Evaluations & Assessments",
        "queries": [
            "Show me players who need improvement in technical skills",
            "Which coaches have given the most assessments?",
            "What are the latest player evaluations?"
        ]
    }
]
