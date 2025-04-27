import os
import sys
import json
import subprocess
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === CONFIG ===

BOT_TOKEN = '7361661359:AAGI9A56aal_GQBjlxpK7jHoL2lTg_0rYaM'
ADMINS = {5193826370}
USER_DATA_FILE = 'users.json'

# === SETUP ===

def load_allowed_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('allowed_users', []))
    return set()

def save_allowed_users():
    data = {"allowed_users": list(ALLOWED_USERS)}
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

ALLOWED_USERS = load_allowed_users()
current_dir = os.path.expanduser("~")

# === HANDLERS ===

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_dir
    try:
        user_id = update.effective_user.id
        message_text = update.message.text.strip()

        # === ADMIN MODE ===
        if user_id in ADMINS:
            if message_text == "ls":
                try:
                    files = os.listdir(current_dir)
                    output = "\n".join(files) or "(Empty Directory)"
                    await update.message.reply_text(f"**Current Directory:**\n`{current_dir}`\n\n{output}", parse_mode='Markdown')
                except Exception as e:
                    await update.message.reply_text(f"Error listing directory: {str(e)}")
                return

            if message_text.startswith("cd "):
                target_dir = message_text[3:].strip()
                new_path = os.path.abspath(os.path.join(current_dir, target_dir))
                if os.path.isdir(new_path):
                    current_dir = new_path
                    await update.message.reply_text(f"Changed directory to:\n`{current_dir}`", parse_mode='Markdown')
                else:
                    await update.message.reply_text(f"Directory not found: {target_dir}")
                return

            if message_text.startswith("./") or message_text.startswith("."):
                command = message_text[1:].strip() if message_text.startswith(". ") else message_text

                await update.message.reply_text(f"Executing:\n`{command}`", parse_mode='Markdown')

                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=current_dir,
                        timeout=600
                    )
                    output = result.stdout.strip() + "\n" + result.stderr.strip()
                    output = output.strip()

                    if "password" in output.lower():
                        await update.message.reply_text("[!] Waiting for password input (manual via VPS).")

                    if not output:
                        output = "(No output)"

                    for i in range(0, len(output), 4000):
                        await update.message.reply_text(output[i:i+4000])

                except subprocess.TimeoutExpired:
                    await update.message.reply_text("Error: Command timeout after 600 seconds.")
                except Exception as e:
                    await update.message.reply_text(f"Error: {str(e)}")
                return

        # === USER MODE (./stx IP PORT DURASI THREAD stx) ===
        if user_id not in ADMINS and user_id not in ALLOWED_USERS:
            await update.message.reply_text("Unauthorized access.")
            return

        args = message_text.split()

        if len(args) != 6:
            await update.message.reply_text("Invalid format. Correct usage:\n./stx IP PORT DURATION THREAD stx")
            return

        prefix, ip, port, duration, thread, suffix = args

        if prefix != "./stx":
            await update.message.reply_text("Message must start with './stx'.")
            return
        if suffix.lower() != "stx":
            await update.message.reply_text("Message must end with 'stx'.")
            return
        if not port.isdigit() or not duration.isdigit() or not thread.isdigit():
            await update.message.reply_text("PORT, DURATION, and THREAD must be numeric.")
            return

        command = f"echo Target IP: {ip}, Port: {port}, Duration: {duration}s, Threads: {thread}"

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=current_dir,
            timeout=600
        )
        output = result.stdout.strip() + "\n" + result.stderr.strip()
        output = output.strip()

        if not output:
            output = "(No output)"

        for i in range(0, len(output), 4000):
            await update.message.reply_text(output[i:i+4000])

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# === ADMIN COMMANDS ===

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMINS:
            await update.message.reply_text("Only admins can use this command.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /adduser <user_id>")
            return

        new_user = int(context.args[0])
        if new_user in ALLOWED_USERS:
            await update.message.reply_text(f"User {new_user} already allowed.")
        else:
            ALLOWED_USERS.add(new_user)
            save_allowed_users()
            await update.message.reply_text(f"User {new_user} added to allowed users.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def del_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMINS:
            await update.message.reply_text("Only admins can use this command.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /deluser <user_id>")
            return

        del_user = int(context.args[0])
        if del_user in ALLOWED_USERS:
            ALLOWED_USERS.remove(del_user)
            save_allowed_users()
            await update.message.reply_text(f"User {del_user} removed from allowed users.")
        else:
            await update.message.reply_text("User not found.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMINS:
            await update.message.reply_text("Only admins can use this command.")
            return

        text = "**Allowed Users:**\n"
        if ALLOWED_USERS:
            text += "\n".join(str(uid) for uid in ALLOWED_USERS)
        else:
            text += "(none)"
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMINS:
            await update.message.reply_text("Only admins can restart the bot.")
            return

        await update.message.reply_text("Restarting bot...")
        await asyncio.sleep(2)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = (
            "**Command List:**\n\n"
            "**Admin:**\n"
            "`/adduser <id>` - Add allowed user\n"
            "`/deluser <id>` - Delete allowed user\n"
            "`/listuser` - List allowed users\n"
            "`/restartbot` - Restart bot\n"
            "`ls`, `cd <dir>`, `./file`, `.command` - Terminal access\n\n"
            "**User:**\n"
            "`./stx IP PORT DURASI THREAD stx` format"
        )
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# === BOT RUN ===

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("adduser", add_user))
app.add_handler(CommandHandler("deluser", del_user))
app.add_handler(CommandHandler("listuser", list_users))
app.add_handler(CommandHandler("restartbot", restart_bot))
app.add_handler(CommandHandler("bantuan", bantuan))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_command))

if __name__ == '__main__':
    print("Bot running...")
    try:
        app.run_polling(allowed_updates=["message", "edited_message"])
    except Exception as e:
        print(f"Polling Error: {str(e)}")
        asyncio.run(app.run_polling(allowed_updates=["message", "edited_message"]))
