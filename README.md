## RSS-to-WP Automator
# 📰 News Automation Pipeline

This project is a Python-based automation tool that monitors **RSS feeds**, **scrapes** full article content from news websites, and **uploads** the results to a **WordPress** site using the REST API.

## 🛠️ Environment Setup (VS Code)

To ensure the project runs correctly and doesn't interfere with other Python projects on your computer, you should use a **Virtual Environment (venv)**.

### 1. Create the Environment

1. Open your project folder in **VS Code**.
2. Open the terminal (Press `Ctrl + ` ` or go to **Terminal > New Terminal**).
3. Type the following command and press Enter:
```bash
python -m venv venv

```


*This creates a folder named `venv` inside your project.*

### 2. Activate the Environment

You must "enter" the environment so VS Code knows to use it.

* **Windows:**
```bash
.\venv\Scripts\activate

```


* **Mac/Linux:**
```bash
source venv/bin/activate

```



> **Tip:** If successful, you will see `(venv)` appear in parentheses at the start of your terminal command line.

### 3. Install Requirements

Once the environment is active, install all the necessary libraries defined in `requirements.txt`:

```bash
pip install -r requirements.txt

```

### 4. Select Interpreter in VS Code

1. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on Mac).
2. Search for **"Python: Select Interpreter"**.
3. Choose the one that starts with **`./venv`** or **`('venv': venv)`**.


## 📂 Project Structure

```text
project-root/
│
├── main.py                # The "Brain" - Orchestrates the entire process
├── .env                   # Configuration & Secrets (URLs, Passwords, Limits)
├── requirements.txt       # List of required Python libraries
│
├── data/                  # Local storage for tracking and results
│   ├── data.json          # Registry of all found links and upload status
│   └── raw_news/          # Temporary folder for scraped .txt files
│
├── scrapers/              # Web scraping logic
│   └── news_spider.py     # Scrapy spider to extract article body text
│
└── utils/                 # Helper modules (Toolbox)
    ├── file_manager.py    # Handles folder creation and cleanup
    ├── readrss.py         # Fetches and parses RSS feeds
    └── wordpress_api.py   # Handles WordPress login and posting

```

---

## 📄 File Descriptions

### 1. `main.py`

This is the entry point of the program. It coordinates the workflow by:

* Loading settings from `.env`.
* Calling `readrss.py` to find new links.
* Selecting only **new** links (where `uploaded: false`) up to the `MAX_LINKS` limit.
* Running the Scraper.
* Uploading the results to WordPress with a `POST_DELAY` between each post.
* Updating the `data.json` so the same article is never posted twice.

### 2. `scrapers/news_spider.py`

Powered by the **Scrapy** framework, this script visits the specific news URLs found in the RSS feed.

* **Extraction:** It uses CSS selectors to find the article body (targeting tags like `<p>`, `article`, and common news classes).
* **Storage:** It saves each article as a `.txt` file in `data/raw_news/`.
* **Error Handling:** It uses `try...except` blocks to ensure that if one website is down, the entire script doesn't stop.

### 3. `utils/readrss.py`

This module acts as the "Discovery" tool.

* It parses the XML from an RSS feed.
* It compares found links against `data/data.json`.
* It adds new links to the registry with a default status of `"uploaded": false`.

### 4. `utils/wordpress_api.py`

This is the communication bridge to your website.

* **Authentication:** Uses **Application Passwords** to log in securely.
* **Create Post:** Sends a `POST` request to the WordPress REST API with the article title and content.
* **Session Management:** Keeps the connection open efficiently during the upload process.

### 5. `utils/file_manager.py`

A utility script to keep the workspace clean.

* It ensures the `data/` folders exist before the script starts.
* It deletes old `.txt` files from the `raw_news/` folder before a new run starts to avoid uploading old data.

---

## ⚙️ Configuration (`.env`)

Students must create a `.env` file in the root directory with the following variables:

```ini
# News Source
RSS_FEED_URL=https://example.com/rss

# WordPress Credentials
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your_user
WORDPRESS_PASSWORD=your_app_password_here

# Automation Settings
MAX_LINKS=5        # Max articles to process per run
POST_DELAY=60      # Seconds to wait between posts (60 = 1 minute)

```

---

## 🔄 The Data Flow (How it works)

1. **Check:** `readrss.py` looks at the RSS feed and updates `data.json`.
2. **Filter:** `main.py` looks for `uploaded: false` entries in `data.json`.
3. **Scrape:** `news_spider.py` visits the links and saves text to `data/raw_news/`.
4. **Upload:** `wordpress_api.py` sends the text to WordPress.
5. **Record:** `main.py` changes the status to `uploaded: true` in the registry.

---

## 🚀 How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Configure your `.env` file.
3. Run the pipeline: `python main.py`



# راهنمای فارسی

# 📰 سامانه خودکارساز اخبار (RSS به وردپرس)

**SpiderPress: سامانه هوشمند انتقال اخبار**

این پروژه یک ابزار خودکارسازی مبتنی بر **Python** است که فیدهای **RSS** را رصد کرده، محتوای کامل مقالات را از سایت‌های خبری **استخراج (Scrape)** می‌کند و در نهایت نتایج را از طریق API به سایت **وردپرس** شما منتقل می‌کند.

---

## 🛠️ راه‌اندازی محیط برنامه‌نویسی (در VS Code)

برای اینکه پروژه به درستی اجرا شود و با سایر کتابخانه‌های سیستم شما تداخل نداشته باشد، حتماً از یک **محیط مجازی (Virtual Environment)** استفاده کنید.

### ۱. ساخت محیط مجازی

۱. پوشه پروژه را در **VS Code** باز کنید.
۲. ترمینال را باز کنید (کلید ترکیبی `Ctrl + ` `).
۳. دستور زیر را تایپ کرده و اینتر بزنید:

```bash
python -m venv venv

```

*این کار پوشه‌ای به نام `venv` در پروژه شما می‌سازد.*

### ۲. فعال‌سازی محیط مجازی

باید وارد این محیط شوید تا VS Code بداند از کدام کتابخانه‌ها استفاده کند:

* **در ویندوز:**

```bash
.\venv\Scripts\activate

```

* **در مک یا لینوکس:**

```bash
source venv/bin/activate

```

> **نکته:** در صورت موفقیت، عبارت `(venv)` را در ابتدای خط فرمان ترمینال خواهید دید.

### ۳. نصب کتابخانه‌های مورد نیاز

پس از فعال‌سازی، تمام پیش‌نیازها را با دستور زیر نصب کنید:

```bash
pip install -r requirements.txt

```

### ۴. انتخاب مفسر (Interpreter) در VS Code

۱. کلیدهای `Ctrl + Shift + P` را بزنید.
۲. عبارت **"Python: Select Interpreter"** را جستجو کنید.
۳. گزینه‌ای که شامل نام **`venv`** است را انتخاب کنید.

---

## 📂 ساختار پروژه

```text
project-root/
│
├── main.py                # مغز متفکر - مدیریت کل فرآیند اجرا
├── .env                   # تنظیمات محرمانه (آدرس‌ها، رمزها و محدودیت‌ها)
├── requirements.txt       # لیست کتابخانه‌های مورد نیاز پایتون
│
├── data/                  # ذخیره‌سازی محلی داده‌ها
│   ├── data.json          # دفتر ثبت لینک‌ها و وضعیت آپلود (آپلود شده یا نه)
│   └── raw_news/          # پوشه موقت برای ذخیره متن اخبار استخراج شده
│
├── scrapers/              # منطق استخراج از وب
│   └── news_spider.py     # خزشگر Scrapy برای استخراج متن اصلی خبر
│
└── utils/                 # ابزارهای کمکی
    ├── file_manager.py    # مدیریت پوشه‌ها و پاکسازی فایل‌های قدیمی
    ├── readrss.py         # دریافت و پردازش فیدهای RSS
    └── wordpress_api.py   # مدیریت ورود و ارسال پست به وردپرس

```

---

## 📄 شرح وظایف فایل‌ها

### 1. فایل `main.py`

نقطه شروع برنامه است. این فایل هماهنگی بین بخش‌ها را انجام می‌دهد:

* بارگذاری تنظیمات از فایل `.env`.
* فراخوانی `readrss.py` برای یافتن لینک‌های جدید.
* انتخاب لینک‌های جدید (آن‌هایی که `uploaded: false` هستند) تا سقف مجاز `MAX_LINKS`.
* اجرای خزشگر (Scraper).
* ارسال نتایج به وردپرس با رعایت فاصله زمانی `POST_DELAY`.
* به‌روزرسانی `data.json` برای جلوگیری از ارسال تکراری اخبار.

### 2. فایل `scrapers/news_spider.py`

این اسکریپت با فریم‌ورک **Scrapy** کار می‌کند و وظیفه دارد به لینک‌های خبری سر بزند.

* **استخراج:** با استفاده از CSS Selectorها، متن اصلی خبر را (با هدف قرار دادن تگ‌های `<p>` و کلاس‌های خبری) پیدا می‌کند.
* **ذخیره‌سازی:** هر خبر را به صورت یک فایل `.txt` در پوشه `data/raw_news/` ذخیره می‌کند.

### 3. فایل `utils/readrss.py`

این ماژول نقش "اکتشاف‌گر" را دارد.

* فایل XML فید RSS را تحلیل می‌کند.
* لینک‌های جدید را با لیست قبلی در `data.json` مقایسه می‌کند.
* لینک‌های جدید را با وضعیت پیش‌فرض `"uploaded": false` به لیست اضافه می‌کند.

### 4. فایل `utils/wordpress_api.py`

پل ارتباطی با سایت شماست.

* **احراز هویت:** از **Application Passwords** برای ورود امن استفاده می‌کند.
* **ارسال پست:** عنوان و محتوا را به API وردپرس ارسال می‌کند.

### 5. فایل `utils/file_manager.py`

وظیفه نظافت محیط کاری را دارد.

* مطمئن می‌شود پوشه‌های `data` قبل از شروع برنامه وجود دارند.
* فایل‌های `.txt` قدیمی را قبل از هر اجرای جدید پاک می‌کند.

---

## ⚙️ تنظیمات (`.env`)

دانشجویان باید یک فایل با نام `.env` در مسیر اصلی بسازند و متغیرهای زیر را در آن تنظیم کنند:

```ini
# منبع خبری
RSS_FEED_URL=آدرس_فید_آر_اس_اس

# اطلاعات وردپرس
WORDPRESS_URL=آدرس_سایت_شما
WORDPRESS_USERNAME=نام_کاربری
WORDPRESS_PASSWORD=رمز_اپلیکیشن_وردپرس

# تنظیمات خودکارسازی
MAX_LINKS=5        # حداکثر تعداد خبر در هر بار اجرا
POST_DELAY=60      # فاصله زمانی بین هر پست به ثانیه (60 = 1 دقیقه)

```

---

## 🔄 جریان داده (نحوه کارکرد)

۱. **بررسی:** فایل `readrss.py` فید را چک کرده و `data.json` را به‌روز می‌کند.
۲. **فیلتر:** فایل `main.py` به دنبال مواردی می‌گردد که وضعیت آپلود آن‌ها `false` است.
۳. **استخراج:** فایل `news_spider.py` محتوای لینک‌ها را خوانده و ذخیره می‌کند.
۴. **ارسال:** فایل `wordpress_api.py` محتوا را به وردپرس می‌فرستد.
۵. **ثبت:** فایل `main.py` وضعیت را در دفتر ثبت به `uploaded: true` تغییر می‌دهد.

---

## 🚀 نحوه اجرا

۱. نصب پیش‌نیازها: `pip install -r requirements.txt`
۲. تنظیم فایل `.env`.
۳. اجرای برنامه: `python main.py`



---

## 👨‍💻 Developer Information

This project was designed and developed by **[Your Name/Team Name]**. The goal is to teach students the concepts of **Automation**, **Web Scraping**, and **API integration**.

* **Developer:** [saman Balahang]
* **GitHub:** [[Your GitHub Link](https://github.com/samanbalahang)]
* **phone:** [09224194485]

> **Note:** If you are a student and encounter any issues while running the project, feel free to reach out via the **Issues** section on GitHub or through email.