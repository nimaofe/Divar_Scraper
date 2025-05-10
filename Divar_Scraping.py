# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger(__name__)

def extract_ads(driver, max_results=20):
    """
    استخراج لیست آگهی‌ها از صفحه نتایج
    :param driver: شیء مرورگر
    :param max_results: حداکثر تعداد آگهی‌های استخراج شده
    :return: لیست دیکشنری‌های حاوی اطلاعات آگهی‌ها
    """
    ads = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select('div.kt-post-card:has(h2.kt-post-card__title)')[:max_results]
        
        for item in items:
            try:
                title = item.select_one('h2.kt-post-card__title').get_text(strip=True)
                link = item.find('a')['href']
                link = f"https://divar.ir{link}" if not link.startswith('http') else link
                
                ads.append({
                    'title': title,
                    'link': link,
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                logger.warning(f"خطا در پردازش آگهی: {str(e)}")
                continue
        
        logger.info(f"تعداد {len(ads)} آگهی با موفقیت استخراج شد")
        return ads
        
    except Exception as e:
        logger.error(f"خطا در استخراج آگهی‌ها: {str(e)}")
        return []

def get_phone_number(driver, ad_url):
    """
    استخراج شماره تلفن از یک آگهی
    :param driver: شیء مرورگر
    :param ad_url: لینک آگهی
    :return: شماره تلفن یا None در صورت خطا
    """
    try:
        driver.get(ad_url)
        time.sleep(2)
        
        # کلیک روی دکمه نمایش تماس
        contact_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.post-actions__get-contact"))
        )
        contact_btn.click()
        time.sleep(1.5)
        
        # استخراج شماره با چند روش مختلف
        phone = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "a[href^='tel:'], .contact-reveal-card__phone-number")
            )
        ).text.strip()
        
        logger.info(f"شماره {phone} با موفقیت استخراج شد")
        return phone
        
    except Exception as e:
        logger.warning(f"خطا در استخراج شماره از {ad_url}: {str(e)}")
        return None

def save_cookies(driver, phone_number, cookies_dir):
    """ذخیره کوکی‌های مرورگر"""
    try:
        os.makedirs(cookies_dir, exist_ok=True)
        cookies = driver.get_cookies()
        with open(f"{cookies_dir}/{phone_number}.pkl", 'wb') as f:
            pickle.dump(cookies, f)
    except Exception as e:
        logger.error(f"خطا در ذخیره کوکی‌ها: {str(e)}")

def load_cookies(driver, phone_number, cookies_dir):
    """بارگذاری کوکی‌های ذخیره شده"""
    try:
        with open(f"{cookies_dir}/{phone_number}.pkl", 'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        return True
    except Exception as e:
        logger.warning(f"خطا در بارگذاری کوکی‌ها: {str(e)}")
        return False