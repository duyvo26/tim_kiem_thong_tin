"""
Script kiểm tra tính hợp lệ của bộ chỉ mục gồm 2 file:

  dictionary.txt    — mỗi dòng: <Term>\t<DF>\t<Offset_byte>
  invertedIndex.txt — mỗi dòng: <IDF>\t<docId1>:<TF1> <docId2>:<TF2> ...

TF-IDF = TF × IDF được tính on-the-fly ở bước tìm kiếm,
không lưu sẵn để tránh bị stale khi corpus được cập nhật thêm tài liệu mới.
"""

import os

DICT_FILE  = "dictionary.txt"
INDEX_FILE = "invertedIndex.txt"

# ─────────────────────────────────────────────
# 1. Đọc dictionary.txt
# ─────────────────────────────────────────────
def load_dictionary():
    """Trả về dict: term -> {df, idf, offset}"""
    dictionary = {}
    with open(DICT_FILE, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            parts = line.rstrip("\n").split("\t")

            # Bỏ qua dòng tiêu đề hoặc dòng rỗng
            if not parts or parts[0] == "Term":
                continue

            if len(parts) < 3:
                print(f"[LỖI] dictionary.txt dòng {lineno}: thiếu cột — {line.rstrip()!r}")
                continue

            term = parts[0]
            try:
                df     = int(parts[1])
                offset = int(parts[2])
            except ValueError as e:
                print(f"[LỖI] dictionary.txt dòng {lineno}: giá trị không hợp lệ — {e}")
                continue

            dictionary[term] = {"df": df, "offset": offset}

    return dictionary


# ─────────────────────────────────────────────
# 2. Kiểm tra invertedIndex.txt bằng Offset
# ─────────────────────────────────────────────
def check_index(dictionary):
    errors    = 0
    checked   = 0

    with open(INDEX_FILE, "rb") as f_bin:           # mở binary để seek byte chính xác
        for term, meta in dictionary.items():
            f_bin.seek(meta["offset"])               # nhảy thẳng đến dòng posting
            raw_line = f_bin.readline().decode("utf-8").rstrip("\n")

            if not raw_line:
                print(f"[LỖI] Không đọc được posting list tại offset {meta['offset']} cho term '{term}'")
                errors += 1
                continue

            # Tách IDF ở đầu dòng và posting list (phân cách bằng Tab)
            parts = raw_line.split("\t", 1)
            if len(parts) < 2:
                print(f"[LỖI] invertedIndex.txt: dòng thiếu IDF tại offset {meta['offset']}")
                errors += 1
                continue

            idf      = float(parts[0])
            postings = parts[1].split(" ") if parts[1] else []

            # Kiểm tra số lượng posting == DF
            if len(postings) != meta["df"]:
                print(
                    f"[CẢNH BÁO] DF mismatch '{term}': "
                    f"dictionary DF={meta['df']}, nhưng index có {len(postings)} postings"
                )
                errors += 1

            # Kiểm tra định dạng từng posting entry
            for p in postings:
                if ":" not in p:
                    print(f"[LỖI] Posting sai format tại '{term}': {p!r}")
                    errors += 1
                    continue

                doc_id, tf_str = p.split(":", 1)
                try:
                    tf    = int(tf_str)
                    tfidf = tf * idf   # tính on-the-fly
                except ValueError:
                    print(f"[LỖI] TF không phải số nguyên tại '{term}' doc='{doc_id}': {tf_str!r}")
                    errors += 1
                    continue

                print(
                    f"  {term:30s}  ->  {doc_id:15s}  "
                    f"TF={tf}  IDF={idf:.5f}  TF-IDF={tfidf:.5f}"
                )

            checked += 1

    print(f"\n{'='*60}")
    print(f"Số term đã kiểm tra : {checked}")
    print(f"Số lỗi phát hiện    : {errors}")
    if errors == 0:
        print("✅ Bộ chỉ mục hợp lệ hoàn toàn!")
    else:
        print("❌ Có lỗi cần xem xét.")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(DICT_FILE) or not os.path.exists(INDEX_FILE):
        print("Chưa tìm thấy dictionary.txt hoặc invertedIndex.txt.")
        print("Hãy chạy main.py trước để tạo bộ chỉ mục.")
    else:
        dictionary = load_dictionary()
        print(f"Đã nạp {len(dictionary)} term từ dictionary.txt\n")
        check_index(dictionary)