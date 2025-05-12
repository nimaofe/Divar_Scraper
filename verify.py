from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# تنظیمات ثابت
BASE_URL = "https://divar.ir/s/tehran"
PHONE_NUMBER = "09217977178"  # شماره خود را جایگزین کنید
TIMEOUT = 30

class LoginManager:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def initialize_driver(self):
        """آماده سازی و تنظیم مرورگر"""
        options = webdriver.EdgeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Edge(options=options)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.driver.maximize_window()
        
    def handle_consent_popup(self):
        """مدیریت popupهای کوکی یا تاییدیه (در صورت وجود)"""
        try:
            consent_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button.kt-button--primary')
            ))
            consent_button.click()
            print("✅ Popup تاییدیه مدیریت شد")
        except TimeoutException:
            pass
            
    def open_login_modal(self):
        """باز کردن مدال ورود"""
        # باز کردن منوی کاربر
        self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[aria-label="منوی کاربری"]')
        )).click()
        print("✅ منوی کاربر باز شد")
        
        # کلیک روی گزینه ورود
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'kt-menu__item') and contains(., 'ورود')]")
        )).click()
        print("✅ مدال ورود فعال شد")
        
    def enter_phone_number(self):
        """وارد کردن شماره تلفن و ارسال درخواست"""
        # سوئیچ به مدال فعال
        modal = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.kt-dimmer--open section')
        ))
        
        # وارد کردن شماره
        phone_input = modal.find_element(By.CSS_SELECTOR, 'input[name="phone"]')
        phone_input.clear()
        phone_input.send_keys(PHONE_NUMBER)
        print("✅ شماره تلفن وارد شد")
        
        # کلیک روی دکمه ادامه
        modal.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        print("✅ درخواست کد ارسال شد")
        
        # بررسی پیام موفقیت
        self.wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, 'div.kt-modal__body'), 'کد تأیید را وارد کنید'
        ))
        print("✅ تایید شماره موفقیت آمیز بود")
        
    def enter_verification_code(self):
        """دریافت و وارد کردن کد تایید"""
        code = input("🔑 کد دریافتی را وارد کرده و Enter بزنید: ")
        
        # پیدا کردن فیلدهای کد
        code_inputs = self.wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'input.verification-input')
        ))
        
        # پر کردن کد
        for i, digit in enumerate(code):
            code_inputs[i].send_keys(digit)
        print("✅ کد تایید وارد شد")
        
        # بررسی ورود موفق
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[data-testid="loggedin-user-info"]')
        ))
        print("✅ ورود موفقیت آمیز انجام شد")
        
    def run(self):
        try:
            self.initialize_driver()
            self.driver.get(BASE_URL)
            print("✅ صفحه اصلی بارگذاری شد")
            
            self.handle_consent_popup()
            self.open_login_modal()
            self.enter_phone_number()
            self.enter_verification_code()
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"❌ خطا در فرآیند: {str(e)}")
            if self.driver:
                self.driver.save_screenshot('error.png')
                print("📸 از صفحه خطا عکس گرفته شد (error.png)")
                
        finally:
            if self.driver:
                self.driver.quit()
                print("✅ مرورگر بسته شد")

if __name__ == "__main__":
    login_manager = LoginManager()
    login_manager.run()