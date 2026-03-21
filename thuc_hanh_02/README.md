# GooSearch - Simple Web Search Engine

GooSearch là một hệ thống công tìm kiếm tài liệu (Web Search Engine) đơn giản được xây dựng dựa trên Mô hình Không gian Vector (Vector Space Model). Dự án này là một phần của bài thực hành "Tìm kiếm thông tin" (Information Retrieval) - Buổi 2.

## Tính năng chính

### Backend (FastAPI)
- Lập chỉ mục theo vị trí (Positional Indexing): Lưu trữ vị trí của các từ trong tài liệu để phục vụ tìm kiếm cụm từ (Phrase Search).
- Trọng số TF-IDF: Tính toán trọng số từ dựa trên tần suất xuất hiện (Term Frequency) và nghịch đảo tần suất tài liệu (Inverse Document Frequency).
- Độ đo tương đồng Cosine (Cosine Similarity): Xếp hạng tài liệu dựa trên góc giữa vector truy vấn và vector tài liệu.
- Tách từ Tiếng Việt (Tokenization): Tách từ bằng thư viện VnCoreNLP để xử lý ngôn ngữ Tiếng Việt chính xác.
- Hỗ trợ đa định dạng: Có thể đọc và lập chỉ mục cho các tệp .pdf, .docx, .html.

### Frontend (React + Vite)
- Giao diện Google-like: Thiết kế tối giản, hiện đại, tích hợp Smooth Animations từ Framer Motion.
- Phân trang (Pagination): Chỉ hiển thị 10 tài liệu phù hợp nhất trên mỗi trang.
- Tự động nhận dạng Search Mode:
  - Nhập từ khóa thông thường: Tìm kiếm từ khóa (Keyword Search).
  - Nhập cụm từ trong dấu ngoặc kép "..." : Tìm kiếm mệnh đề (Phrase Search) dựa trên vị trí từ.
- Hộp thoại xác nhận hiện đầu: Thay thế các Alert mặc định bằng Modal đẹp mắt với motion/react.
- Thông báo Real-time: Sử dụng sonner để hiển thị trạng thái xử lý của hệ thống.

## Công nghệ sử dụng

- Backend: Python 3.10+, FastAPI, PyVnCoreNLP, Java 8 (cho VnCoreNLP).
- Frontend: React 19, TypeScript, Vite, Tailwind CSS, Framer Motion, Lucide Icons.
- Dataset: Lưu trữ tại thư mục /dataset.

## Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
- Đã cài đặt Python 3.10+.
- Đã cài đặt Node.js và npm.
- Đã cài đặt Java JDK 8 (để chạy VnCoreNLP).

### 2. Cài đặt Backend
1. Cài đặt các thư viện từ server:
   ```bash
   pip install -r requirements.txt
   ```
2. Cấu hình đường dẫn Java trong app/config.py hoặc .env.
3. Chạy server API:
   ```bash
   python run_api.py
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
3. Khởi động môi trường phát triển:
   ```bash
   npm run dev
   ```

## Cách sử dụng

1. Truy cập: Mở trình duyệt và vào địa chỉ http://localhost:3000.
2. Lập chỉ mục: Nhấp vào nút "Lập lại chỉ mục toàn bộ tài liệu" ở footer để hệ thống quét và xây dựng bộ chỉ mục từ dataset.
3. Tìm kiếm từ khóa: Nhập các từ khóa cách nhau bằng khoảng trắng (Ví dụ: startup manager).
4. Tìm kiếm mệnh đề: Nhập cụm từ trong dấu nháy kép (Ví dụ: "Startup Manager") để tìm chính xác các tài liệu chứa cụm từ này theo đúng thứ tự.

## Thông tin sinh viên
- Họ tên: Võ Khương Duy
- Mã số sinh viên: 2513464
- Môn học: Tìm kiếm thông tin - Mô hình Không gian Vector (VSM)

---
*Dự án được phát triển với mục đích học tập và nghiên cứu các thuật toán IR cơ bản.*
