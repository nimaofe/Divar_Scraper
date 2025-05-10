# -*- coding: utf-8 -*-
import sys
import os
import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# تنظیمات سیستم برای پشتیبانی از UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# تنظیمات لاگ پیشرفته
class UnicodeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            msg = self.format(record).encode('utf-8', 'replace').decode('utf-8')
            self.stream.write(msg + self.terminator)
            self.flush()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('divar_scraper.log', encoding='utf-8'),
        UnicodeStreamHandler()
    ]
)

# تنظیمات اصلی
CONFIG = {
    'output_dir': 'results',
    'phone_number': '09217977178',  # شماره خود را وارد کنید
    'default_city': 'tehran',
    'default_query': 'خودرو',
    'max_wait_time': 30,
    'headless': False  # برای حالت بدون نمایش مرورگر True شود
}

class DivarScraper:
    def __init__(self):
        self.driver = self._init_driver()
        os.makedirs(CONFIG['output_dir'], exist_ok=True)

    def _init_driver(self):
        """تنظیم و راه‌اندازی مرورگر Edge با قابلیت‌های پیشرفته"""
        try:
            options = Options()
            
            # تنظیمات اصلی
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-notifications")
            options.add_argument("--log-level=3")
            
            # بهینه‌سازی‌های امنیتی و عملکردی
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=9222")
            
            if CONFIG['headless']:
                options.add_argument("--headless=new")
            
            # غیرفعال کردن لاگ‌های اضافی
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            service = Service(
                executable_path='msedgedriver.exe',
                service_args=['--silent']
            )
            
            driver = webdriver.Edge(service=service, options=options)
            driver.set_page_load_timeout(CONFIG['max_wait_time'])
            return driver
            
        except Exception as e:
            logging.error(f"خطا در راه‌اندازی مرورگر: {str(e)}")
            raise

    def _manual_login(self):
        """سیستم ورود دستی با راهنمای گام به گام"""
        try:
            logging.info("📲 در حال باز کردن صفحه دیوار...")
            self.driver.get("https://divar.ir")
            time.sleep(3)

            # انتخاب خودکار شهر تهران
            try:
                city_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران')]"))
                )
                city_btn.click()
                time.sleep(2)
                logging.info("✅ شهر تهران انتخاب شد")
            except:
                logging.warning("⚠️ انتخاب شهر انجام نشد (احتمالاً قبلاً انتخاب شده)")

            logging.info("""
            🚨 لطفاً مراحل ورود را به صورت دستی انجام دهید:
            1. روی دکمه 'ورود' کلیک کنید
            2. شماره تلفن را وارد کنید: %s
            3. کد تأیید را دریافت و وارد نمایید
            4. پس از ورود موفق، به این پنجره برگردید
            5. کلید Enter را فشار دهید
            """ % CONFIG['phone_number'])
            
            input("⏳ پس از ورود موفق، Enter را بزنید...")
            return True
            
        except Exception as e:
            logging.error(f"❌ خطا در فرآیند ورود: {str(e)}")
            return False

    def _save_results(self, data):
        """ذخیره هوشمند نتایج با فرمت JSON"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_{timestamp}.json"
            filepath = os.path.join(CONFIG['output_dir'], filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # ذخیره آخرین نتایج به صورت جداگانه
            latest_path = os.path.join(CONFIG['output_dir'], "latest_results.json")
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            logging.info(f"💾 نتایج در {filepath} ذخیره شد")
            return filepath
            
        except Exception as e:
            logging.error(f"❌ خطا در ذخیره نتایج: {str(e)}")
            return None

    def _scrape_data(self):
        """مثال: تابع اصلی استخراج داده"""
        try:
            logging.info("🔍 در حال جمع‌آوری اطلاعات از دیوار...")
            
            # اینجا می‌توانید توابع استخراج خود را اضافه کنید
            sample_data = {
                "metadata": {
                    "project": "Divar Scraper",
                    "version": "2.1",
                    "author": "nimaofe",
                    "timestamp": datetime.now().isoformat()
                },
                "data": [
                    {
                        "title": "نمونه آگهی ۱",
                        "phone": "09123456789",
                        "location": "تهران"
                    },
                    {
                        "title": "نمونه آگهی ۲",
                        "phone": "09381234567",
                        "location": "تهران"
                    }
                ]
            }
            
            return sample_data
            
        except Exception as e:
            logging.error(f"❌ خطا در استخراج داده: {str(e)}")
            return None

    def run(self):
        """مدیریت اصلی فرآیند"""
        try:
            logging.info("🚀 شروع برنامه استخراج اطلاعات از دیوار")
            
            # ورود به سیستم
            if not self._manual_login():
                raise Exception("ورود ناموفق بود")
            
            # استخراج داده
            scraped_data = self._scrape_data()
            if not scraped_data:
                raise Exception("هیچ داده‌ای استخراج نشد")
            
            # ذخیره نتایج
            saved_file = self._save_results(scraped_data)
            if not saved_file:
                raise Exception("خطا در ذخیره نتایج")
            
            logging.info("🎉 عملیات با موفقیت تکمیل شد")
            return True
            
        except Exception as e:
            logging.error(f"🔴 خطای اصلی: {str(e)}")
            return False
            
        finally:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                logging.info("🛑 مرورگر بسته شد")
            input("\nبرای خروج، کلیدی را فشار دهید...")

if __name__ == "__main__":
    scraper = DivarScraper()
    success = scraper.run()
    sys.exit(0 if success else 1)