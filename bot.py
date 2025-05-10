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
from bs4 import BeautifulSoup

# تنظیمات سیستم
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('divar_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# تنظیمات اصلی
CONFIG = {
    'output_dir': 'results',
    'phone_number': '09217977178',
    'default_city': 'tehran',
    'default_query': 'خودرو',
    'max_results': 50,  # حداکثر تعداد نتایج
    'scroll_pause': 2,  # زمان توقف بین اسکرول (ثانیه)
    'headless': False
}

class RealTimeDivarScraper:
    def __init__(self):
        self.driver = self._init_driver()
        os.makedirs(CONFIG['output_dir'], exist_ok=True)
        self.scraped_data = []

    def _init_driver(self):
        """تنظیم مرورگر با قابلیت‌های پیشرفته"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        if CONFIG['headless']:
            options.add_argument("--headless=new")
        
        service = Service('msedgedriver.exe')
        return webdriver.Edge(service=service, options=options)

    def _manual_login(self):
        """ورود دستی به دیوار"""
        try:
            self.driver.get("https://divar.ir")
            time.sleep(3)

            # انتخاب شهر
            try:
                city_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران')]"))
                )
                city_btn.click()
                time.sleep(2)
            except:
                pass

            print("\nلطفاً مراحل ورود را انجام دهید:")
            print("1. روی دکمه ورود کلیک کنید")
            print(f"2. شماره {CONFIG['phone_number']} را وارد کنید")
            print("3. کد تأیید را دریافت و وارد نمایید")
            input("پس از ورود موفق، Enter را بزنید...")
            return True
            
        except Exception as e:
            logging.error(f"خطا در ورود: {str(e)}")
            return False

    def _scroll_to_bottom(self):
        """اسکرول صفحه تا انتها برای بارگذاری تمام آگهی‌ها"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(CONFIG['scroll_pause'])
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _extract_advertisements(self):
        """استخراج آگهی‌های واقعی از صفحه"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        ads = []
        
        for item in soup.find_all('div', class_='post-card-item')[1:-1]:
            try:
                title = item.find('h2', class_='post-card-title').text.strip()
                link = item.find('a')['href']
                if not link.startswith('http'):
                    link = f"https://divar.ir{link}"
                
                ads.append({
                    'title': title,
                    'link': link,
                    'timestamp': datetime.now().isoformat()
                })
                
                if len(ads) >= CONFIG['max_results']:
                    break
                    
            except Exception as e:
                logging.warning(f"خطا در پردازش آگهی: {str(e)}")
                continue
        
        return ads

    def _get_phone_number(self, ad_url):
        """استخراج شماره تلفن از یک آگهی"""
        try:
            self.driver.get(ad_url)
            time.sleep(2)
            
            # کلیک روی دکمه نمایش تماس
            contact_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".post-actions__get-contact"))
            )
            contact_btn.click()
            time.sleep(2)
            
            # استخراج شماره
            phone_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='tel:']"))
            )
            return phone_element.text
            
        except Exception as e:
            logging.warning(f"خطا در استخراج شماره: {str(e)}")
            return None

    def _scrape_real_time_data(self):
        """استخراج داده‌های واقعی از دیوار"""
        try:
            # ساخت URL جستجو
            search_url = f"https://divar.ir/s/{CONFIG['default_city']}?q={CONFIG['default_query']}"
            self.driver.get(search_url)
            time.sleep(3)
            
            # اسکرول برای بارگذاری تمام آگهی‌ها
            self._scroll_to_bottom()
            
            # استخراج لیست آگهی‌ها
            ads = self._extract_advertisements()
            
            # استخراج شماره تلفن‌ها
            for ad in ads:
                ad['phone'] = self._get_phone_number(ad['link'])
                time.sleep(1)  # فاصله بین درخواست‌ها
                
                # نمایش لحظه‌ای نتایج
                print(f"\n📌 آگهی جدید:")
                print(f"عنوان: {ad['title']}")
                print(f"شماره: {ad.get('phone', 'یافت نشد')}")
                print(f"لینک: {ad['link']}")
                
                self.scraped_data.append(ad)
            
            return True
            
        except Exception as e:
            logging.error(f"خطا در استخراج داده: {str(e)}")
            return False

    def _save_results(self):
        """ذخیره نتایج با فرمت JSON"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"divar_results_{timestamp}.json"
            filepath = os.path.join(CONFIG['output_dir'], filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, ensure_ascii=False, indent=4)
            
            logging.info(f"نتایج در {filepath} ذخیره شد")
            return filepath
            
        except Exception as e:
            logging.error(f"خطا در ذخیره نتایج: {str(e)}")
            return None

    def run(self):
        """اجرای اصلی برنامه"""
        try:
            logging.info("شروع استخراج اطلاعات از دیوار")
            
            if not self._manual_login():
                raise Exception("ورود ناموفق بود")
            
            if not self._scrape_real_time_data():
                raise Exception("خطا در استخراج داده")
            
            self._save_results()
            logging.info("عملیات با موفقیت انجام شد")
            return True
            
        except Exception as e:
            logging.error(f"خطای اصلی: {str(e)}")
            return False
            
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()
                logging.info("مرورگر بسته شد")
            input("\nبرای خروج، کلیدی را فشار دهید...")

if __name__ == "__main__":
    scraper = RealTimeDivarScraper()
    sys.exit(0 if scraper.run() else 1)