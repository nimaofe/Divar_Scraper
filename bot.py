# -*- coding: utf-8 -*-
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

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('divar_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class DivarScraper:
    def __init__(self):
        self.driver = self._init_driver()
        self.results = []
        os.makedirs('results', exist_ok=True)

    def _init_driver(self):
        """تنظیم مرورگر Edge"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        
        service = Service('msedgedriver.exe')
        return webdriver.Edge(service=service, options=options)

    def _login(self):
        """ورود به دیوار"""
        try:
            self.driver.get("https://divar.ir")
            time.sleep(3)

            # انتخاب شهر تهران
            try:
                city_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران')]"))
                )
                city_btn.click()
                time.sleep(2)
            except:
                logging.warning("انتخاب شهر انجام نشد")

            # ورود دستی
            print("\nلطفاً مراحل ورود را انجام دهید:")
            print("1. روی دکمه ورود کلیک کنید")
            print("2. شماره تلفن را وارد کنید")
            print("3. کد تأیید را دریافت و وارد نمایید")
            input("پس از ورود موفق، Enter را بزنید...")
            return True
            
        except Exception as e:
            logging.error(f"خطا در ورود: {str(e)}")
            return False

    def _scroll_page(self):
        """اسکرول صفحه برای بارگذاری تمام آگهی‌ها"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _extract_ads(self):
        """استخراج آگهی‌ها از صفحه"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        ads = []
        
        for item in soup.find_all('div', class_='post-card-item')[1:-1]:  # حذف آیتم‌های غیرمرتبط
            try:
                title = item.find('h2', class_='post-card-title').text.strip()
                link = item.find('a')['href']
                if not link.startswith('http'):
                    link = f"https://divar.ir{link}"
                
                ads.append({
                    'title': title,
                    'link': link,
                    'scraped_at': datetime.now().isoformat()
                })
            except Exception as e:
                logging.warning(f"خطا در پردازش آگهی: {str(e)}")
        
        return ads

    def _get_phone_number(self, url):
        """استخراج شماره تلفن از آگهی"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # کلیک روی دکمه نمایش تماس
            contact_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".post-actions__get-contact"))
            )
            contact_btn.click()
            time.sleep(2)
            
            # استخراج شماره
            phone = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='tel:']"))
            ).text
            
            return phone
        except Exception as e:
            logging.warning(f"خطا در استخراج شماره: {str(e)}")
            return None

    def scrape(self, query="خدمات", city="tehran", max_ads=20):
        """استخراج اطلاعات از دیوار"""
        try:
            if not self._login():
                return False

            # جستجو
            search_url = f"https://divar.ir/s/{city}?q={query}"
            self.driver.get(search_url)
            time.sleep(3)
            
            # اسکرول و استخراج
            self._scroll_page()
            ads = self._extract_ads()[:max_ads]  # محدودیت تعداد آگهی‌ها
            
            # استخراج شماره تلفن‌ها
            for ad in ads:
                ad['phone'] = self._get_phone_number(ad['link'])
                self.results.append(ad)
                logging.info(f"استخراج شد: {ad['title']} - {ad.get('phone', 'بدون شماره')}")
                time.sleep(1)  # فاصله بین درخواست‌ها
            
            return True
            
        except Exception as e:
            logging.error(f"خطا در استخراج: {str(e)}")
            return False

    def save_results(self):
        """ذخیره نتایج"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/divar_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
            
            logging.info(f"نتایج در {filename} ذخیره شد")
            return filename
        except Exception as e:
            logging.error(f"خطا در ذخیره نتایج: {str(e)}")
            return None

if __name__ == "__main__":
    scraper = DivarScraper()
    if scraper.scrape(query="خودرو", max_ads=10):  # تست با 10 آگهی
        scraper.save_results()
    input("برای خروج Enter بزنید...")