import logging
from selenium.webdriver.remote.remote_connection import LOGGER

# تنظیم سطح لاگ
LOGGER.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO)

def setup_driver():
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59")
    
    # فعال کردن لاگ مرورگر
    service = Service(
        executable_path='msedgedriver.exe',
        service_args=['--verbose', '--log-path=edgedriver.log']
    )
    
    return webdriver.Edge(service=service, options=options)

try:
    driver = setup_driver()
    print("در حال تست اتصال به دیوار...")
    driver.get("https://divar.ir")
    print("عنوان صفحه:", driver.title)
    input("اگر صفحه نمایش داده شد Enter بزنید...")
except Exception as e:
    print("خطای دقیق:", str(e))
finally:
    driver.quit()