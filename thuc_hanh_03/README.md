# Thực hành 03: Xây dựng Danh mục Từ đồng xuất hiện

Bài tập này triển khai việc tìm kiếm 10 từ đồng xuất hiện cao nhất của một từ truy vấn bằng hai phương pháp: **Ma trận đồng xuất hiện truyền thống** và **Nhúng từ (Word Embedding) với CBOW**.

---

## Sơ đồ hoạt động (Workflow)

```mermaid
graph TD
    A[Dữ liệu thô - Dataset] --> B[Đọc file & Tiền xử lý]
    B --> C[Tokenize bằng VnCoreNLP]
    
    C --> D[Lọc bỏ Stopwords]
    D --> E[Tách thành danh sách Câu & Các Từ]
    
    E --> F1[Phương pháp 1: Ma trận Co-occurrence]
    E --> F2[Phương pháp 2: Word2Vec CBOW]
    
    F1 --> G1[Tính C = A * A^T]
    G1 --> H1[Trích xuất Top 10 Co-occurrence]
    
    F2 --> G2[Huấn luyện model CBOW window=3]
    G2 --> H2[Tính Cosine Similarity]
    
    H1 --> I[So khớp Truy vấn Người dùng]
    H2 --> I
    
    I --> J{Có trong Từ điển?}
    J -- Có --> K[In danh sách Top 10]
    J -- Không --> L[Dừng lại, Báo Lỗi Out-Of-Vocabulary]
    K --> M[Xuất báo cáo JSON/Markdown]
    
    style J fill:#f9f,stroke:#333,stroke-width:2px;
    style L fill:#f66,stroke:#333,stroke-width:2px;
```

---

## Yêu cầu hệ thống & Cài đặt

### 1. Yêu cầu phần mềm
*   **Python**: Phiên bản 3.9+ 
*   **Java**: JDK 1.8+ (Bắt buộc để chạy VnCoreNLP)
*   Thư viện: `numpy`, `scipy`, `gensim`, `py_vncorenlp`, `python-docx`, `pdfminer.six`, `beautifulsoup4`.

### 2. Cài đặt môi trường
1.  **Cấu hình Java**: Đảm bảo đường dẫn `JAVA_HOME` trong file `utils.py` trỏ đúng vào thư mục cài đặt JDK của bạn.
2.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```

---

## Hướng dẫn chạy chương trình

Để thực hiện toàn bộ quy trình và xem kết quả, bạn chỉ cần chạy file main:

```bash
python main.py
```

### Kết quả đầu ra:
*   `results.json`: Chứa kết quả thô dạng JSON.
*   `results.md`: Báo cáo so sánh Top 10 từ của 2 phương pháp dưới dạng bảng.
*   `word2vec_cbow.model`: Model Word2Vec đã được huấn luyện.

---

## Mô tả kỹ thuật

### Phương pháp 1: Ma trận đồng xuất hiện
*   **Ma trận A (Binary)**: Mỗi hàng là một từ, mỗi cột là một câu. Giá trị là 1 nếu từ xuất hiện trong câu.
*   **Ma trận C**: Kết quả của phép nhân $A \times A^T$. Phần tử $C[i][j]$ cho biết số lần từ $i$ và từ $j$ cùng xuất hiện trong một câu.

### Phương pháp 2: Word2Vec (CBOW)
*   Sử dụng mô hình **Continuous Bag of Words** (CBOW).
*   **Kích thước cửa sổ (Window size)**: 3 (xem xét 3 từ trước và 3 từ sau).
*   Ý nghĩa: Tìm các từ có sự tương đồng về mặt ngữ nghĩa (semantic similarity) dựa trên ngữ cảnh xung quanh thay vì chỉ đếm số lần xuất hiện thuần túy.

---

## Cơ chế Truy vấn cốt lõi
Hệ thống được thiết kế theo tư duy nền tảng của các thuật toán Xử lý ngôn ngữ tự nhiên cơ bản:

1.  **Strict Search (Tìm kiếm Tuyệt đối)**: 
    Lấy duy nhất token đầu tiên (từ khóa chính) được tách ra bởi bộ xử lý (VnCoreNLP) vào đối chiếu. Hệ thống đi tìm một cách chính xác tuyệt đối chữ đó trong `dictionary.txt`. 
2.  **Không Fallback (Bảo vệ thông tin)**:
    Nếu từ khóa đầu tiên không khớp/ nhập sai, hệ thống dừng quy trình và báo lỗi liền chứ không lấy chữ thứ hai bù vào. Nếu bạn nhập `"window"`, không có trong kho (do kho là `"windows"`), máy sẽ báo `Không tìm thấy` chứ không tự tiện sửa chữ. Sự nghiêm ngặt này bám đúng theo yêu cầu không làm sai lệch truy vấn (No-Coercement).

---
*Bản quyền thực hành: Tìm kiếm thông tin - Chương trình Thạc sĩ*
