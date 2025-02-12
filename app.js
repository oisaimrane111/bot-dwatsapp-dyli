const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@adiwajshing/baileys');
const { makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@adiwajshing/baileys');
const sqlite3 = require('sqlite3');

async function connectWhatsApp() {
    const { state, saveState } = await useMultiFileAuthState('./auth');
    const { version } = await fetchLatestBaileysVersion();
    const conn = makeWASocket({
        version,
        printQRInTerminal: true,
        auth: state,
    });

    conn.ev.on('connection.update', (update) => {
        if (update.connection === 'close') {
            console.log('Connection closed, reconnecting...');
            connectWhatsApp();  // Reconnect if connection is lost
        }
    });

    conn.ev.on('messages.upsert', async (m) => {
        const message = m.messages[0];
        const messageText = message.message.conversation.toLowerCase().trim();
        const senderId = message.key.remoteJid;

        if (messageText === "!create_tournament") {
            const parts = messageText.split(" ");
            if (parts.length < 3) {
                conn.sendMessage(senderId, '⚠️ Usage: !create_tournament <name> <format>', { text: 'text' });
            } else {
                const name = parts[1];
                const format = parts[2];
                const db = new sqlite3.Database('./tournaments.db');
                db.run("INSERT INTO tournaments (name, format) VALUES (?, ?)", [name, format], (err) => {
                    if (err) {
                        conn.sendMessage(senderId, '❌ Error creating tournament!', { text: 'text' });
                    } else {
                        conn.sendMessage(senderId, `✅ Tournament '${name}' created with format '${format}'! 🏆`, { text: 'text' });
                    }
                });
            }
        } else {
            conn.sendMessage(senderId, '❌ Invalid command! Use !help for available commands.', { text: 'text' });
        }
    });
}

async function initDb() {
    const db = new sqlite3.Database('./tournaments.db');
    db.serialize(() => {
        db.run("CREATE TABLE IF NOT EXISTS tournaments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, format TEXT)");
        db.run("CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY AUTOINCREMENT, tournament_id INTEGER, name TEXT, FOREIGN KEY (tournament_id) REFERENCES tournaments(id))");
        db.run("CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, tournament_id INTEGER, team1 TEXT, score1 INTEGER, team2 TEXT, score2 INTEGER, FOREIGN KEY (tournament_id) REFERENCES tournaments(id))");
    });
}

connectWhatsApp();
initDb();
