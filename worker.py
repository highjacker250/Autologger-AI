import asyncio
import random
import string
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from db import create_task, update_task_status, get_pending_otp

def generate_email():
    return f"pind{random.randint(10000,99999)}@gmail.com"

def generate_password():
    return f"Pind_Wale$${random.randint(1000,9999)}"

async def wait_for_otp(phone, timeout=180):
    for _ in range(timeout):
        otp = get_pending_otp(phone)
        if otp:
            return otp
        await asyncio.sleep(1)
    return None

async def run_automation(platform, phone, range_id):
    email = generate_email()
    password = generate_password()
    
    task_id = create_task(platform, phone, email, password)
    update_task_status(task_id, "starting_browser")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)

        try:
            if platform == "instagram":
                update_task_status(task_id, "loading_instagram")
                await page.goto("https://www.instagram.com/accounts/emailsignup/")
                await page.wait_for_timeout(4000)
                
                update_task_status(task_id, "filling_form")
                await page.fill('input[name="emailOrPhone"]', email)
                await page.fill('input[name="fullName"]', "Pind Wale")
                await page.fill('input[name="username"]', f"pind_{random.randint(1000,9999)}")
                await page.fill('input[name="password"]', password)
                
                await page.click('button[type="submit"]')
                update_task_status(task_id, "waiting_otp")
                
                # Wait for OTP
                otp = await wait_for_otp(phone)
                if otp:
                    update_task_status(task_id, "entering_otp")
                    await page.fill('input[name="email_confirmation_code"]', otp)
                    await page.click('button[type="button"]')
                    await page.wait_for_timeout(5000)
                    
                    update_task_status(task_id, "success", {"cookies": str(await context.cookies())})
                    await browser.close()
                    return True, email, password
                else:
                    raise Exception("OTP Timeout")
            
            elif platform == "facebook":
                update_task_status(task_id, "loading_facebook")
                await page.goto("https://www.facebook.com/r.php")
                await page.wait_for_timeout(3000)
                
                update_task_status(task_id, "filling_form")
                await page.fill('input[name="firstname"]', "Pind")
                await page.fill('input[name="lastname"]', "Wale")
                await page.fill('input[name="reg_email__"]', phone)
                await page.fill('input[name="reg_passwd__"]', password)
                await page.click('button[name="websubmit"]')
                
                update_task_status(task_id, "waiting_otp")
                otp = await wait_for_otp(phone)
                if otp:
                    update_task_status(task_id, "entering_otp")
                    await page.fill('input[name="code"]', otp)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(5000)
                    
                    update_task_status(task_id, "success", {"cookies": str(await context.cookies())})
                    await browser.close()
                    return True, email, password
                else:
                    raise Exception("OTP Timeout")

        except Exception as e:
            update_task_status(task_id, "failed", {"error": str(e)})
            await browser.close()
            return False, email, str(e)
