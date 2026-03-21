# GooSearch - Hệ thống Tìm kiếm Thông tin (VSM Model)

Dự án thực hành tìm kiếm thông tin sử dụng Mô hình Không gian Vector (Vector Space Model - VSM), hỗ trợ tách từ tiếng Việt chuẩn xác và tìm kiếm mệnh đề (Phrase Search).

**Sinh viên thực hiện:** Võ Khương Duy - 2513464

---

## Tính năng chính

- **Lập chỉ mục theo vị trí (Positional Indexing)**: Cho phép tìm kiếm cụm từ chính xác.
- **Xếp hạng tài liệu (Ranking)**: Sử dụng trọng số TF-IDF và độ đo Cosine Similarity.
- **Tìm kiếm đa dạng**:
  - **Chương 1**: Truy vấn từ khóa thông thường (AND logic).
  - **Chương 2**: Truy vấn dạng mệnh đề (Phrase Search - đặt trong dấu ngoặc kép " ").
- **Giao diện hiện đại**: Thiết kế theo phong cách GooSearch, chuẩn tối giản, mượt mà.
- **Tách từ tiếng Việt**: Tích hợp thư viện VnCoreNLP mạnh mẽ.

---

## Cấu trúc dự án

- `/app`: Mã nguồn Backend (FastAPI).
- `/frontend`: Mã nguồn Frontend (React + Vite + TailwindCSS).
- `/dataset`: Thư mục chứa các tài liệu cần lập chỉ mục (.pdf, .docx, .html).
- `/vncorenlp`: Chứa model tách từ của VnCoreNLP.
- `dictionary.txt`, `invertedIndex.txt`: Các tệp lưu trữ chỉ mục sau khi xử lý.

---

## Hướng dẫn cài đặt

### 1. Chuẩn bị môi trường
- Đã cài đặt **Python 3.10+**.
- Đã cài đặt **Node.js 18+**.
- Đã cài đặt **Java (JDK 8 trở lên)** để chạy VnCoreNLP.

### 2. Cài đặt Backend
1. Tạo môi trường ảo (khuyến nghị):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Cài đặt các thư viện:
   ```bash
   pip install -r requirements.txt
   ```
3. Cấu hình file `.env` (nếu cần thiết để trỏ đường dẫn Java):
   ```env
   JAVA_HOME="C:\Program Files\Java\jdk1.8.0_202"
   ```

### 3. Cài đặt Frontend
1. Di chuyển vào thư mục frontend:
   ```bash
   cd frontend
   ```
2. Cài đặt dependencies:
   ```bash
   npm install
   ```

---

## Hướng dẫn khởi chạy

### Bước 1: Chạy Backend API
Từ thư mục gốc dự án:
```powershell
.\run_api.py
```
*API sẽ chạy tại: `http://localhost:3005`*

### Bước 2: Chạy Frontend (Giao diện)
Từ thư mục `/frontend`:
```bash
npm run dev
```
*Truy cập giao diện tại: `http://localhost:3000`*

---

## Cách sử dụng

1. **Lập chỉ mục dữ liệu lần đầu**:
   - Nhấn nút **"Hệ thống: Lập lại chỉ mục"** ở dưới Footer của trang web để hệ thống quét toàn bộ tệp trong thư mục `/dataset`.
2. **Tìm kiếm thông thường**:
   - Nhập từ khóa: `windows nâng cấp`
3. **Tìm kiếm mệnh đề**:
   - Nhập cụm từ trong ngoặc kép: `"gỡ các chương trình"`

---

## Công nghệ sử dụng
- **Backend**: FastAPI, py-vncorenlp, BeautifulSoup4, pdfminer.six, python-docx.
- **Frontend**: React 19, Vite, TailwindCSS, Lucide Icons, Sonner (Notifications), Motion (Animations).
- **Hệ thống**: Java (cho word segmentation).

---
© 2024 - Project thực hành môn Tìm kiếm Thông tin.
