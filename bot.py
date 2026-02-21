import os
import asyncio
import importlib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from playwright.async_api import async_playwright

# Import the accounts from your separate accounts.py file
import accounts

# --- CONFIGURATION ---
# Replace the string below with your actual Bot Token
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
SECURITY_URL = "https://console.byteplus.com/user/security/"

async def run_instance(update: Update, username, password, inst_name):
    async with async_playwright() as p:
        # Args optimized for server stability
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={'width': 1600, 'height': 1000})
        page = await context.new_page()
        
        try:
            # --- STEP 1: LOGIN ---
            await update.message.reply_text(f"🔑 [{inst_name}] Starting login for: {username}")
            await page.goto("https://console.byteplus.com/auth/login/", wait_until="networkidle")
            await page.locator('input:visible').nth(0).fill(username)
            await page.locator('input[type="password"]:visible').last.fill(password)
            await page.locator('button:has-text("Sign in")').first.evaluate("n => n.click()")
            await page.wait_for_url("**/console**", timeout=30000)
            
            # Dashboard Screenshot
            path_dash = f"dash_{inst_name}.png"
            await page.screenshot(path=path_dash)
            await update.message.reply_photo(photo=open(path_dash, "rb"), caption=f"1️⃣ [{inst_name}] Dashboard")
            os.remove(path_dash)

            # --- STEP 2: SECURITY PAGE ---
            await page.goto(SECURITY_URL, wait_until="networkidle")
            await page.add_style_tag(content="#cookiebanner, .arco-modal-container { display: none !important; }")
            await asyncio.sleep(5)
            
            path_sec = f"sec_{inst_name}.png"
            await page.screenshot(path=path_sec)
            await update.message.reply_photo(photo=open(path_sec, "rb"), caption=f"2️⃣ [{inst_name}] Security Page")
            os.remove(path_sec)

            # --- STEP 3: OPEN POPUP ---
            # Locating the toggle for "Sensitive actions protection"
            toggle = page.locator('button[role="switch"]').filter(has=page.locator('xpath=../..//*[text()="Sensitive actions protection"]')).first
            if await toggle.count() == 0:
                toggle = page.locator('.arco-switch').last

            await toggle.evaluate("n => n.click()")
            await asyncio.sleep(3)
            
            path_pop = f"popup_{inst_name}.png"
            await page.screenshot(path=path_pop)
            await update.message.reply_photo(photo=open(path_pop, "rb"), caption=f"3️⃣ [{inst_name}] Popup Open (Timer Started)")
            os.remove(path_pop)

            # --- STEP 4: 2-MINUTE RESEND LOOP ---
            count = 1
            while True:
                # Wait total 2 minutes (120 seconds) per cycle
                await asyncio.sleep(120) 
                
                resend_btn = page.locator('span:has-text("Resend code"), button:has-text("Resend")').first
                await resend_btn.evaluate("n => n.click()")
                
                path_loop = f"loop_{inst_name}_{count}.png"
                await page.screenshot(path=path_loop)
                await update.message.reply_photo(
                    photo=open(path_loop, "rb"), 
                    caption=f"🔄 [{inst_name}] Resend #{count} (2-min interval)"
                )
                os.remove(path_loop)
                count += 1

        except Exception as e:
            await update.message.reply_text(f"❌ [{inst_name}] Error: {str(e)[:100]}")
        finally:
            await browser.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reload accounts.py to catch any updates in the file
    importlib.reload(accounts)
    acc_list = accounts.ACCOUNTS
    
    await update.message.reply_text(f"🚀 Detected {len(acc_list)} accounts. Starting with 30s gaps...")
    
    # Dynamic Loop: Starts every account found in accounts.py
    for i, acc in enumerate(acc_list):
        inst_label = f"Inst_{i+1}"
        asyncio.create_task(run_instance(update, acc["user"], acc["pass"], inst_label))
        
        # Staggered start: 30-second delay between each new instance
        if i < len(acc_list) - 1:
            await asyncio.sleep(30)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function allows you to upload a new accounts.py file to the bot
    if update.message.document.file_name == "accounts.py":
        file = await update.message.document.get_file()
        await file.download_to_drive("accounts.py")
        importlib.reload(accounts)
        await update.message.reply_text("✅ `accounts.py` updated successfully! Use /start to run with new list.")

def main():
    # Build the application using the hardcoded BOT_TOKEN
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("🚀 Bot running without .env file...")
    app.run_polling()

if __name__ == "__main__":
    main()
