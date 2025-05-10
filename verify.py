from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

SELECTORS = {
    "dropdown": "/html/body/div[1]/header/nav/div[2]/div[3]/div[1]/button",
    "login_button": "//div[@class='kt-menu__item' and contains(., 'ورود')]",
    "phone_input": "/html/body/div[5]/div/section/div/div/form/div/input",
    "submit_button": "/html/body/div[5]/div/section/footer/div/button"
}

def main():
    options = webdriver.EdgeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--ignore-certificate-errors")
    
    driver = webdriver.Edge(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        # مرحله ۱: باز کردن صفحه
        driver.get("https://divar.ir/s/tehran")
        print("✅ صفحه اصلی بارگذاری شد")
        time.sleep(3)

        # مرحله ۲: باز کردن منوی کاربر
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS["dropdown"])))
        dropdown.click()
        print("✅ منوی کاربر باز شد")
        time.sleep(2)

        # مرحله ۳: کلیک روی گزینه "ورود" با جاوااسکریپت
        login_btn = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS["login_button"])))
        driver.execute_script("arguments[0].click();", login_btn)
        print("✅ فرم ورود فعال شد")
        time.sleep(3)

        # مرحله ۴: وارد کردن شماره تلفن
        phone_field = wait.until(EC.visibility_of_element_located((By.XPATH, SELECTORS["phone_input"])))
        phone_field.send_keys("09217977178")  # شماره خود را وارد کنید
        print("✅ شماره وارد شد")
        time.sleep(1)

        # مرحله ۵: ارسال درخواست کد
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS["submit_button"])))
        submit_btn.click()
        print("✅ درخواست کد ارسال شد")
        time.sleep(3)

        # مرحله ۶: وارد کردن دستی کد
        input("🔑 کد دریافتی را وارد کرده و Enter بزنید: ")
        print("✅ ورود موفقیت‌آمیز شد!")

    except TimeoutException as e:
        print(f"❌ خطا: عنصر پیدا نشد! ({str(e)})")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()