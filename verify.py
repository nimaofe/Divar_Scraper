from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def main():
    # تنظیمات مرورگر
    options = webdriver.EdgeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Edge(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # مرحله 1: باز کردن صفحه
        driver.get("https://divar.ir/s/tehran/car")
        print("✅ صفحه اصلی باز شد")

        # مرحله 2: انتخاب شهر تهران
        try:
            city_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='tehran-city-button']"))
            )
            city_btn.click()
            print("✅ شهر تهران انتخاب شد")
            time.sleep(2)
        except TimeoutException:
            print("⚠️ انتخاب شهر ضروری نبود")

        # مرحله 3: ورود به حساب کاربری
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ورود')]"))
        )
        login_btn.click()
        print("✅ وارد صفحه ورود شد")

        # وارد کردن شماره تلفن
        phone_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='phone']"))
        )
        phone_input.send_keys("09217977178")  # شماره خود را جایگزین کنید
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        print("✅ شماره تلفن وارد شد")

        # وارد کردن کد پیامک (دستی)
        input("✉️ کد پیامک شده را وارد کرده و Enter بزنید...")

        # مرحله 4: اسکرول و انتخاب آگهی
        ads = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.post-card-item"))
        )
        print(f"🔍 تعداد آگهی‌های یافت شده: {len(ads)}")

        # انتخاب اولین آگهی
        ads[0].click()
        print("✅ روی آگهی کلیک شد")
        time.sleep(3)

        # مرحله 5: دریافت شماره تماس
        contact_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.post-actions__get-contact"))
        )
        contact_btn.click()
        print("✅ دکمه تماس کلیک شد")
        time.sleep(2)

        phone = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.kt-unexpandable-row__value-box"))
        )
        print(f"📞 شماره تماس: {phone.text}")

    except TimeoutException as e:
        print(f"⛔ خطا: عنصر مورد نظر یافت نشد! ({str(e)})")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()