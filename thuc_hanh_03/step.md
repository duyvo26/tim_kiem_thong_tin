Ok, mình phân tích bài này theo kiểu của dân code để bạn dễ triển khai 👇

---

# 1. Input (đầu vào)

### Dữ liệu chính:

* **Corpus văn bản** (tập dữ liệu từ buổi 1)
* Dữ liệu này cần được:

  * Tách **câu** (vì tài liệu = câu)
  * Tách **từ** (tokenize)
  * Có thể cần:

    * lowercase
    * loại stopword (tùy bạn)

---

### Input logic sau khi xử lý:

```text
[
  ["windows", "xp", "rất", "nhẹ"],
  ["phần", "mềm", "này", "chạy", "tốt"],
  ...
]
```

---

# 2. Output (đầu ra)

Với **mỗi từ (word)**:

👉 Trả về:

```text
word → [top 10 từ đồng xuất hiện]
```

Ví dụ:

```text
"windows" → ["xp", "microsoft", "hệ", "điều", "hành", ...]
"phần mềm" → ["ứng dụng", "cài đặt", "chạy", ...]
```

⚠️ Lưu ý:

* Với method 1: đồng xuất hiện thật (co-occurrence)
* Với method 2: tương đồng ngữ nghĩa (embedding similarity)

---

# 3. Các bước xử lý (core pipeline)

---

# 🚀 PHƯƠNG PHÁP 1: Ma trận đồng xuất hiện

## Bước 1: Tạo vocabulary

```python
vocab = list(set(all_words))
```

---

## Bước 2: Tạo ma trận A (word – sentence)

### Ý nghĩa:

* Hàng: từ
* Cột: câu
* Giá trị:

  * 1: từ xuất hiện trong câu
  * 0: không xuất hiện

```text
        sentence1 sentence2 sentence3
word1      1         0         1
word2      0         1         1
```

---

## Bước 3: Tính ma trận đồng xuất hiện

Áp dụng công thức:

C = A \cdot A^T

👉 Ý nghĩa:

* C[i][j] = số lần từ i và j xuất hiện cùng câu

---

## Bước 4: Lấy top 10 từ

Với mỗi từ:

* Lấy dòng tương ứng trong ma trận C
* Sort giảm dần
* Bỏ chính nó (i != j)
* Lấy top 10

---

## Output method 1:

```python
{
  "windows": ["xp", "microsoft", ...],
  ...
}
```

---

# 🚀 PHƯƠNG PHÁP 2: Word Embedding (CBOW)

---

## Bước 1: Chuẩn bị dữ liệu huấn luyện

Với window size = 3:

👉 Context = 3 từ bên trái + 3 từ bên phải

Ví dụ:

```text
["tôi", "dùng", "windows", "xp", "rất", "lâu"]
```

Target = "xp"

Context:

```text
["tôi", "dùng", "windows", "rất", "lâu"]
```

---

## Bước 2: Train Word2Vec (CBOW)

Dùng thư viện:

* `gensim`

```python
from gensim.models import Word2Vec

model = Word2Vec(
    sentences=data,
    vector_size=100,
    window=3,
    sg=0  # CBOW
)
```

---

## Bước 3: Lấy từ tương đồng

```python
model.wv.most_similar("windows", topn=10)
```

---

## Output method 2:

```python
{
  "windows": ["xp", "microsoft", "os", ...]
}
```

---

# 4. So sánh 2 phương pháp

| Tiêu chí | Ma trận C             | Word2Vec |
| -------- | --------------------- | -------- |
| Dễ làm   | ✅                     | ❌        |
| Tốc độ   | ❌ chậm với vocab lớn  | ✅        |
| Ý nghĩa  | literal co-occurrence | semantic |
| Bộ nhớ   | ❌ rất lớn             | ✅ nhỏ    |

---

# 5. Các bước tổng thể (flow chuẩn)

```text
1. Load dataset
2. Tiền xử lý (tokenize, tách câu)

--- Method 1 ---
3. Build vocab
4. Build matrix A
5. Compute C = A * A^T
6. Extract top 10

--- Method 2 ---
7. Train Word2Vec (CBOW, window=3)
8. Query most_similar()

9. Test với:
   - "window xp"
   - "phần mềm"

10. Ghi nhận kết quả
```

---

# 6. Điểm dễ bị trừ (cực quan trọng)

* ❌ Không tách câu đúng
* ❌ Không đúng window = 3
* ❌ Không loại chính nó khỏi top 10
* ❌ Không so sánh kết quả 2 phương pháp
* ❌ Không test đúng từ đề yêu cầu:

  * `"window xp"`
  * `"phần mềm"`

---

