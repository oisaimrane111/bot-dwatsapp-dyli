import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import sqlite3
import random

app = Flask(__name__)

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Database setup
def init_db():
    conn = sqlite3.connect("tournaments.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'ongoing'
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER,
        team1 TEXT,
        team2 TEXT,
        score TEXT,
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT UNIQUE,
        points INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Admins list (replace with actual WhatsApp numbers)
ADMINS = {"+1234567890"}  # Example admin number

# Player guessing game data
players = {
    "messi": "https://example.com/messi.jpg",
    "ronaldo": "https://example.com/ronaldo.jpg",
    "neymar": "https://example.com/neymar.jpg"
}
current_challenge = {}

# Function to send WhatsApp messages
def send_whatsapp_message(to, message, media_url=None):
    message_data = {
        "from_": TWILIO_WHATSAPP_NUMBER,
        "body": message,
        "to": to
    }
    if media_url:
        message_data["media_url"] = media_url
    client.messages.create(**message_data)

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From", "")
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == "/start":
        msg.body("🔥 Welcome to the eFootball Tournament Bot! ⚽\nUse /help for commands.")
    elif incoming_msg == "/help":
        msg.body("📌 Commands:\n🏆 /create_tournament <name> <type> - Admin Only\n⚽ /match_result <tournament> <team1> <team2> <score> - Admin Only\n📋 /view_tournaments - View all tournaments\n📊 /view_matches <tournament> - View match results\n🎯 /guess_player - Guess the player\n🥇 /leaderboard - View top scorers")
    elif incoming_msg.startswith("/create_tournament") and sender in ADMINS:
        try:
            _, name, t_type = incoming_msg.split(" ", 2)
            conn = sqlite3.connect("tournaments.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tournaments (name, type) VALUES (?, ?)", (name, t_type))
            conn.commit()
            conn.close()
            msg.body(f"✅ Tournament '{name}' ({t_type}) created successfully! 🎉")
        except:
            msg.body("❌ Invalid format. Use: /create_tournament <name> <type>")
    elif incoming_msg.startswith("/match_result") and sender in ADMINS:
        try:
            _, tournament, team1, team2, score = incoming_msg.split(" ", 4)
            conn = sqlite3.connect("tournaments.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO matches (tournament_id, team1, team2, score) VALUES ((SELECT id FROM tournaments WHERE name=?), ?, ?, ?)", (tournament, team1, team2, score))
            conn.commit()
            conn.close()
            msg.body(f"📢 Result recorded: {team1} {score} {team2} in {tournament}. ⚽")
        except:
            msg.body("❌ Invalid format. Use: /match_result <tournament> <team1> <team2> <score>")
    elif incoming_msg == "/view_tournaments":
        conn = sqlite3.connect("tournaments.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, type, status FROM tournaments")
        tournaments = cursor.fetchall()
        conn.close()
        if tournaments:
            msg.body("🏆 Tournaments:\n" + "\n".join([f"🔹 {t[0]} ({t[1]}) - {t[2]}" for t in tournaments]))
        else:
            msg.body("❌ No tournaments found.")
    elif incoming_msg == "/guess_player":
        player, image_url = random.choice(list(players.items()))
        current_challenge[sender] = player
        send_whatsapp_message(sender, "🔍 Guess the player! Reply with the name.", image_url)
    elif sender in current_challenge and incoming_msg == current_challenge[sender]:
        conn = sqlite3.connect("tournaments.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO leaderboard (player, points) VALUES (?, 1) ON CONFLICT(player) DO UPDATE SET points = points + 1", (sender,))
        conn.commit()
        conn.close()
        del current_challenge[sender]
        msg.body("✅ Correct! You earned a point! 🏆")
    elif incoming_msg == "/leaderboard":
        conn = sqlite3.connect("tournaments.db")
        cursor = conn.cursor()
        cursor.execute("SELECT player, points FROM leaderboard ORDER BY points DESC LIMIT 5")
        leaderboard = cursor.fetchall()
        conn.close()
        if leaderboard:
            msg.body("🥇 Leaderboard:\n" + "\n".join([f"{i+1}. {l[0]} - {l[1]} pts" for i, l in enumerate(leaderboard)]))
        else:
            msg.body("❌ No scores yet.")
    else:
        msg.body("⚠️ Invalid command. Use /help for available commands.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
