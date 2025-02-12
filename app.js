const { WAConnection, MessageType } = require('@adiwajshing/baileys');
const sqlite3 = require('sqlite3');
const fs = require('fs');

const conn = new WAConnection();
conn.on('open', () => {
    console.log('WhatsApp Web is ready');
});

// Connect to WhatsApp
async function connectWhatsApp() {
    await conn.connect();
    console.log('Connected to WhatsApp');
}

// Initialize DB (if you don't have one)
function initDb() {
    const db = new sqlite3.Database('./tournaments.db');
    db.serialize(() => {
        db.run("CREATE TABLE IF NOT EXISTS tournaments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, format TEXT)");
        db.run("CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY AUTOINCREMENT, tournament_id INTEGER, name TEXT, FOREIGN KEY (tournament_id) REFERENCES tournaments(id))");
        db.run("CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, tournament_id INTEGER, team1 TEXT, score1 INTEGER, team2 TEXT, score2 INTEGER, FOREIGN KEY (tournament_id) REFERENCES tournaments(id))");
    });
}

// Handle incoming messages
conn.on('chat-update', async (chatUpdate) => {
    if (chatUpdate.messages) {
        const message = chatUpdate.messages[0];
        const messageText = message.message.conversation.toLowerCase().trim();
        const senderId = message.key.remoteJid;

        if (messageText === "!create_tournament") {
            // Example: !create_tournament <name> <format>
            const parts = messageText.split(" ");
            if (parts.length < 3) {
                conn.sendMessage(senderId, '⚠️ Usage: !create_tournament <name> <format>', MessageType.text);
            } else {
                const name = parts[1];
                const format = parts[2];
                const db = new sqlite3.Database('./tournaments.db');
                db.run("INSERT INTO tournaments (name, format) VALUES (?, ?)", [name, format], (err) => {
                    if (err) {
                        conn.sendMessage(senderId, '❌ Error creating tournament!', MessageType.text);
                    } else {
                        conn.sendMessage(senderId, `✅ Tournament '${name}' created with format '${format}'! 🏆`, MessageType.text);
                    }
                });
            }
        } 
        // Add more commands as needed
        else {
            conn.sendMessage(senderId, '❌ Invalid command! Use !help for available commands.', MessageType.text);
        }
    }
});

connectWhatsApp();
initDb();
