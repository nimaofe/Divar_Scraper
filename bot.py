# -*- coding: utf-8 -*-
import os
import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        service = Service('msedgedriver.exe')
        return webdriver.Edge(service=service, options=options)

    def _login(self):
        """ورود به دیوار"""
        try:
            self.driver.get("https://divar.ir")
            time.sleep(3)

            # انتخاب شهر
            try:
                city_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران')]"))
                )
                city_btn.click()
                time.sleep(2)
            except:
                logging.warning("انتخاب شهر انجام نشد")

            print("\nلطفاً مراحل ورود را انجام دهید:")
            print("1. روی دکمه ورود کلیک کنید")
            print("2. شماره تلفن را وارد کنید")
            print("3. کد تأیید را دریافت و وارد نمایید")
            input("پس از ورود موفق، Enter را بزنید...")
            return True
            
        except Exception as e:
            logging.error(f"خطا در ورود: {str(e)}")
            return False

    def _scrape_ads(self, query="خودرو", max_ads=10):
        """استخراج آگهی‌ها"""
        try:
            search_url = f"https://divar.ir/s/tehran?q={query}"
            self.driver.get(search_url)
            time.sleep(3)

            # اسکرول صفحه
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while len(self.results) < max_ads:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

                # استخراج آگهی‌ها
                ads = self.driver.find_elements(By.CSS_SELECTOR, 'div.kt-post-card')
                for ad in ads[len(self.results):max_ads]:
                    try:
                        title = ad.find_element(By.CSS_SELECTOR, 'h2.kt-post-card__title').text
                        link = ad.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        self.results.append({'title': title, 'link': link})
                    except:
                        continue

            return True
            
        except Exception as e:
            logging.error(f"خطا در استخراج آگهی‌ها: {str(e)}")
            return False

    def _get_phones(self):
        """استخراج شماره تلفن‌ها"""
        for ad in self.results:
            try:
                self.driver.get(ad['link'])
                time.sleep(2)
                
                contact_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.post-actions__get-contact"))
                )
                contact_btn.click()
                time.sleep(2)
                
                phone = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='tel:']"))
                ).text
                ad['phone'] = phone
                
            except Exception as e:
                ad['phone'] = None
                logging.warning(f"خطا در استخراج شماره: {str(e)}")

    def run(self):
        """اجرای اصلی"""
        try:
            if not self._login():
                return False

            if not self._scrape_ads():
                return False

            self._get_phones()
            
            # ذخیره نتایج
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/results_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            logging.info(f"نتایج در {filename} ذخیره شد")
            return True
            
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = DivarScraper()
    scraper.run()
    input("برای خروج Enter بزنید...")