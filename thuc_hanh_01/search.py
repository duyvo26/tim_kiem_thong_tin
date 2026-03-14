"""
search.py — Demo tìm kiếm sử dụng bộ chỉ mục nghịch đảo.

Luồng hoạt động:
  1. Nạp dictionary.txt vào RAM (1 lần)
  2. Nhận truy vấn từ người dùng
  3. Tách từ truy vấn bằng VnCoreNLP + lọc stop words
  4. Với mỗi từ trong truy vấn:
       - Tra dictionary → lấy IDF, Offset
       - file.seek(Offset) vào invertedIndex.txt → lấy danh sách (docId, TF)
       - Tính TF-IDF = TF × IDF
  5. Cộng dồn điểm TF-IDF theo từng tài liệu → xếp hạng → hiển thị kết quả
"""

import os
import collections
import py_vncorenlp

# ─── Cấu hình đường dẫn ──────────────────────────────────────────────────────
DIR_ROOT         = os.path.dirname(os.path.abspath(__file__))
DICT_FILE        = os.path.join(DIR_ROOT, "dictionary.txt")
INDEX_FILE       = os.path.join(DIR_ROOT, "invertedIndex.txt")
STOPWORDS_FILE   = os.path.join(DIR_ROOT, "vietnamese-stopwords.txt")
VNCORENLP_DIR    = os.path.join(DIR_ROOT, "vncorenlp")
JAVA_HOME        = r"C:\Program Files\Java\jdk1.8.0_202"

os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PATH"]      = JAVA_HOME + r"\bin;" + os.environ["PATH"]

TOP_K = 5  # số kết quả trả về


# ─── Khởi tạo model (1 lần) ──────────────────────────────────────────────────
print("Đang nạp mô hình VnCoreNLP...")
model = py_vncorenlp.VnCoreNLP(save_dir=VNCORENLP_DIR, annotators=["wseg"])


# ─── 1. Nạp dictionary.txt vào RAM ───────────────────────────────────────────
def load_dictionary(path: str) -> dict:
    """Trả về dict: term → {"df": int, "offset": int}"""
    dictionary = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3 or parts[0] == "Term":
                continue
            term = parts[0]
            try:
                df     = int(parts[1])
                offset = int(parts[2])
            except ValueError:
                continue
            dictionary[term] = {"df": df, "offset": offset}
    return dictionary


# ─── 2. Nạp stop words ───────────────────────────────────────────────────────
def load_stopwords(path: str) -> set:
    with open(path, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


# ─── 3. Tách từ truy vấn ─────────────────────────────────────────────────────
def tokenize_query(query: str, stopwords: set) -> list[str]:
    result   = model.annotate_text(query)
    sentences = result.values() if isinstance(result, dict) else result
    tokens   = []
    for sentence in sentences:
        for token in sentence:
            word = token["wordForm"].lower()
            if word not in stopwords:
                tokens.append(word)
    return tokens


# ─── 4. Tìm kiếm ─────────────────────────────────────────────────────────────
def search(query_tokens: list[str], dictionary: dict, index_path: str) -> list[tuple]:
    """
    Trả về danh sách (doc_id, score) đã sắp xếp giảm dần theo tổng điểm TF-IDF.
    """
    scores = collections.defaultdict(float)

    with open(index_path, "rb") as f_bin:
        for token in query_tokens:
            if token not in dictionary:
                print(f"  [!] '{token}' không có trong chỉ mục — bỏ qua")
                continue

            meta = dictionary[token]
            f_bin.seek(meta["offset"])
            raw_line = f_bin.readline().decode("utf-8").rstrip("\n")

            # Tách IDF và posting list
            parts = raw_line.split("\t", 1)
            if len(parts) < 2:
                continue

            idf      = float(parts[0])
            postings = parts[1].split(" ") if parts[1] else []

            for p in postings:
                if ":" not in p:
                    continue
                doc_id, tf_str = p.split(":", 1)
                tf    = int(tf_str)
                tfidf = tf * idf          # tính TF-IDF on-the-fly
                scores[doc_id] += tfidf

    # Xếp hạng giảm dần
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Đang nạp dictionary vào RAM...")
    dictionary = load_dictionary(DICT_FILE)
    stopwords  = load_stopwords(STOPWORDS_FILE)
    print(f"  → {len(dictionary)} term trong chỉ mục\n")

    print("=" * 60)
    print("  SEARCH ENGINE — Tìm kiếm tài liệu tiếng Việt")
    print("  Gõ 'exit' để thoát")
    print("=" * 60)

    while True:
        query = input("\nNhập truy vấn: ").strip()
        if query.lower() in ("exit", "quit", "q"):
            print("Thoát.")
            break
        if not query:
            continue

        # Tách từ
        tokens = tokenize_query(query, stopwords)
        if not tokens:
            print("  Không có từ hợp lệ sau khi lọc stop words.")
            continue

        print(f"  Từ khóa: {tokens}")

        # Tìm kiếm
        results = search(tokens, dictionary, INDEX_FILE)

        if not results:
            print("  Không tìm thấy tài liệu nào.")
        else:
            print(f"\n  Top {min(TOP_K, len(results))} kết quả:")
            print(f"  {'Hạng':<6} {'Tài liệu':<20} {'Điểm TF-IDF'}")
            print(f"  {'-'*45}")
            for rank, (doc_id, score) in enumerate(results[:TOP_K], 1):
                print(f"  {rank:<6} {doc_id:<20} {score:.5f}")
