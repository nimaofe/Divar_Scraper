from selenium import webdriver
from bs4 import BeautifulSoup

def test_selectors():
    driver = webdriver.Edge()
    try:
        driver.get("https://divar.ir/s/tehran/car")
        input("صفحه را بررسی کنید سپس Enter بزنید...")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # تست سلکتور عنوان‌ها
        titles = soup.find_all('h2', class_='kt-post-card__title')
        print(f"\nتعداد عنوان‌های یافت شده: {len(titles)}")
        for i, title in enumerate(titles[:3], 1):
            print(f"{i}. {title.text.strip()}")
        
        # تست سلکتور لینک‌ها
        links = [a['href'] for a in soup.select('.kt-post-card a[href]')]
        print(f"\nتعداد لینک‌های یافت شده: {len(links)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_selectors()