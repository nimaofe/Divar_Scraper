def login_divar(driver, phone_number):
    """ورود دو مرحله‌ای به دیوار"""
    try:
        print("🔵 در حال بارگذاری صفحه دیوار...")
        driver.get("https://divar.ir")
        time.sleep(3)
        
        # مرحله 1: انتخاب شهر تهران
        print("🔵 در حال انتخاب شهر تهران...")
        try:
            city_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'تهران')]"))
            )
            city_btn.click()
            time.sleep(2)
        except:
            print("⚠️ دکمه انتخاب شهر یافت نشد (شاید قبلاً انتخاب شده)")
        
        # مرحله 2: کلیک روی ورود
        print("🔵 در حال کلیک روی دکمه ورود...")
        login_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='login-button']"))
        )
        login_btn.click()
        time.sleep(2)
        
        # مرحله 3: وارد کردن شماره تلفن
        print(f"🔵 در حال وارد کردن شماره {phone_number}...")
        phone_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "mobile"))
        )
        phone_input.clear()
        phone_input.send_keys(phone_number)
        time.sleep(1)
        
        # مرحله 4: ارسال شماره
        submit_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_btn.click()
        time.sleep(3)
        
        # مرحله 5: انتظار برای ورود دستی کاربر
        print("\n🔴 لطفاً مراحل زیر را انجام دهید:")
        print("1. کد پیامک شده را وارد کنید")
        print("2. پس از ورود موفق، این پنجره را نبندید")
        print("3. در اینجا کلید Enter را فشار دهید")
        
        input("پس از ورود موفق، Enter را بزنید...")
        return True
        
    except Exception as e:
        print(f"❌ خطا در فرآیند ورود: {str(e)}")
        return False