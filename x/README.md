# Telegram MultiBot Terminal

Bot Telegram multi-token untuk kontrol terminal VPS/Linux.

## Installasi

```bash
npm install
npm start
```

## Tambah Bot

Edit array `BOTS` di `index.js`:

```javascript
{
  token: 'TOKEN_BOT',
  admins: [ID_ADMIN1, ID_ADMIN2]
}
```

## Auto Booting VPS (Systemd Setup)

1. Copy `telegram-bot.service` ke `/etc/systemd/system/`:

```bash
sudo cp telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
```

2. Enable dan start:

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

3. Cek status bot:

```bash
sudo systemctl status telegram-bot
```

Kalau mau pakai **PM2**:

```bash
pm2 start index.js --name telegram-multibot
pm2 save
pm2 startup
```

Ikuti instruksi `pm2 startup` untuk autostart.