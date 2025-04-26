const { Telegraf } = require('telegraf');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const BOT_TOKEN = '8167886725:AAGCIY2tLSn5Fx6V-hDVn3Ft_xMRhhKkOYk';
const ALLOWED_USER_ID = 7382759396;

const bot = new Telegraf(BOT_TOKEN);

let currentDir = os.homedir();

bot.on('text', async (ctx) => {
  const userId = ctx.from.id;
  if (userId !== ALLOWED_USER_ID) {
    return ctx.reply('Kamu siapa?');
  }

  const command = ctx.message.text.trim();

  // Tangani perintah 'cd'
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
    let output = `${stdout}
${stderr}`.trim();
    if (error && !output) {
      output = `Error: ${error.message}`;
    } else if (!output) {
      output = 'root@xixixi:~#';
    }

    const chunks = output.match(/[\s\S]{1,4000}/g) || [];
    chunks.forEach(chunk => ctx.reply(chunk));
  });
});

bot.launch().then(() => console.log('Bot running...'));