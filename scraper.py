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
CATEGORY_URL = f"{BASE_URL}/s/tehran/services"
AD_COUNT = 20
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
        time.sleep(3)  # زمان برای لود اولیه

    def smart_scroll(self):
        """اسکرول هوشمند با تشخیص عناصر جدید"""
        last_count = 0
        retries = 0
        
        while retries < 5:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)
            
            # تشخیص آگهی‌های جدید
            current_ads = self.driver.find_elements(By.CSS_SELECTOR, 'a.unsafe-kt-post-card')
            if len(current_ads) > last_count:
                last_count = len(current_ads)
                retries = 0
            else:
                retries += 1
                
            if last_count >= AD_COUNT:
                break

    def collect_ad_links(self):
        try:
            print("🔍 در حال جستجو برای آگهی‌ها...")
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.unsafe-kt-post-card__info')
            ))
            
            self.smart_scroll()
            
            ads = self.driver.find_elements(By.CSS_SELECTOR, 'a.unsafe-kt-post-card')[:AD_COUNT]
            links = [ad.get_attribute('href') for ad in ads if ad.get_attribute('href')]
            print(f"✅ {len(links)} لینک آگهی جمع‌آوری شد")
            return links
        except Exception as e:
            print(f"❌ خطا در جمع‌آوری لینک‌ها: {str(e)}")
            return []

    def extract_phone_with_retry(self):
        """استخراج شماره با مکانیزم تلاش مجدد"""
        for attempt in range(MAX_RETRIES):
            try:
                # کلیک روی دکمه نمایش شماره
                contact_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button.post-actions__get-contact')
                ))
                contact_btn.click()
                
                # انتظار برای لود پاپ‌آپ
                self.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'div.kt-contact-row')
                ))
                
                # استخراج شماره
                phone_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'a[href^="tel:"]'
                )
                return phone_element.get_attribute('href').replace('tel:', '')
            except (TimeoutException, NoSuchElementException):
                print(f"⚠️ تلاش {attempt+1}/{MAX_RETRIES} برای دریافت شماره ناموفق بود")
                time.sleep(1)
        
        print("❌ دریافت شماره پس از چندین تلاش ناموفق")
        return "یافت نشد"

    def process_ad_page(self, url):
        print(f"\n📌 پردازش آگهی: {url}")
        self.driver.get(url)
        
        try:
            # استخراج عنوان
            title = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h1.unsafe-kt-page-title__title')
            )).text.strip()
        except:
            title = "بدون عنوان"
            
        # استخراج شماره
        phone = self.extract_phone_with_retry()
        
        # ذخیره اطلاعات
        self.data.append({
            "title": title,
            "phone": phone,
            "url": url
        })
        print(f"📝 اطلاعات ثبت شد: {title[:30]}... | شماره: {phone}")

    def save_results(self):
        try:
            os.makedirs("result", exist_ok=True)
            file_path = os.path.join("result", "ads.csv")
            
            with open(file_path, "w", encoding="utf-8", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["title", "phone", "url"])
                writer.writeheader()
                writer.writerows(self.data)
            print(f"\n✅ داده‌ها با موفقیت در {file_path} ذخیره شدند")
        except PermissionError:
            print("\n❌ خطا: دسترسی به فایل مجاز نیست. مطمئن شوید فایل قبلی بسته است.")
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
                    time.sleep(1.5)
                
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