# Buổi 1 – Xây dựng tập chỉ mục nghịch đảo

**Môn:** Tìm kiếm thông tin  
**Sinh viên:** Võ Khương Duy

---

## Mô tả

Script `main.py` đọc toàn bộ tài liệu trong thư mục `dataset/`, tách từ tiếng Việt bằng **VnCoreNLP**, lọc stop words, rồi xây dựng bộ chỉ mục nghịch đảo lưu ra 2 file `.txt`.

---

## Định dạng tập tin đầu vào

| Định dạng | Thư viện xử lý |
|---|---|
| `*.doc`, `*.docx` | `python-docx` |
| `*.pdf` | `pdfminer` |
| `*.html`, `*.htm` | `crawl4ai` |

---

## Cấu trúc 2 file đầu ra

### 1. `dictionary.txt` — Từ điển tra cứu

Mỗi dòng lưu thông tin của **1 từ**, các trường phân cách bằng **Tab (`\t`)**:

```
Term    DF    Offset
```

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `Term` | string | Từ đã tách và chuẩn hoá (chữ thường) |
| `DF` | int | Document Frequency — số tài liệu chứa từ này |
| `Offset` | int | Vị trí byte trong `invertedIndex.txt` để `seek()` trực tiếp đến dòng posting list tương ứng |

**Ví dụ:**
```
Term            DF    Offset
windows_xp      5     0
kết_thúc        4     100
máy_tính        7     182
```

---

### 2. `invertedIndex.txt` — Danh sách posting (Posting List)

Mỗi dòng ứng với **1 từ** trong `dictionary.txt` (theo đúng thứ tự), các trường phân cách bằng **Tab (`\t`)**. Trong từng dòng, các posting entry phân cách bằng **dấu cách**:

```
IDF    docId1:TF-IDF1 docId2:TF-IDF2 ...
```

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `IDF` | float (5 chữ số thập phân) | Inverse Document Frequency = `log₁₀(N / DF)`, N là tổng số tài liệu |
| `docId:TF` | string:int | Tên file tài liệu và **TF thô** (số lần từ xuất hiện trong tài liệu đó) |

> **Lý do không lưu TF×IDF:** Khi corpus được cập nhật thêm tài liệu mới, N thay đổi → IDF thay đổi toàn bộ → mọi giá trị TF×IDF đã lưu đều sai (stale). Lưu TF thô đảm bảo dữ liệu luôn đúng; TF-IDF sẽ được tính on-the-fly lúc tìm kiếm: `TF-IDF = TF × IDF`.

**Ví dụ:**
```
0.30103    1001.docx:3 1005.pdf:6 1003.docx:9
0.39794    1002.docx:2 1004.docx:1
0.15490    1001.docx:3 1003.docx:2 1006.pdf:1
```

---

## Cách 2 file phối hợp khi tìm kiếm

```
Bước 1: Nạp toàn bộ dictionary.txt vào RAM (1 lần, lúc khởi động)

Bước 2: Với mỗi từ khóa truy vấn:
         Tra dictionary → lấy Offset
         file.seek(Offset) vào invertedIndex.txt
         Đọc đúng 1 dòng → lấy IDF và danh sách (docId, TF-IDF)
         Không cần đọc toàn bộ invertedIndex.txt
```

> **Lưu ý:** Tổng số tài liệu N **không lưu vào file** vì IDF đã được tính sẵn lúc indexing. Khi corpus thay đổi (thêm/bớt tài liệu), cần chạy lại `main.py` để tạo lại toàn bộ chỉ mục.

---

## Giải thuật tạo chỉ mục — One Pass Indexing

Mỗi tài liệu chỉ được **đọc đúng 1 lần duy nhất**:

1. Đọc nội dung file → tách từ (VnCoreNLP) → lọc stop words → đếm TF
2. Tích lũy kết quả vào cấu trúc trung gian `inverted_index_raw` trong RAM: `term → {docId: TF}`
3. Sau khi xử lý hết toàn bộ tài liệu, tính IDF và TF-IDF, ghi ra 2 file một lần duy nhất

---

## Chạy chương trình

```bash
python main.py
```

Kết quả sinh ra `dictionary.txt` và `invertedIndex.txt` trong thư mục gốc của project.
