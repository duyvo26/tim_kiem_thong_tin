# 🔍 Hệ Thống Tìm Kiếm Nhanh Với Cluster Pruning

Hệ thống cung cấp giải pháp tìm kiếm thông tin hiệu năng cao dựa trên kỹ thuật **Cluster Pruning** (Tỉa nhánh cụm), giúp giảm khối lượng tính toán nhưng vẫn đảm bảo kết quả phù hợp.

---

## 🏗️ Sơ Đồ Quy Trình Hoạt Động

### 1. Giai đoạn Chỉ mục (Indexing Phase)
Hệ thống chọn ngẫu nhiên các "Leader" và phân nhóm các "Follower" vào các cụm gần nhất.

```mermaid
graph TD
    A[Dataset: .docx, .pdf, .html] --> B[Tiền xử lý & Tách từ tiếng Việt]
    B --> C[Xây dựng mô hình TF-IDF]
    C --> D[Chọn ngẫu nhiên sqrt|N| Leaders]
    D --> E[Gán mỗi Followers vào 2 cụm gần nhất]
    E --> F[Lưu trữ Index.pkl Cache]
```

### 2. Giai đoạn Truy vấn (Search Phase)
Thay vì so khớp toàn bộ, hệ thống chỉ tìm kiếm trong "vùng tiềm năng" cực nhỏ.

```mermaid
graph LR
    Q[Truy vấn người dùng] --> V[Vector hóa TF-IDF]
    V --> L[Tìm 2 Leaders gần nhất]
    L --> P[Tỉa nhánh: Chỉ lấy Followers thuộc cụm này]
    P --> R[Xếp hạng Cosine & Trả kết quả]
```

---

## 🛠️ Cấu Trúc Các Thành Phần (Classes)

Hệ thống được thiết kế theo hướng đối tượng (OOP) với 5 lớp chính:

1.  **`DocumentDataLoader`**: Nạp dữ liệu đa định dạng từ thư mục dataset.
2.  **`TextProcessor`**: Xử lý ngôn ngữ, tách từ (Word Segmentation) và lọc stopwords.
3.  **`VectorModel`**: Quản lý bộ từ điển và tính toán trọng số TF-IDF, Cosine Similarity.
4.  **`ClusterPruningIndexer`**: Thực hiện giải thuật phân cụm $\sqrt{N}$ và gán tài liệu vào các leader.
5.  **`SearchHandler`**: Điều phối quy trình tìm kiếm nhanh (Fast Search) và xếp hạng kết quả.

---

## ⚡ Tính Năng Nổi Bật

- **Tối ưu hóa tốc độ**: Sử dụng cơ chế Pruning giúp giảm tới 60-80% khối lượng tính toán so với tìm kiếm tuyến tính.
- **Cơ chế Cache**: Tự động lưu chỉ mục vào `index.pkl` sau lần chạy đầu tiên, giúp các lần sau khởi động tức thì mà không cần nạp lại mô hình NLP nặng.
- **Hỗ trợ đa định dạng**: Chế độ đọc file thông minh cho `.pdf`, `.docx`, `.doc` và `.html`.

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Cài đặt môi trường
Đảm bảo bạn đã cài đặt các thư viện cần thiết:
```bash
pip install numpy gensim python-docx pdfminer.six beautifulsoup4 py_vncorenlp
```

### 2. Chạy chương trình
```bash
python cluster_pruning.py
```

### 3. Xem báo cáo
Sau mỗi lần chạy, kết quả tìm kiếm sẽ được tự động cập nhật vào file `report_05.md`.

---
*Thực hiện bởi: [Họ tên của bạn]*
*Khóa học: Tìm kiếm thông tin - Thạc sĩ*
