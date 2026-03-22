# Phân tích Thuật toán Cluster Pruning (Tìm kiếm theo cụm)

Bản phân tích kỹ thuật cho bài thực hành số 5: Tối ưu hóa tốc độ tìm kiếm bằng kỹ thuật Cluster Pruning.

---

## 1. Giới thiệu bài toán (Overview)

Mục tiêu chính là cải thiện tốc độ truy vấn trong hệ thống tìm kiếm thông tin có số lượng tài liệu lớn. Thay vì so khớp truy vấn với tất cả tài liệu ($|D|$), chúng ta phân nhóm (cluster) các tài liệu lại và chỉ thực hiện tìm kiếm trên các nhóm có tiềm năng chứa kết quả cao nhất.

### Thông số cấu hình
*   **Độ đo tương tự**: Cosine Similarity (Khoảng cách Cosine).
*   **Số lượng cụm (k)**: $\sqrt{|D|}$, với $D$ là tập tài liệu.
*   **Chiến lược phân bổ**: Mỗi tài liệu (follower) được gán vào **2 cụm** gần nhất (dựa trên 2 leaders gần nhất).
*   **Dữ liệu đầu vào**: `thuc_hanh_05\dataset _B5_1`.

---

## 2. Quy trình thực hiện (Implementation Workflow)

### Giai đoạn 1: Xây dựng chỉ mục (Indexing / Clustering)

```mermaid
graph TD
    A[Bắt đầu] --> B[Trích xuất văn bản từ đa định dạng]
    B --> C[Tiền xử lý & Vectơ hóa TF-IDF]
    C --> D[Chọn ngẫu nhiên sqrt|D| Leaders]
    D --> E[Với mỗi Follower d thuộc D]
    E --> F[Tính Cosine với tất cả Leaders]
    F --> G[Chọn 2 Leaders gần nhất]
    G --> H[Gán d vào 2 cụm tương ứng]
    H --> I[Lưu cấu trúc Inverted Cluster Index]
    I --> J[Kết thúc Giai đoạn 1]
```

1.  **Tiền xử lý văn bản**:
    *   Trích xuất nội dung từ các định dạng file (`.doc`, `.docx`, `.pdf`, `.html`).
    *   Tokenization (Sử dụng `underthesea` hoặc `PyVi` cho tiếng Việt).
    *   Loại bỏ Stopwords và chuẩn hóa văn bản.
2.  **Biểu diễn Vector**:
    *   Sử dụng mô hình Vector Space Model (TF-IDF).
3.  **Tạo các cụm (Clustering)**:
    *   **Bước 1**: Chọn ngẫu nhiên $k = \sqrt{|D|}$ tài liệu để làm **Leaders**.
    *   **Bước 2**: Với mỗi tài liệu còn lại (gọi là **Followers**):
        *   Tính độ tương tự Cosine với tất cả các Leaders.
        *   Xác định 2 Leaders có độ tương tự cao nhất.
        *   Gán Follower đó vào danh sách "Followers" của 2 Leaders này.
    *   **Bước 3**: Lưu cấu trúc cụm này vào bộ nhớ hoặc file (Inverted Cluster Index).

---

## 3. Giai đoạn 2: Tìm kiếm nhanh (Fast Search Phase)

Khi nhận được một truy vấn (Query) từ người dùng:

1.  **Vectơ hóa truy vấn**: Chuyển đổi truy vấn thành vectơ TF-IDF trong cùng không gian với các tài liệu.
2.  **Tìm Leaders tương đồng**:
    *   Tính độ tương tự Cosine giữa vectơ truy vấn và tất cả các **Leaders**.
    *   Chọn ra **2 Leaders** có điểm số cao nhất.
3.  **Lọc dữ liệu tìm kiếm**:
    *   Lấy tập hợp tất cả các Follower thuộc về 2 Leaders đã chọn ở bước trên.
4.  **Tính toán và Xếp hạng**:
    *   Chỉ tính toán độ tương tự Cosine giữa vectơ truy vấn và các Follower trong tập hợp đã lọc.
    *   Sắp xếp kết quả và trả về cho người dùng.

---

## 4. Ưu điểm và Độ phức tạp

### Độ phức tạp (Complexity)
*   **Tìm kiếm thông thường**: $O(|D| \times \text{vec_size})$ (Phải so sánh với mọi tài liệu).
*   **Cluster Pruning**:
    *   So sánh với Leaders: $O(\sqrt{|D|} \times \text{vec_size})$.
    *   So sánh với Followers trong cụm: $O(2 \times \frac{|D|}{\sqrt{|D|}} \times \text{vec_size}) \approx O(\sqrt{|D|} \times \text{vec_size})$.
    *   **Tổng cộng**: $O(\sqrt{|D|})$.

### Ưu điểm (Pros)
*   Giảm đáng kể thời gian phản hồi cho các tập dữ liệu cực lớn.
*   Việc gán một follower vào nhiều cụm (2 cụm) giúp giảm thiểu lỗi "bỏ lỡ" (recall error) khi truy vấn nằm ở biên giữa các cụm.

---

## 5. Danh sách thư viện cần thiết

Dựa trên requirements hiện tại:
*   `python-docx`: Xử lý file `.docx`.
*   `pdfminer.six`: Trích xuất dữ liệu từ PDF.
*   `beautifulsoup4`: Xử lý file HTML.
*   `numpy` & `scipy`: Tính toán vectơ và Cosine Similarity.
*   `py_vncorenlp`: Xử lý ngôn ngữ tự nhiên tiếng Việt.
*   `gensim`: Hỗ trợ quản lý dữ liệu và TF-IDF.

---

## 6. Ghi chú triển khai
*   Cần xử lý ngoại lệ cho file định dạng `.doc` (Word 97-2003) vì `python-docx` chủ yếu hỗ trợ `.docx`. Có thể sử dụng `antiword` hoặc chuyển đổi sang định dạng khác nếu cần.
*   Việc chọn Leaders có thể thực hiện ngẫu nhiên hoặc có thể cải tiến bằng cách chọn các tài liệu phân tán đều trong không gian vectơ.
