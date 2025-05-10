# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os
import json
import logging

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('divar_scraper.log'),
        logging.StreamHandler()
    ]
)

# تنظیمات پایه
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class DivarScraper:
    def __init__(self):
        self.driver = self._init_driver()
        self.phone_number = "09217977178"  # شماره خود را وارد کنید

    def _init_driver(self):
        """تنظیم و راه‌اندازی مرورگر Edge"""
        try:
            options = Options()
            
            # تنظیمات ضروری
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-notifications")
            
            # بهینه‌سازی عملکرد
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # غیرفعال کردن لاگ‌های اضافی
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            service = Service(
                executable_path='msedgedriver.exe',
                service_args=['--silent']
            )
            
            driver = webdriver.Edge(service=service, options=options)
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            logging.error(f"خطا در راه‌اندازی مرورگر: {str(e)}")
            raise

    def _manual_login(self):
        """ورود دستی به دیوار"""
        try:
            logging.info("در حال باز کردن صفحه دیوار...")
            self.driver.get("https://divar.ir")
            time.sleep(3)

            # انتخاب شهر تهران (اگر نیاز باشد)
            try:
                city_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران')]"))
                )
                city_btn.click()
                time.sleep(2)
            except:
                logging.warning("انتخاب شهر انجام نشد (احتمالاً قبلاً انتخاب شده)")

            logging.info("""
            لطفاً مراحل ورود را به صورت دستی انجام دهید:
            1. روی دکمه 'ورود' کلیک کنید
            2. شماره تلفن را وارد کنید
            3. کد تأیید را دریافت و وارد نمایید
            4. پس از ورود موفق، این پنجره را نبندید
            5. در اینجا کلید Enter را فشار دهید
            """)
            
            input("پس از ورود موفق، Enter را بزنید...")
            return True
            
        except Exception as e:
            logging.error(f"خطا در فرآیند ورود دستی: {str(e)}")
            return False

    def _save_results(self, data, filename_prefix="results"):
        """ذخیره نتایج در فایل JSON"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # ذخیره آخرین نتایج
            latest_file = os.path.join(OUTPUT_DIR, "latest_results.json")
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logging.info(f"نتایج با موفقیت در {filepath} ذخیره شد")
            
        except Exception as e:
            logging.error(f"خطا در ذخیره نتایج: {str(e)}")

    def run(self):
        """اجرای اصلی برنامه"""
        try:
            logging.info("شروع فرآیند استخراج اطلاعات از دیوار")
            
            # ورود به سیستم
            if not self._manual_login():
                logging.error("ورود ناموفق بود. برنامه متوقف شد.")
                return

            # جستجو و استخراج اطلاعات
            logging.info("در حال جستجو در دیوار...")
            # اینجا می‌توانید توابع استخراج خود را اضافه کنید
            
            # نمونه داده برای تست
            sample_data = {
                "status": "success",
                "message": "این یک نمونه خروجی است",
                "data": [
                    {"title": "آگهی نمونه 1", "phone": "09123456789"},
                    {"title": "آگهی نمونه 2", "phone": "09381234567"}
                ]
            }
            
            self._save_results(sample_data)
            
        except Exception as e:
            logging.error(f"خطای غیرمنتظره: {str(e)}", exc_info=True)
            
        finally:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                logging.info("مرورگر بسته شد")
            input("برای خروج از برنامه، کلیدی را فشار دهید...")

if __name__ == "__main__":
    scraper = DivarScraper()
    scraper.run()