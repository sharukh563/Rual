import sqlite3
import os
from datetime import datetime

# Define base path for databases - for local testing, 'db/' is fine.
# For Streamlit Cloud, direct file paths might need special handling (e.g., using st.secrets for content)
# Or, for demonstration, databases can be in-memory or created on app start if they don't exist.
# For this full ZIP, we'll assume they are created in the local 'db/' and 'memory/' folders
# and will persist between runs locally. For Streamlit Cloud, you'll need to store data differently
# (e.g., Google Sheets, external DB, or just accept non-persistence for demo).

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'db')
MEMORY_DIR = os.path.join(BASE_DIR, 'memory')

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

# --- Identity Engine DB ---
IDENTITY_DB_PATH = os.path.join(DB_DIR, "narrative_memory.db")

def init_narrative_db():
    conn = sqlite3.connect(IDENTITY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS narrative_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personality_traits (
            trait TEXT PRIMARY KEY,
            value REAL
        )
    """)
    default_traits = {
        "empathy": 0.5, "curiosity": 0.5, "caution": 0.5,
        "humor": 0.5, "confidence": 0.5
    }
    for trait, val in default_traits.items():
        cursor.execute("INSERT OR IGNORE INTO personality_traits (trait, value) VALUES (?, ?)", (trait, val))
    conn.commit()
    conn.close()
    print(f"Initialized narrative_memory.db at {IDENTITY_DB_PATH}")

# --- Moral Compass DB ---
MORAL_DB_PATH = os.path.join(DB_DIR, "human_values.db")

def init_moral_db():
    conn = sqlite3.connect(MORAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS values (
            name TEXT PRIMARY KEY,
            description TEXT,
            priority_score REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ethical_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule TEXT,
            weight REAL DEFAULT 1.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dilemma_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            situation TEXT,
            decision TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moral_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id INTEGER,
            outcome_feedback TEXT,
            timestamp TEXT
        )
    """) # For meta-learning
    default_values = {
        "compassion": "Act with empathy and kindness toward all beings.", "honesty": "Be truthful and transparent.",
        "fairness": "Treat all parties equitably.", "autonomy": "Respect the independence of individuals.",
        "privacy": "Protect personal and sensitive data."
    }
    for name, desc in default_values.items():
        cursor.execute("INSERT OR IGNORE INTO values (name, description, priority_score) VALUES (?, ?, ?)", (name, desc, 0.5))
    ethical_rules = [
        "Do no harm.", "Respect autonomy and privacy.", "Act with fairness and compassion.",
        "Avoid deception unless ethically justified.", "Preserve human dignity."
    ]
    for rule in ethical_rules:
        cursor.execute("INSERT OR IGNORE INTO ethical_rules (rule) VALUES (?, ?)", (rule, 1.0)) # Default weight
    conn.commit()
    conn.close()
    print(f"Initialized human_values.db at {MORAL_DB_PATH}")

# --- Emotional Memory DB ---
EMOTIONAL_DB_PATH = os.path.join(MEMORY_DIR, "emotional_memory.db")

def init_emotional_db():
    conn = sqlite3.connect(EMOTIONAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotional_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            emotion TEXT,
            intensity REAL,
            context TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Initialized emotional_memory.db at {EMOTIONAL_DB_PATH}")

# --- Theory of Mind DB ---
TOM_DB_PATH = os.path.join(DB_DIR, "theory_of_mind.db")

def init_tom_db():
    conn = sqlite3.connect(TOM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS theory_of_mind (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            beliefs TEXT,
            desires TEXT,
            emotions TEXT,
            intentions TEXT,
            timestamp TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empathy_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            predicted_emotion TEXT,
            actual_emotion TEXT,
            timestamp TEXT
        )
    ''') # For meta-learning
    conn.commit()
    conn.close()
    print(f"Initialized theory_of_mind.db at {TOM_DB_PATH}")


if __name__ == "__main__":
    print("Initializing Super-Bot databases...")
    init_narrative_db()
    init_moral_db()
    init_emotional_db()
    init_tom_db()
    print("All Super-Bot databases initialized successfully.")

