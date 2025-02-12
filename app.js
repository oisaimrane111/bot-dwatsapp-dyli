const { makeWASocket, fetchLatestBaileysVersion, useSingleFileAuthState } = require('@adiwajshing/baileys');
const axios = require('axios');

// Giphy API Key
const giphyAPIKey = 'YOUR_GIPHY_API_KEY';
const giphyURL = 'https://api.giphy.com/v1/gifs/random?api_key=' + giphyAPIKey;

// Use emoji in messages
const emojis = {
  football: '⚽',
  winner: '🏆',
  celebration: '🎉'
};

const { state, saveState } = useSingleFileAuthState('./auth_info.json');

// Create the WhatsApp socket
async function startBot() {
  const { version, isLatest } = await fetchLatestBaileysVersion();
  const sock = makeWASocket({
    printQRInTerminal: true,
    auth: state,
    version
  });

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect } = update;
    if (connection === 'close') {
      startBot();
    }
  });

  sock.ev.on('messages.upsert', async ({ messages }) => {
    const msg = messages[0];
    const chat = msg.key.remoteJid;

    if (!msg.message) return;

    if (msg.message.conversation) {
      const text = msg.message.conversation.toLowerCase();

      if (text === '!help') {
        await sock.sendMessage(chat, {
          text: `Here are some commands you can use:
          - !help: Get this help message.
          - !gif: Get a random football GIF! ⚽
          - !score: Get the latest football score.`
        });
      }

      if (text === '!gif') {
        const gifRes = await axios.get(giphyURL);
        const gifUrl = gifRes.data.data.images.original.url;

        await sock.sendMessage(chat, {
          video: { url: gifUrl },
          caption: 'Here’s a random football GIF! ⚽'
        });
      }

      if (text === '!score') {
        // This can be replaced with actual football match data
        await sock.sendMessage(chat, {
          text: `The current score is: Team A 1 - 0 Team B 🏆`
        });
      }
    }
  });

  sock.ev.on('auth-state.update', saveState);
}

startBot().catch((err) => console.error(err));
