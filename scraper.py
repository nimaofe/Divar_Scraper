import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_URL = "https://divar.ir"
CATEGORY_URL = f"{BASE_URL}/s/mashhad/services"
AD_COUNT = 4
MAX_RETRIES = 3

class DivarScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.data = []

    def initialize_driver(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 25)

    def wait_for_login(self):
        print("⏳ لطفاً در مرورگر وارد حساب کاربری شوید...")
        self.driver.get(BASE_URL)
        input("✅ پس از ورود، Enter را فشار دهید ")

    def go_to_services(self):
        self.driver.get(CATEGORY_URL)
        print("✅ وارد بخش خدمات شد")
        time.sleep(3)

    def smart_scroll(self):
        """اسکرول تطبیقی با تشخیص المان‌های جدید"""
        last_height = 0
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0

        while len(self.driver.find_elements(By.CSS_SELECTOR, 'div.widget-col-d2306')) < AD_COUNT and scroll_attempts < 15:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_height = new_height

    def collect_ad_links(self):
        try:
            print("🔍 در حال جستجو برای آگهی‌ها...")
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'article.unsafe-kt-post-card')
            ))
            
            self.smart_scroll()
            
            ads = self.driver.find_elements(By.CSS_SELECTOR, 'article.unsafe-kt-post-card')[:AD_COUNT]
            links = [ad.find_element(By.CSS_SELECTOR, 'a.unsafe-kt-post-card__action').get_attribute('href') for ad in ads]
            print(f"✅ {len(links)} لینک آگهی جمع‌آوری شد")
            return links
        except Exception as e:
            print(f"❌ خطا در جمع‌آوری لینک‌ها: {str(e)}")
            return []

    def extract_phone_with_retry(self):
        """استخراج شماره با مکانیزم پیشرفته"""
        for attempt in range(MAX_RETRIES):
            try:
                # تشخیص نوع دکمه تماس
                contact_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[data-testid="contact-button"], button.post-actions__get-contact')
                ))
                self.driver.execute_script("arguments[0].click();", contact_btn)
                
                # انتظار برای لود پاپ‌آپ
                self.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'div.kt-modal--scrollable, div.kt-contact-row')
                ))
                
                # استخراج شماره از نسخه‌های مختلف
                phone_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'a[href^="tel:"]:not([href="tel:"]), div.kt-contact-row a[href^="tel:"]'
                )
                return phone_element.get_attribute('href').replace('tel:', '').strip()
            except (TimeoutException, NoSuchElementException) as e:
                print(f"⚠️ تلاش {attempt+1}/{MAX_RETRIES} برای دریافت شماره ناموفق بود ({str(e)})")
                time.sleep(1.5)
        
        print("❌ دریافت شماره پس از چندین تلاش ناموفق")
        return "یافت نشد"

    def process_ad_page(self, url):
        print(f"\n📌 پردازش آگهی: {url}")
        self.driver.get(url)
        
        try:
            # استخراج عنوان با دو روش مختلف
            try:
                title = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'h1.kt-page-title__title, h1.unsafe-kt-page-title__title')
                )).text.strip()
            except:
                title = self.driver.title.split('|')[0].strip()

            # استخراج موقعیت جغرافیایی
            try:
                location = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'span.unsafe-kt-post-card__bottom-description, span.post-fields-item__value')
                )).text.strip()
            except:
                location = "نامشخص"
            
            # استخراج شماره
            phone = self.extract_phone_with_retry()
            
            # ذخیره اطلاعات
            self.data.append({
                "title": title,
                "phone": phone,
                "location": location,
                "url": url
            })
            print(f"📝 اطلاعات ثبت شد: {title[:30]}... | شماره: {phone} | موقعیت: {location}")
        except Exception as e:
            print(f"❌ خطا در پردازش آگهی: {str(e)}")

    def save_results(self):
        try:
            os.makedirs("result", exist_ok=True)
            file_path = os.path.join("result", "divar_ads.csv")
            
            with open(file_path, "w", encoding="utf-8-sig", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["title", "phone", "location", "url"])
                writer.writeheader()
                writer.writerows(self.data)
            print(f"\n✅ داده‌ها با موفقیت در {file_path} ذخیره شدند")
        except Exception as e:
            print(f"\n❌ خطا در ذخیره فایل: {str(e)}")

    def run(self):
        try:
            self.initialize_driver()
            self.wait_for_login()
            self.go_to_services()
            
            if links := self.collect_ad_links():
                print(f"\n🔗 شروع پردازش {len(links)} آگهی")
                for i, link in enumerate(links, 1):
                    print(f"\n📌 آگهی {i}/{len(links)}")
                    self.process_ad_page(link)
                    time.sleep(1.2)
                
                self.save_results()
            else:
                print("\n❌ هیچ آگهی یافت نشد")
            
        except Exception as e:
            print(f"\n❌ خطای غیرمنتظره: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    scraper = DivarScraper()
    scraper.run()