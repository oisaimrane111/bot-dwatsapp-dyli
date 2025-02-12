import os
import requests
from flask import Flask, request

app = Flask(__name__)

# WhatsApp Cloud API credentials
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")  # Replace with your access token
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")  # Replace with your phone number ID
API_URL = f"https://graph.facebook.com/v15.0/{PHONE_NUMBER_ID}/messages"

def send_message(to, message):
    """Send message via WhatsApp Cloud API"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,  # Receiver's phone number (in international format)
        "text": {"body": message}  # Message content
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.status_code}, {response.text}")

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From", "").strip()  # Get the sender's phone number
    response = "❌ Invalid command! Use !help for available commands."

    if incoming_msg.startswith("!create_tournament"):
        parts = incoming_msg.split(" ", 2)
        if len(parts) < 3:
            response = "⚠️ Usage: !create_tournament <name> <format>"
        else:
            name, format_type = parts[1], parts[2]
            # Database code here for creating a tournament
            response = f"✅ Tournament '{name}' created successfully with format '{format_type}'! 🏆"
    
    elif incoming_msg.startswith("!add_team"):
        parts = incoming_msg.split(" ", 2)
        if len(parts) < 3:
            response = "⚠️ Usage: !add_team <tournament> <team_name>"
        else:
            tournament, team_name = parts[1], parts[2]
            # Database code here for adding a team
            response = f"✅ Team '{team_name}' added to '{tournament}'! ⚽"
    
    elif incoming_msg.startswith("!set_match"):
        parts = incoming_msg.split(" ", 5)
        if len(parts) < 6:
            response = "⚠️ Usage: !set_match <tournament> <team1> <score1> <team2> <score2>"
        else:
            tournament, team1, score1, team2, score2 = parts[1], parts[2], parts[3], parts[4], parts[5]
            # Database code here for setting a match result
            response = f"✅ Match result recorded: {team1} {score1}-{score2} {team2} ⚽"
    
    # Send the response to WhatsApp
    send_message(sender, response)

    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
