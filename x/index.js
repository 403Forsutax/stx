const { Telegraf } = require('telegraf');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Daftar Bot: token + admin
const BOTS = [
  {
    token: 'ISI_TOKEN_BOT1',
    admins: [7382759396, 1234567890]
  },
  {
    token: 'ISI_TOKEN_BOT2',
    admins: [9876543210]
  }
  // Tambahkan bot lain di sini
];

let bots = [];

BOTS.forEach(({ token, admins }) => {
  const bot = new Telegraf(token);

  let currentDir = os.homedir();

  bot.on('text', async (ctx) => {
    const userId = ctx.from.id;
    if (!admins.includes(userId)) {
      return ctx.reply('Kamu siapa?');
    }

    const command = ctx.message.text.trim();

    if (command.startsWith('cd ')) {
      const targetPath = command.slice(3).trim();
      const newDir = path.resolve(currentDir, targetPath);
      if (fs.existsSync(newDir) && fs.lstatSync(newDir).isDirectory()) {
        currentDir = newDir;
        return ctx.reply(`cd ${currentDir}`);
      } else {
        return ctx.reply(`No such directory: ${newDir}`);
      }
    }

    exec(command, { cwd: currentDir, timeout: 600000 }, (error, stdout, stderr) => {
      let output = \`\${stdout}
\${stderr}\`.trim();
      if (error && !output) {
        output = \`Error: \${error.message}\`;
      } else if (!output) {
        output = 'root@xixixi:~#';
      }

      const chunks = output.match(/[\s\S]{1,4000}/g) || [];
      chunks.forEach(chunk => ctx.reply(chunk));
    });
  });

  bot.launch().then(() => console.log(\`Bot running with token ending in \${token.slice(-8)}\`));
  bots.push(bot);
});

process.once('SIGINT', () => bots.forEach(bot => bot.stop('SIGINT')));
process.once('SIGTERM', () => bots.forEach(bot => bot.stop('SIGTERM')));