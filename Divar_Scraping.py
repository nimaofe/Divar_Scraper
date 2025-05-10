# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import os
import requests

# تنظیمات
WAIT_TIMEOUT = 25
MAX_RETRIES = 3

def convert_persian_numbers(text):
    """تبدیل اعداد فارسی به انگلیسی"""
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    return ''.join(persian_to_english.get(c, c) for c in text)

def login_divar(driver, phone_number):
    """ورود به دیوار با قابلیت انتخاب شهر"""
    try:
        print("🔵 در حال ورود به دیوار...")
        driver.get("https://divar.ir")
        time.sleep(3)

        # انتخاب شهر تهران (اگر نیاز باشد)
        try:
            city_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران')]"))
            )
            city_btn.click()
            time.sleep(2)
        except:
            pass

        # کلیک روی دکمه ورود
        login_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='login-button']"))
        )
        login_btn.click()
        time.sleep(2)

        # وارد کردن شماره تلفن
        phone_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.NAME, "mobile"))
        )
        phone_input.clear()
        phone_input.send_keys(phone_number)
        time.sleep(1)

        # ارسال شماره
        submit_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_btn.click()
        time.sleep(3)

        # انتظار برای ورود دستی کاربر
        print("\n🔴 لطفاً مراحل زیر را انجام دهید:")
        print("1. کد پیامک شده را وارد کنید")
        print("2. پس از ورود موفق، به این پنجره برگردید")
        print("3. کلید Enter را فشار دهید")
        input("پس از ورود موفق، Enter را بزنید...")
        
        return True

    except Exception as e:
        print(f"❌ خطا در ورود: {str(e)}")
        return False

def extract_phone(driver, url):
    """استخراج شماره از یک آگهی"""
    for _ in range(MAX_RETRIES):
        try:
            driver.get(url)
            time.sleep(2)

            # کلیک روی دکمه نمایش تماس
            contact_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".post-actions__get-contact"))
            )
            contact_btn.click()
            time.sleep(2)

            # استخراج شماره
            phone_element = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='tel:']"))
            )
            return convert_persian_numbers(phone_element.text)
            
        except Exception as e:
            print(f"⚠️ خطا در استخراج شماره (تلاش مجدد): {str(e)}")
            time.sleep(3)
    
    return None

def get_phone_numbers(driver, urls):
    """استخراج شماره‌ها از لیست URLها"""
    phones = []
    for i, url in enumerate(urls, 1):
        print(f"\n📌 آگهی {i} از {len(urls)}")
        phone = extract_phone(driver, url)
        if phone:
            print(f"✅ شماره یافت شد: {phone}")
            phones.append(phone)
        else:
            print("❌ شماره یافت نشد")
    
    return phones

def extract_urls(page_source):
    """استخراج لینک‌های آگهی‌ها"""
    soup = BeautifulSoup(page_source, 'html.parser')
    return [
        f"https://divar.ir{item.find('a')['href']}"
        for item in soup.find_all('div', class_='post-card-item')
        if item.find('a')
    ][1:-1]  # حذف اولین و آخرین آیتم غیرمرتبط

def divar_search(driver, query, city='tehran', category=None, limit=None):
    """جستجو در دیوار و جمع‌آوری لینک‌ها"""
    base_url = f'https://divar.ir/s/{city}/{category}?q={query}' if category else f'https://divar.ir/s/{city}?q={query}'
    
    try:
        if not requests.get(base_url, timeout=10).ok:
            print("❌ مشکل در دسترسی به دیوار")
            return None
            
        print(f"🔍 در حال جستجو برای '{query}' در {city}...")
        driver.get(base_url)
        time.sleep(3)
        
        urls = []
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # اسکرول و جمع‌آوری لینک‌ها
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            urls.extend(extract_urls(driver.page_source))
            urls = list(set(urls))  # حذف تکراری‌ها
            
            # بررسی محدودیت تعداد
            if limit and len(urls) >= limit:
                break
                
            # بررسی پایان صفحه
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        return urls[:limit] if limit else urls
        
    except Exception as e:
        print(f"❌ خطا در جستجو: {str(e)}")
        return None