import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEBUG_FOLDER = "debug_info"

class DivarDebugger:
    def __init__(self):
        self.driver = None
        
    def start(self):
        try:
            # ایجاد پوشه دیباگ
            os.makedirs(DEBUG_FOLDER, exist_ok=True)
            
            # تنظیمات مرورگر
            options = Options()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0")
            
            self.driver = webdriver.Edge(options=options)
            self.driver.maximize_window()
            
            # ورود دستی
            print("⏳ لطفاً مراحل زیر را انجام دهید:")
            print("1. وارد سایت divar.ir شوید")
            print("2. به بخش خدمات بروید")
            print("3. صفحه را تا انتها اسکرول کنید")
            print("4. وقتی آماده بودید Enter را بزنید")
            input("✅ پس از انجام مراحل، Enter را فشار دهید ")
            
            # جمع‌آوری اطلاعات
            self.save_page_info()
            print(f"\n✅ اطلاعات دیباگ در پوشه {DEBUG_FOLDER} ذخیره شد")
            
        finally:
            if self.driver:
                self.driver.quit()

    def save_page_info(self):
        """ذخیره اطلاعات مهم صفحه"""
        # ذخیره HTML کامل
        with open(f"{DEBUG_FOLDER}/full_page.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
            
        # ذخیره عناصر آگهی
        ads = self.driver.find_elements(By.CSS_SELECTOR, 'div.post-card-item, div.unsafe-kt-post-card, [data-testid="post-card"]')
        with open(f"{DEBUG_FOLDER}/ad_elements.txt", "w", encoding="utf-8") as f:
            for i, ad in enumerate(ads, 1):
                f.write(f"=== آگهی شماره {i} ===\n")
                f.write(f"عنوان: {ad.text}\n")
                f.write(f"Outer HTML:\n{ad.get_attribute('outerHTML')}\n\n")
                
        # ذخیره اسکرینشات
        self.driver.save_screenshot(f"{DEBUG_FOLDER}/page_screenshot.png")

if __name__ == "__main__":
    debugger = DivarDebugger()
    debugger.start()