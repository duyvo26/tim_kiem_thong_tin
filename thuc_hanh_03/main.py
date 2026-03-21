"""
Thực hành 03 – Main Script
===========================
Chạy 2 phương pháp tìm từ đồng xuất hiện:
  1. Ma trận đồng xuất hiện (C = A × A^T)
  2. Word Embedding – Word2Vec CBOW (window=3)

Thử nghiệm với 2 từ theo đề bài:
  - "windows xp"  (VnCoreNLP thường tách thành 2 token: windows / xp)
  - "phần mềm"   (VnCoreNLP thường ghép: phần_mềm)

Cách chạy:
    cd thuc_hanh_03
    python main.py
"""

import os
import json
import time

from utils import load_corpus_sentences, DIR_ROOT
from cooccurrence import CoOccurrenceModel
from word_embedding import WordEmbeddingModel


# ─────────────────────────────────────────────────────────────────────────────
# Cấu hình
# ─────────────────────────────────────────────────────────────────────────────
TOPN = 10

# Các từ cần thử nghiệm theo đề bài
TEST_WORDS = [
    "windows_xp",   # VnCoreNLP thường ghép thành token có gạch dưới
    "windows",      # token riêng lẻ (phòng khi không ghép)
    "xp",           # token riêng lẻ
    "phần_mềm",     # VnCoreNLP thường ghép thành phần_mềm
    "phần",         # fallback
    "mềm",          # fallback
]

# Từ truy vấn chính cho báo cáo kết quả
REPORT_QUERIES = {
    "window xp": ["windows_xp", "windows xp", "xp", "windows"],
    "phần mềm":  ["phần_mềm",  "phần mềm"],
}

OUTPUT_JSON = os.path.join(DIR_ROOT, "results.json")
OUTPUT_MD   = os.path.join(DIR_ROOT, "results.md")


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────
def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(label: str, word: str, results: list[tuple[str, float]]):
    print(f"\n  [{label}] Top-{TOPN} từ đồng xuất hiện của '{word}':")
    if not results:
        print("    (Không tìm thấy – từ không có trong vocabulary)")
    else:
        for rank, (w, score) in enumerate(results, 1):
            print(f"    {rank:>2}. {w:<25} score = {score:.4f}")


def find_best_result(model_obj, queries: list[str], method_name: str) -> tuple[str, list]:
    """
    Thử lần lượt các dạng từ trong `queries`, trả kết quả đầu tiên thấy.
    """
    for q in queries:
        res = model_obj.most_similar(q, topn=TOPN)
        if res:
            return q, res
    return queries[0], []


def export_markdown(all_results: dict, output_path: str):
    """
    Xuất kết quả ra file Markdown dưới dạng bảng để dễ báo cáo.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO KẾT QUẢ THỰC HÀNH 03\n\n")
        f.write("## So sánh Top 10 từ đồng xuất hiện/tương đồng\n\n")

        for label, data in all_results.items():
            f.write(f"### Từ truy vấn: `{label}`\n\n")
            f.write("| STT | Ma trận Đồng xuất hiện (Score) | Word2Vec CBOW (Similarity) |\n")
            f.write("|:---:|:------------------------------|:---------------------------|\n")

            res1 = data["method1_cooccurrence"]["results"]
            res2 = data["method2_word2vec"]["results"]

            # Lấy số lượng tối đa của 2 bên (thường là 10)
            max_len = max(len(res1), len(res2))

            for i in range(max_len):
                m1_txt = f"{res1[i][0]} ({res1[i][1]})" if i < len(res1) else "-"
                m2_txt = f"{res2[i][0]} ({res2[i][1]:.4f})" if i < len(res2) else "-"
                f.write(f"| {i+1} | {m1_txt} | {m2_txt} |\n")
            
            f.write("\n---\n\n")
        
        f.write("\n*Lưu ý: Phương pháp Ma trận tính số lần cùng câu mẫu, Word2Vec tính độ tương đồng cosine trong không gian vector.*\n")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print_header("THỰC HÀNH 03 – Từ đồng xuất hiện (Co-occurrence)")

    # ── 1. Load corpus ────────────────────────────────────────────────────
    print_header("Bước 1: Nạp và tiền xử lý corpus (loại bỏ stopwords)")
    t0 = time.time()
    # Chuyển thành True để lọc bỏ từ dừng (là, và, của, các...)
    sentences = load_corpus_sentences(remove_stopwords=True)
    print(f"  Thời gian nạp corpus: {time.time() - t0:.1f}s")

    if not sentences:
        print("Lỗi: Không có dữ liệu. Kiểm tra lại thư mục dataset/")
        return

    # ── 2. Phương pháp 1: Ma trận đồng xuất hiện ─────────────────────────
    print_header("Phương pháp 1: Ma trận đồng xuất hiện (C = A × A^T)")
    co_model = CoOccurrenceModel()
    t1 = time.time()
    co_model.fit(sentences)
    print(f"  Thời gian xây dựng ma trận: {time.time() - t1:.1f}s")

    # ── 3. Phương pháp 2: Word2Vec CBOW ───────────────────────────────────
    print_header("Phương pháp 2: Word Embedding – Word2Vec CBOW (window=3)")
    w2v_model = WordEmbeddingModel(window=3)
    t2 = time.time()
    w2v_model.fit(sentences)
    print(f"  Thời gian huấn luyện Word2Vec: {time.time() - t2:.1f}s")

    # Tuỳ chọn: lưu Word2Vec model để tái sử dụng
    model_path = os.path.join(DIR_ROOT, "word2vec_cbow.model")
    w2v_model.save(model_path)

    # ── 4. Kết quả thử nghiệm ─────────────────────────────────────────────
    print_header("Kết quả thử nghiệm")

    all_results = {}

    for query_label, query_variants in REPORT_QUERIES.items():
        print(f"\n{'─' * 55}")
        print(f"  Từ truy vấn: '{query_label}'")
        print(f"{'─' * 55}")

        # Method 1
        found_word_m1, res_m1 = find_best_result(co_model,  query_variants, "M1")
        print_result("Ma trận C", found_word_m1, res_m1)

        # Method 2
        found_word_m2, res_m2 = find_best_result(w2v_model, query_variants, "M2")
        print_result("Word2Vec ", found_word_m2, res_m2)

        all_results[query_label] = {
            "method1_cooccurrence": {
                "searched_as": found_word_m1,
                "results": [(w, round(s, 4)) for w, s in res_m1],
            },
            "method2_word2vec": {
                "searched_as": found_word_m2,
                "results": [(w, round(s, 4)) for w, s in res_m2],
            },
        }

    # ── 5. So sánh 2 phương pháp ──────────────────────────────────────────
    print_header("So sánh 2 phương pháp")
    print("""
  ┌─────────────────┬─────────────────────────┬──────────────────────────────┐
  │ Tiêu chí        │ Phương pháp 1 (Ma trận) │ Phương pháp 2 (Word2Vec)     │
  ├─────────────────┼─────────────────────────┼──────────────────────────────┤
  │ Loại mối quan hệ│ Đồng xuất hiện thực tế  │ Tương đồng ngữ nghĩa         │
  │ Ý nghĩa score   │ Số câu cùng xuất hiện   │ Cosine similarity embedding  │
  │ Tốc độ build    │ Nhanh (phép nhân ma trận│ Chậm hơn (neural training)   │
  │ Bộ nhớ           │ Lớn O(V²)              │ Nhỏ O(V×d)                   │
  │ Yêu cầu dữ liệu │ Corpus nhỏ cũng được    │ Cần nhiều dữ liệu hơn        │
  │ Ứng dụng        │ Thống kê từ cùng ngữ cảnh│ Hiểu ngữ nghĩa từ           │
  └─────────────────┴─────────────────────────┴──────────────────────────────┘
    """)

    # ── 6. Lưu kết quả ────────────────────────────────────────────────────
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    export_markdown(all_results, OUTPUT_MD)
    
    print(f"\nKết quả đã lưu tại (JSON): {OUTPUT_JSON}")
    print(f"Kết quả đã lưu tại (Markdown): {OUTPUT_MD}")
    print(f"Kết quả đã lưu tại: {model_path}")


if __name__ == "__main__":
    main()
