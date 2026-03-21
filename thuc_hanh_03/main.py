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

from utils import load_corpus_sentences, DIR_ROOT, tokenize_sentences
from cooccurrence import CoOccurrenceModel
from word_embedding import WordEmbeddingModel
# ─────────────────────────────────────────────────────────────────────────────
TOPN = 10

# Từ truy vấn chính gốc chưa qua xử lý
RAW_QUERIES = [
    "window xp",
    "phần mềm",
]

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


def find_best_result(model_obj, query: str, method_name: str) -> tuple[str, list]:
    """
    Tìm trực tiếp từ khóa (token) đầu tiên được quét ra bởi bộ tokenizer.
    Không tìm được -> Dừng luôn (Trả về rỗng). Không cố tình tìm các từ đằng sau (Fallback).
    """
    res = model_obj.most_similar(query, topn=TOPN)
    if res:
        return query, res

    return query, []


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

    for query_label in RAW_QUERIES:
        # Dùng VnCoreNLP để động nhận dạng/ghép chữ
        sents = tokenize_sentences(query_label, stopwords=set(), remove_stopwords=False)
        query_variants = [w for sent in sents for w in sent]
        
        # Dùng từ khóa đại diện đầu tiên. Cắt cái trò tìm không được rồi nhảy sang từ thứ 2.
        core_query = query_variants[0] if query_variants else query_label

        print(f"\n{'─' * 55}")
        print(f"  Từ truy vấn gốc: '{query_label}'")
        print(f"  VnCoreNLP tokenize thành: {query_variants}")
        print(f"{'─' * 55}")

        # Method 1
        found_word_m1, res_m1 = find_best_result(co_model, core_query, "M1")
        print_result("Ma trận C", found_word_m1, res_m1)

        # Method 2
        found_word_m2, res_m2 = find_best_result(w2v_model, core_query, "M2")
        print_result("Word2Vec ", found_word_m2, res_m2)

        all_results[query_label] = {
            "method1_cooccurrence": {
                "searched_as": found_word_m1,
                "results": [(w, round(float(s), 4)) for w, s in res_m1],
            },
            "method2_word2vec": {
                "searched_as": found_word_m2,
                "results": [(w, round(float(s), 4)) for w, s in res_m2],
            },
        }
    # ── 5. Lưu kết quả ────────────────────────────────────────────────────
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    export_markdown(all_results, OUTPUT_MD)
    
    print(f"\nKết quả đã lưu tại (JSON): {OUTPUT_JSON}")
    print(f"Kết quả đã lưu tại (Markdown): {OUTPUT_MD}")
    print(f"Kết quả đã lưu tại: {model_path}")


if __name__ == "__main__":
    main()
