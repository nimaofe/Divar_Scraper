from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time

SELECTORS = {
    # اصلاح سلکتور منوی کاربر اصلی
    "user_menu": "//button[contains(@class, 'nav-bar__more-button')]",
    "login_button": "//div[contains(@class, 'kt-menu__item') and contains(., 'ورود')]",
    "phone_input": "//input[@type='tel' and @name='phone']",
    "submit_button": "//button[@type='submit' and contains(., 'ارسال کد')]",
    # سلکتور جدید برای بستن باکس انتخاب شهر اگر باز باشد
    "close_city_modal": "//button[contains(@class, 'kt-modal__close-button')]"
}

def main():
    options = webdriver.EdgeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Edge(options=options)
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)

    try:
        # مرحله ۱: باز کردن صفحه و مدیریت احتمالی مودال شهر
        driver.get("https://divar.ir/s/tehran")
        print("✅ صفحه اصلی بارگذاری شد")
        
        # تلاش برای بستن مودال انتخاب شهر اگر وجود دارد
        try:
            close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS["close_city_modal"])))
            close_btn.click()
            print("✅ باکس انتخاب شهر بسته شد")
            time.sleep(1)
        except TimeoutException:
            pass

        # مرحله ۲: باز کردن منوی کاربر اصلی
        user_menu = wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS["user_menu"])))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", user_menu)
        time.sleep(0.5)
        user_menu.click()
        print("✅ منوی کاربر باز شد")
        time.sleep(1)

        # مرحله ۳: کلیک روی گزینه ورود با حرکت ماوس
        login_btn = wait.until(EC.visibility_of_element_located((By.XPATH, SELECTORS["login_button"])))
        actions.move_to_element(login_btn).pause(0.5).click().perform()
        print("✅ فرم ورود فعال شد")
        time.sleep(2)

        # مرحله ۴: وارد کردن شماره تلفن
        phone_field = wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS["phone_input"])))
        phone_field.send_keys("09217977178")  # شماره خود را وارد کنید
        print("✅ شماره وارد شد")

        # مرحله ۵: ارسال درخواست کد
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS["submit_button"])))
        driver.execute_script("arguments[0].click();", submit_btn)
        print("✅ درخواست کد ارسال شد")
        time.sleep(3)

        # مرحله ۶: وارد کردن دستی کد
        input("🔑 کد دریافتی را وارد کرده و Enter بزنید: ")
        print("✅ ورود موفقیت‌آمیز شد!")

    except TimeoutException as e:
        print(f"❌ خطا: عنصر پیدا نشد! ({str(e)})")
        driver.save_screenshot('error.png')
    except Exception as e:
        print(f"❌ خطای ناشناخته: {str(e)}")
        driver.save_screenshot('critical_error.png')
    finally:
        driver.quit()

if __name__ == "__main__":
    main()