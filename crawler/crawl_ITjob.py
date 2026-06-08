import requests as rq
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Đường dẫn lưu danh sách link đã crawl và file json chứa chi tiết job
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS_FILE = os.path.join(BASE_DIR, "data", "raw", "crawled_ITviec_links.txt")
JOBS_FILE = os.path.join(BASE_DIR, "data", "raw", "jobs_detail.json")

#====================
# Helper functions for links file
#====================
def load_crawled_links(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_crawled_link(file_path, link):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def save_jobs_to_json(file_path, new_jobs):
    if not new_jobs:
        return
    existing_jobs = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_jobs = json.load(f)
                if not isinstance(existing_jobs, list):
                    existing_jobs = []
        except Exception as e:
            print(f"Lỗi khi đọc file JSON cũ: {e}. Sẽ ghi đè file mới.")
    
    existing_jobs = new_jobs + existing_jobs
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_jobs, f, ensure_ascii=False, indent=4)
        print(f"✅ Đã lưu thêm {len(new_jobs)} jobs vào file JSON: {file_path}")
    except Exception as e:
        print(f"❌ Lỗi khi lưu file JSON: {e}")

# Cấu hình headers giả lập trình duyệt để tránh bị chặn (403 Forbidden)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8"
}

#====================
# Get job links
#====================
def get_job(url_base):
    links = []

    for page in range(1, 3):  # Adjust the range as needed
        url = f"{url_base}?page={page}"
        print(f"-> Đang lấy danh sách công việc từ: {url}")
        try:
            response = rq.get(url, headers=HEADERS)
            print(f"   Trạng thái phản hồi: {response.status_code}")
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            page_links = []
            for h3 in soup.find_all("h3", class_="imt-3 text-break"):
                link = h3.get("data-url")
                if link:
                    page_links.append(link)
            
            print(f"   Tìm thấy {len(page_links)} links trên trang {page}")
            links.extend(page_links)
        except Exception as e:
            print(f"   Lỗi khi lấy dữ liệu trang {page}: {e}")

    return links



#====================
# Convert posted time
#====================

def convert_posted_time(posted_time: str):

    now = datetime.now()

    posted_time = posted_time.lower().strip()

    if "phút trước" in posted_time:
        minutes = int(re.search(r"\d+", posted_time).group())
        return now - timedelta(minutes=minutes)

    elif "giờ trước" in posted_time:
        hours = int(re.search(r"\d+", posted_time).group())
        return now - timedelta(hours=hours)

    elif "ngày trước" in posted_time:
        days = int(re.search(r"\d+", posted_time).group())
        return now - timedelta(days=days)

    return now

#====================
# Extract job header
#====================

def extract_job_header(soup):

    result = {
        "title": "",
        "company": ""
    }

    header = soup.select_one("div.job-header-info")

    if not header:
        return result

    title = header.find("h1")
    company = header.select_one("div.employer-name")

    if title:
        result["title"] = title.get_text(strip=True)

    if company:
        result["company"] = company.get_text(strip=True)

    return result

#====================
# Extract job info
#==================== 

def extract_job_info(info, url=None):

    result = {
        "url": url,
        "locations": [],
        "working_mode": "",
        "posted_time_raw": "",
        "posted_at": None,
        "skills": [],
        "specializations": [],
        "industries": []
    }

    if info is None:
        return result

    # =====================
    # LOCATION + WORK MODE + POSTED TIME
    # =====================

    spans = info.select(
        "span.normal-text.text-rich-grey"
    )

    for span in spans:

        text = span.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        # Posted time
        if any(
            keyword in text.lower()
            for keyword in [
                "phút trước",
                "giờ trước",
                "ngày trước"
            ]
        ):

            result["posted_time_raw"] = text

            result["posted_at"] = (
                convert_posted_time(text)
                .isoformat()
            )

        # Working mode
        elif text in [
            "Linh hoạt",
            "Hybrid",
            "Remote",
            "On-site",
            "Tại văn phòng"
        ]:

            result["working_mode"] = text

        # Location
        elif len(text) > 0:

            result["locations"].append(text)

    # =====================
    # SKILLS
    # =====================

    skill_header = info.find(
        string=lambda x: x and "Kỹ năng" in x
    )

    if skill_header:

        skill_block = skill_header.find_parent(
            "div",
            class_=lambda c: c and "flex-column" in c
        )

        if skill_block:

            result["skills"] = [
                a.get_text(strip=True)
                for a in skill_block.select("a")
            ]

    # =====================
    # SPECIALIZATIONS
    # =====================

    specialization_header = info.find(
        string=lambda x: x and "Chuyên môn" in x
    )

    if specialization_header:

        specialization_block = specialization_header.find_parent(
            "div",
            class_=lambda c: c and "flex-column" in c
        )

        if specialization_block:

            result["specializations"] = [
                a.get_text(strip=True)
                for a in specialization_block.select("a")
            ]

    # =====================
    # INDUSTRIES
    # =====================

    industry_header = info.find(
        string=lambda x: x and "Lĩnh vực" in x
    )

    if industry_header:

        industry_block = industry_header.find_parent(
            "div",
            class_=lambda c: c and "flex-column" in c
        )

        if industry_block:

            result["industries"] = [
                div.get_text(strip=True)
                for div in industry_block.select(
                    "div.itag"
                )
            ]

    return result

#====================
# Extract job content
#====================

def extract_job_content(soup):

    result = {
        "job_description": "",
        "requirements": "",
        "benefits": ""
    }

    sections = soup.select(
        "div.imy-5.paragraph"
    )

    for section in sections:

        h2 = section.find("h2")

        if not h2:
            continue

        title = h2.get_text(strip=True)

        # copy để không ảnh hưởng html gốc
        section_copy = BeautifulSoup(
            str(section),
            "html.parser"
        )

        first_h2 = section_copy.find("h2")

        if first_h2:
            first_h2.extract()

        content = section_copy.get_text(
            "\n",
            strip=True
        )

        if "Mô tả công việc" in title:
            result["job_description"] = content

        elif "Yêu cầu công việc" in title:
            result["requirements"] = content

        elif "Tại sao bạn sẽ yêu thích" in title:
            result["benefits"] = content

    return result

#====================
# MAIN
#====================

url_base = "https://itviec.com/viec-lam-it"
job_links = get_job(url_base)

if not job_links:
    print("\n[CẢNH BÁO] Không lấy được danh sách job link nào. Vui lòng kiểm tra lại kết nối mạng hoặc trang web có thể đã chặn request.")
else:
    print(f"\nLấy danh sách hoàn tất. Tổng số job links tìm thấy: {len(job_links)}")

# Tải các link đã crawl từ trước
crawled_links = load_crawled_links(LINKS_FILE)

job_detail = []
new_crawled_count = 0

for link in job_links:
    if link in crawled_links:
        print(f"Bỏ qua link đã crawl: {link}")
        continue

    print(f"Đang crawl link mới: {link}")
    try:
        response = rq.get(link, headers=HEADERS)
        if response.status_code != 200:
            print(f"Không thể tải link {link}: HTTP {response.status_code}")
            continue

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )
        title = soup.find("div", class_ ="ipy-3 ipx-5 bg-it-white text-rich-grey job-show-info box-shadow-medium")
        job = {}

        job.update(extract_job_header(soup))

        job.update(
            extract_job_info(title, url=link)
        )

        job.update(
            extract_job_content(soup)
        )
        job_detail.append(job)

        # Lưu link vào file sau khi crawl thành công
        save_crawled_link(LINKS_FILE, link)
        crawled_links.add(link)
        new_crawled_count += 1

    except Exception as e:
        print(f"Lỗi khi crawl link {link}: {e}")

print(f"\n=== Hoàn thành crawl. Tổng số job mới đã bóc tách: {new_crawled_count} ===")

# Lưu chi tiết job đã crawl vào file JSON
save_jobs_to_json(JOBS_FILE, job_detail)

