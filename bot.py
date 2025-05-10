from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from Divar_Scraping import login_divar, get_phone_numbers, divar_search
import time
import os

# تنظیمات
output_path = "Results"
os.makedirs(output_path, exist_ok=True)

def main():
    # تنظیمات Edge
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    service = Service('msedgedriver.exe')
    driver = webdriver.Edge(service=service, options=options)
    
    try:
        # ورود به دیوار
        if not login_divar(driver, "09217977178"):
            print("❌ ورود ناموفق بود! لطفاً:")
            print("- شماره را بررسی کنید")
            print("- اینترنت را چک کنید")
            print("- دستی وارد شوید")
            input("کلید Enter برای خروج...")
            return

        # عملیات استخراج
        print("✅ ورود موفق! در حال جستجو...")
        urls = divar_search(driver, "خودرو", "tehran")
        if urls:
            phones = get_phone_numbers(driver, urls)
            if phones:
                with open(f"{output_path}/phones.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(phones))
                print(f"📊 {len(phones)} شماره ذخیره شد")
        
    finally:
        driver.quit()
        print("🛑 مرورگر بسته شد")
        input("کلید Enter برای خروج...")

if __name__ == "__main__":
    main()