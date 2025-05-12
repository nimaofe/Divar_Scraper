import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://divar.ir"
CATEGORY_URL = f"{BASE_URL}/s/tehran/services"
AD_COUNT = 20

class DivarScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.data = []

    def initialize_driver(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 30)

    def wait_for_login(self):
        print("⏳ لطفاً در مرورگر وارد حساب کاربری شوید...")
        self.driver.get(BASE_URL)
        input("✅ پس از ورود، Enter را فشار دهید ")

    def go_to_services(self):
        self.driver.get(CATEGORY_URL)
        print("✅ وارد بخش خدمات شد")

    def load_all_ads(self):
        """اسکرول صفحه برای لود تمام آگهی‌ها"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def collect_ad_links(self):
        try:
            # استفاده از سلکتور صحیح برای آگهی‌ها
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.post-card-item')
            ))
            
            # اسکرول برای لود تمام آگهی‌ها
            self.load_all_ads()
            
            ads = self.driver.find_elements(By.CSS_SELECTOR, 'a.kt-post-card')[:AD_COUNT]
            return [ad.get_attribute('href') for ad in ads if ad.get_attribute('href')]
        except Exception as e:
            print(f"خطا در جمع‌آوری لینک‌ها: {e}")
            return []

    def extract_phone_number(self):
        try:
            contact_btn = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button.post-actions__get-contact')
            ))
            contact_btn.click()
            
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.kt-contact-row')
            ))
            
            phone_element = self.driver.find_element(
                By.CSS_SELECTOR, 
                'a[href^="tel:"]'
            )
            return phone_element.get_attribute('href').replace('tel:', '')
        except Exception as e:
            print(f"خطا در استخراج شماره: {e}")
            return "یافت نشد"

    def process_ad_page(self, url):
        self.driver.get(url)
        try:
            title = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h1.kt-page-title__title')
            )).text.strip()
        except:
            title = "بدون عنوان"
            
        phone = self.extract_phone_number()
        
        self.data.append({
            "title": title,
            "phone": phone,
            "url": url
        })
        print(f"✅ اطلاعات ذخیره شد: {title}")

    def save_results(self):
        os.makedirs("result", exist_ok=True)
        with open("result/ads.csv", "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["title", "phone", "url"])
            writer.writeheader()
            writer.writerows(self.data)
        print("✅ داده‌ها ذخیره شدند")

    def run(self):
        try:
            self.initialize_driver()
            self.wait_for_login()
            self.go_to_services()
            
            links = self.collect_ad_links()
            print(f"🔎 تعداد {len(links)} آگهی پیدا شد")
            
            for i, link in enumerate(links, 1):
                print(f"پردازش آگهی {i}/{len(links)}...")
                self.process_ad_page(link)
                time.sleep(1)
            
            self.save_results()
            
        except Exception as e:
            print(f"❌ خطا: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    scraper = DivarScraper()
    scraper.run()