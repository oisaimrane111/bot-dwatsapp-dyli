from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import sqlite3
import os

app = Flask(__name__)

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def init_db():
    conn = sqlite3.connect("tournaments.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        format TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER,
        name TEXT,
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER,
        team1 TEXT,
        score1 INTEGER,
        team2 TEXT,
        score2 INTEGER,
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
    )
    """)
    conn.commit()
    conn.close()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    response = MessagingResponse()
    msg = response.message()
    
    if incoming_msg.startswith("!create_tournament"):
        parts = incoming_msg.split(" ", 2)
        if len(parts) < 3:
            msg.body("⚠️ Usage: !create_tournament <name> <format>")
        else:
            name, format_type = parts[1], parts[2]
            conn = sqlite3.connect("tournaments.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tournaments (name, format) VALUES (?, ?)", (name, format_type))
            conn.commit()
            conn.close()
            msg.body(f"✅ Tournament '{name}' created successfully with format '{format_type}'! 🏆")
    
    elif incoming_msg.startswith("!add_team"):
        parts = incoming_msg.split(" ", 2)
        if len(parts) < 3:
            msg.body("⚠️ Usage: !add_team <tournament> <team_name>")
        else:
            tournament, team_name = parts[1], parts[2]
            conn = sqlite3.connect("tournaments.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tournaments WHERE name = ?", (tournament,))
            row = cursor.fetchone()
            if row:
                cursor.execute("INSERT INTO teams (tournament_id, name) VALUES (?, ?)", (row[0], team_name))
                conn.commit()
                msg.body(f"✅ Team '{team_name}' added to '{tournament}'! ⚽")
            else:
                msg.body("❌ Tournament not found!")
            conn.close()
    
    elif incoming_msg.startswith("!set_match"):
        parts = incoming_msg.split(" ", 5)
        if len(parts) < 6:
            msg.body("⚠️ Usage: !set_match <tournament> <team1> <score1> <team2> <score2>")
        else:
            tournament, team1, score1, team2, score2 = parts[1], parts[2], parts[3], parts[4], parts[5]
            conn = sqlite3.connect("tournaments.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tournaments WHERE name = ?", (tournament,))
            row = cursor.fetchone()
            if row:
                cursor.execute("INSERT INTO matches (tournament_id, team1, score1, team2, score2) VALUES (?, ?, ?, ?, ?)", 
                               (row[0], team1, score1, team2, score2))
                conn.commit()
                msg.body(f"✅ Match result recorded: {team1} {score1}-{score2} {team2} ⚽")
            else:
                msg.body("❌ Tournament not found!")
            conn.close()
    
    elif incoming_msg.startswith("!standings"):
        msg.body("📊 Feature coming soon! Standings will be available in the next update.")
    
    elif incoming_msg.startswith("!fixtures"):
        msg.body("📅 Feature coming soon! Fixtures will be available in the next update.")
    
    else:
        msg.body("❌ Invalid command! Use !help for available commands.")
    
    return str(response)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
