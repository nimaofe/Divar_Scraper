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
        """تنظیم مرورگر Edge با قابلیت‌های پیشرفته"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        
        service = Service('msedgedriver.exe')
        driver = webdriver.Edge(service=service, options=options)
        driver.set_page_load_timeout(30)
        return driver

    def _login(self):
        """سیستم ورود پیشرفته با تشخیص خودکار"""
        try:
            logging.info("در حال باز کردن دیوار...")
            self.driver.get("https://divar.ir")
            time.sleep(3)

            # تشخیص و انتخاب خودکار شهر
            try:
                city_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران') or contains(text(),'Tehran')]"))
                )
                city_btn.click()
                time.sleep(2)
                logging.info("شهر تهران انتخاب شد")
            except:
                logging.warning("انتخاب شهر انجام نشد (احتمالاً قبلاً انتخاب شده)")

            # راهنمای ورود دستی
            logging.info("""
            لطفاً مراحل ورود را انجام دهید:
            1. روی دکمه 'ورود' کلیک کنید
            2. شماره تلفن را وارد کنید
            3. کد تأیید را دریافت و وارد نمایید
            """)
            input("پس از ورود موفق، Enter را بزنید...")
            return True
            
        except Exception as e:
            logging.error(f"خطا در فرآیند ورود: {str(e)}")
            return False

    def _scroll_page(self):
        """اسکرول هوشمند صفحه"""
        scroll_pause = 2
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempt = 0
        
        while scroll_attempt < 5:  # حداکثر 5 بار اسکرول
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
            scroll_attempt += 1

    def _extract_ads(self):
        """استخراج آگهی‌ها با سلکتورهای به‌روزرسانی‌شده"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        ads = []
        
        # سلکتورهای سازگار با نسخه جدید دیوار
        for item in soup.select('div.kt-post-card:not(.kt-post-card--outlined)'):
            try:
                title = item.select_one('h2.kt-post-card__title').text.strip()
                link = item.find('a')['href']
                link = f"https://divar.ir{link}" if not link.startswith('http') else link
                
                ads.append({
                    'title': title,
                    'link': link,
                    'scraped_at': datetime.now().isoformat()
                })
            except Exception as e:
                logging.warning(f"خطا در پردازش آگهی: {str(e)}")
                continue
        
        logging.info(f"تعداد {len(ads)} آگهی پیدا شد")
        return ads

    def _get_phone_number(self, url):
        """استخراج شماره با مدیریت خطاهای پیشرفته"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # کلیک روی دکمه نمایش تماس
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.post-actions__get-contact"))
            ).click()
            time.sleep(2)
            
            # استخراج شماره با چند روش مختلف
            phone = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "a[href^='tel:'], .contact-reveal-card__phone-number"))
            ).text.strip()
            
            return phone
            
        except Exception as e:
            logging.warning(f"خطا در استخراج شماره: {str(e)}")
            return None

    def scrape(self, query="خودرو", city="tehran", max_ads=15):
        """فرآیند اصلی استخراج"""
        try:
            if not self._login():
                return False

            # جستجو
            search_url = f"https://divar.ir/s/{city}?q={query}"
            self.driver.get(search_url)
            time.sleep(3)
            
            # اسکرول و استخراج
            self._scroll_page()
            ads = self._extract_ads()[:max_ads]
            
            if not ads:
                logging.error("هیچ آگهی یافت نشد!")
                return False
            
            # استخراج شماره‌ها
            for ad in ads:
                ad['phone'] = self._get_phone_number(ad['link'])
                self.results.append(ad)
                logging.info(f"استخراج شد: {ad['title']} - {ad.get('phone', 'بدون شماره')}")
                time.sleep(1.5)  # فاصله ایمن
            
            return True
            
        except Exception as e:
            logging.error(f"خطای استخراج: {str(e)}")
            return False

    def save_results(self):
        """ذخیره نتایج با فرمت JSON"""
        try:
            if not self.results:
                logging.warning("هیچ نتیجه‌ای برای ذخیره وجود ندارد")
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/divar_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
            
            logging.info(f"نتایج در {filename} ذخیره شد")
            return True
            
        except Exception as e:
            logging.error(f"خطا در ذخیره نتایج: {str(e)}")
            return False

if __name__ == "__main__":
    scraper = DivarScraper()
    if scraper.scrape(query="خودرو", max_ads=10):  # تست با 10 آگهی
        scraper.save_results()
    input("برای خروج Enter بزنید...")