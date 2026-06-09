# Vietnam Tech Job Analytics 🇻🇳💼

Dự án tự động thu thập, xử lý và phân tích dữ liệu tuyển dụng ngành công nghệ thông tin (IT) tại Việt Nam từ nguồn **ITviec**, đồng bộ lên cơ sở dữ liệu quan hệ **Supabase** phục vụ cho việc phân tích xu hướng công nghệ, mức lương và thị trường lao động.

---

## 🏗️ Kiến trúc & Luồng hoạt động (Workflow)

Hệ thống hoạt động theo mô hình ETL tự động (Extract - Transform - Load) theo luồng khép kín như sau:

```mermaid
graph TD
    A[ITviec Website] -->|Crawl Pages 1-2| B(crawler/crawl_ITjob.py)
    B -->|Đọc trùng lặp| C{crawled_ITviec_links.txt}
    C -->|Link Mới| D[Cào chi tiết Job]
    D -->|Prepend - Lưu mới lên đầu| E[(jobs_detail.json)]
    E --> F(etl/load.py)
    F -->|1. SELECT url FROM jobs| G[(Supabase PostgreSQL)]
    F -->|2. Lọc bỏ Job đã tồn tại| H[Tách danh sách New Jobs]
    H -->|3. Đồng bộ hóa| G
    G -->|Direct Query / Import| I[Power BI Dashboard]
```

### Chi tiết luồng hoạt động:
1. **Cào dữ liệu (Crawl Phase)**:
   - Script chạy định kỳ (hoặc thủ công) để lấy danh sách URL các job tuyển dụng mới nhất từ trang danh mục của ITviec.
   - Hệ thống đối chiếu URL với file `crawled_ITviec_links.txt`. Các URL nào đã được cào từ trước sẽ bị bỏ qua để tránh lãng phí tài nguyên mạng.
   - Với các URL mới, script tải mã nguồn HTML và phân tách chi tiết: *Tiêu đề, Công ty, Địa điểm, Chế độ làm việc, Ngày đăng, Kỹ năng yêu cầu, Chuyên môn, Lĩnh vực hoạt động, Mô tả chi tiết công việc, Yêu cầu ứng viên, Phúc lợi*.
   - Sau khi hoàn thành, danh sách công việc mới được lưu bằng cách **chèn lên đầu** file `data/raw/jobs_detail.json`, giúp các dữ liệu mới nhất luôn nằm ở đầu danh sách.

2. **Xử lý và tải lên Database (ETL Phase)**:
   - Script `etl/load.py` đọc toàn bộ dữ liệu từ `jobs_detail.json`.
   - Kết nối tới cơ sở dữ liệu Supabase, thực hiện truy vấn nhanh danh sách các URL job đã tồn tại.
   - Loại bỏ các job đã tồn tại khỏi danh sách xử lý và chỉ lọc ra các công việc thực sự mới.
   - Tiến hành chuẩn hóa dữ liệu địa điểm (sử dụng module `extract_city` để quy hoạch địa điểm về các thành phố lớn: Hà Nội, TP.HCM, Đà Nẵng, Cần Thơ, Hải Phòng).
   - Tải dữ liệu vào các bảng tương ứng trên Supabase theo mối quan hệ chuẩn hóa.

3. **Trực quan hóa dữ liệu (Visualization Phase)**:
   - Power BI Desktop kết nối đến Supabase thông qua driver PostgreSQL.
   - Truy vấn dữ liệu từ các bảng đã được chuẩn hóa để vẽ các báo cáo trực quan hóa về xu hướng công nghệ, nhu cầu thị trường, phân bố công việc theo địa lý, và kỹ năng được săn đón nhiều nhất.

---

## 🛠️ Công nghệ sử dụng (Tech Stack)
- **Ngôn ngữ lập trình**: Python 3.10+
- **Thư viện chính**:
  - `requests`: Gửi các HTTP request để tải nội dung HTML từ website.
  - `BeautifulSoup4` (`bs4`): Phân tích cú pháp HTML và bóc tách các trường dữ liệu cần thiết.
  - `pandas`: Hỗ trợ cấu trúc dữ liệu và xử lý nếu cần phân tích sâu hơn.
  - `SQLAlchemy`: ORM kết nối và thực thi các câu lệnh SQL với database một cách bảo mật và có cấu trúc.
  - `psycopg2-binary`: Driver PostgreSQL phục vụ kết nối với Supabase.
  - `python-dotenv`: Quản lý các cấu hình nhạy cảm qua file môi trường `.env`.
- **Hệ quản trị CSDL**: Supabase PostgreSQL.

---

## 📂 Cấu trúc thư mục dự án
```text
vietnam-tech-job-analytics/
├── .github/
│   └── workflows/
│       └── crawl.yml           # Tự động hóa lịch trình cào và nạp dữ liệu (GitHub Actions)
├── crawler/
│   └── crawl_ITjob.py          # Script thu thập dữ liệu tuyển dụng từ website ITviec
├── data/
│   └── raw/
│       ├── crawled_ITviec_links.txt  # Bộ lưu trữ danh sách các link job đã crawl
│       └── jobs_detail.json          # File JSON lưu thông tin chi tiết toàn bộ job cào được
├── database/
│   ├── init_db.py              # Script thiết lập các bảng trên Supabase ban đầu
│   ├── schema.sql              # File DDL định nghĩa cấu trúc cơ sở dữ liệu
│   └── test_connection.py      # Script test kết nối tới cơ sở dữ liệu Supabase
├── etl/
│   ├── extract.py              # Trích xuất thông tin (Chuẩn hóa tỉnh/thành phố)
│   ├── load.py                 # Module nạp dữ liệu tối ưu hóa vào Supabase
│   └── transform.py            # Chứa các bộ tiền xử lý logic transform dữ liệu
├── .env                        # Chứa cấu hình kết nối DB bí mật (Không đẩy lên Git)
├── requirements.txt            # Danh sách các thư viện phụ thuộc của dự án
└── README.md                   # Tài liệu hướng dẫn sử dụng và luồng dự án
```

---

## 💾 Thiết kế Cơ sở dữ liệu (Database Schema)

Cơ sở dữ liệu được thiết kế theo dạng quan hệ nhằm mục đích phân tích sâu về mối tương quan giữa công việc và các yếu tố kỹ năng/địa điểm/chuyên ngành.

```mermaid
erDiagram
    jobs {
        bigint id PK
        text url UNIQUE
        text title
        text company
        text working_mode
        timestamp posted_at
        timestamp crawl_time
        text job_description
        text requirements
        text benefits
        text source
    }
    skills {
        bigint id PK
        text name UNIQUE
    }
    industries {
        bigint id PK
        text name UNIQUE
    }
    specializations {
        bigint id PK
        text name UNIQUE
    }
    job_locations {
        bigint id PK
        bigint job_id FK
        text location
        text city
    }
    job_skills {
        bigint job_id PK, FK
        bigint skill_id PK, FK
    }
    job_industries {
        bigint job_id PK, FK
        bigint industry_id PK, FK
    }
    job_specializations {
        bigint job_id PK, FK
        bigint specialization_id PK, FK
    }

    jobs ||--o{ job_locations : "has"
    jobs ||--o{ job_skills : "requires"
    skills ||--o{ job_skills : "used in"
    jobs ||--o{ job_industries : "belongs to"
    industries ||--o{ job_industries : "categorized under"
    jobs ||--o{ job_specializations : "categorizes"
    specializations ||--o{ job_specializations : "mapped to"
```

### Các thực thể chính:
* **jobs**: Lưu trữ các thông tin chi tiết cơ bản của tin tuyển dụng.
* **skills**, **industries**, **specializations**: Bảng danh mục hỗ trợ việc phân nhóm và chuẩn hóa các kỹ năng công nghệ (ví dụ: Python, SQL), lĩnh vực kinh doanh (Fintech, Outsourcing), và chuyên môn làm việc (Backend, Mobile Developer).
* **job_locations**: Lưu thông tin chi tiết địa điểm làm việc và thành phố được phân loại (`Hồ Chí Minh`, `Hà Nội`, `Đà Nẵng`, `Cần Thơ`, `Hải Phòng`, `Khác`) phục vụ phân tích phân bố địa lý của thị trường việc làm.

---

## ⚡ Giải pháp Tối ưu hóa hiệu năng nạp dữ liệu (Optimizations)

Trước đây, khi số lượng công việc đã cào tăng lên, script `load.py` phải thực hiện quét từng bản ghi trong file JSON và chạy hàng nghìn câu lệnh kiểm tra / chèn dữ liệu trực tiếp vào database qua mạng, dẫn đến tình trạng chạy rất chậm (lên tới hàng chục phút).

### Các giải pháp tối ưu đã triển khai:
1. **Lưu dữ liệu mới nhất lên đầu JSON**:
   - Khi chạy `crawl_ITjob.py`, các job mới cào được sẽ được chèn lên đầu mảng JSON (`prepend` thay vì `append` / `extend`), giúp việc theo dõi thủ công và lưu trữ file tối ưu hơn:
     ```python
     existing_jobs = new_jobs + existing_jobs
     ```
2. **Lọc dữ liệu trên bộ nhớ (In-memory Filtering) trước khi nạp**:
   - Trong `load.py`, thay vì kiểm tra sự tồn tại của từng job bằng cách gửi truy vấn SQL lặp đi lặp lại qua internet, chương trình chỉ gửi duy nhất **1 truy vấn** để lấy toàn bộ URL hiện có trong CSDL:
     ```sql
     SELECT url FROM jobs
     ```
   - Chuyển tập hợp URL đó thành kiểu dữ liệu `set` trong Python ($O(1)$ lookup).
   - Lọc nhanh danh sách job mới cần đẩy lên bằng Python:
     ```python
     new_jobs = [job for job in jobs if job.get("url") not in existing_urls]
     ```
   - **Kết quả**: Chỉ chèn dữ liệu thực sự mới. Thời gian đồng bộ hóa giảm từ nhiều phút xuống chỉ còn **dưới 15 giây** (cho lượng dữ liệu hàng nghìn bản ghi).

---

## 🚀 Hướng dẫn thiết lập & Chạy dự án

### 1. Cài đặt các thư viện cần thiết
Đảm bảo bạn đã cài đặt Python 3.10 trở lên. Tiến hành chạy lệnh cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường
Tạo file `.env` nằm tại thư mục gốc dự án và định nghĩa các tham số kết nối Supabase của bạn:
```ini
DB_HOST=aws-1-ap-southeast-2.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=your_supabase_user
DB_PASSWORD=your_supabase_password
DATABASE_URL=postgresql://your_supabase_user:your_supabase_password@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres
```

### 3. Kiểm tra kết nối CSDL
Để đảm bảo thông tin đăng nhập trong file `.env` chính xác, hãy chạy script test kết nối:
```bash
python database/test_connection.py
```

### 4. Khởi tạo Cơ sở dữ liệu (Database Initialization)
Nếu là lần đầu chạy dự án, tiến hành khởi tạo các bảng và khóa ngoại bằng schema:
```bash
python database/init_db.py
```

### 5. Thu thập & Đồng bộ dữ liệu
Để thực hiện quy trình thủ công:
- **Bước 1**: Cào dữ liệu việc làm từ ITviec:
  ```bash
  python crawler/crawl_ITjob.py
  ```
- **Bước 2**: Đồng bộ dữ liệu mới cào lên database:
  ```bash
  python etl/load.py
  ```

---

## 📅 Tự động hóa lịch trình (Automation với GitHub Actions)
Dự án được cấu hình sẵn GitHub Actions tại `.github/workflows/crawl.yml` để chạy tự động cào và đồng bộ dữ liệu hàng ngày vào lúc **(08:00 AM, 12:00 PM, 4:00 PM, 8:00 PM Giờ Việt Nam)**:
- Không cần cắm máy chạy local, Actions tự động setup Python, cài đặt dependencies, chạy file crawl và load dữ liệu trực tiếp lên DB Supabase từ xa.
- Để sử dụng tính năng này trên kho lưu trữ của bạn, cần add biến mật `DATABASE_URL` vào phần **GitHub Secrets** của repository.

---

## 📊 Hướng dẫn kết nối Power BI với Supabase

Để trực quan hóa dữ liệu tuyển dụng đã lưu trên Supabase bằng Power BI:

### 1. Lấy thông tin kết nối từ Supabase
Truy cập vào Supabase Dashboard, chọn dự án của bạn và vào mục **Project Settings** -> **Database**:
- **Host**: ví dụ `aws-1-ap-southeast-2.pooler.supabase.com`
- **Port**: `5432`
- **Database Name**: `postgres`
- **User**: `postgres.xxxxxx` (User đăng nhập database)
- **Password**: Mật khẩu database của dự án bạn đã khởi tạo ban đầu

### 2. Thiết lập trên Power BI Desktop
1. Mở phần mềm **Power BI Desktop** trên máy tính.
2. Tại màn hình chính, chọn **Get Data** -> **PostgreSQL database**.
3. Điền các tham số kết nối:
   - **Server**: Nhập `<Host>:<Port>` (Ví dụ: `aws-1-ap-southeast-2.pooler.supabase.com:5432`)
   - **Database**: `postgres`
   - Chọn chế độ kết nối dữ liệu (**Data Connectivity mode**):
     - **Import**: Tải toàn bộ dữ liệu hiện tại về Power BI (Khuyên dùng vì xử lý biểu đồ nhanh hơn).
     - **DirectQuery**: Kết nối thời gian thực trực tiếp đến Database mỗi khi tương tác biểu đồ.
4. Ở màn hình điền thông tin xác thực, chọn tab **Database** ở cột bên trái:
   - **User name**: Nhập **User** của Supabase.
   - **Password**: Nhập mật khẩu cơ sở dữ liệu.
5. Nhấn **Connect**. Nếu hiển thị hộp thoại cảnh báo về kết nối bảo mật (Encryption), nhấn **OK** hoặc **Run** để tiếp tục.
6. Khi kết nối thành công, danh sách các bảng như `jobs`, `skills`, `job_skills`, `job_locations`... sẽ hiện lên trong cửa sổ Navigator. Bạn chọn các bảng cần phân tích, rồi nhấn **Load** để bắt đầu thiết kế dashboard và phân tích dữ liệu tuyển dụng IT.

## Dashboard PowerBI
![alt text](image.png)