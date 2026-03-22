import os
import random
import numpy as np
import pickle
from gensim import corpora, models
import utils

# ─────────────────────────────────────────────
# Tham số toàn cục cho thuật toán Cluster Pruning
# ─────────────────────────────────────────────
TOP_K = 2  # Số cụm gần nhất: mỗi follower thuộc TOP_K cụm; tìm kiếm trong TOP_K leaders gần nhất

class DocumentDataLoader:
    """Lớp quản lý việc nạp dữ liệu từ các tập tin trong hệ thống."""
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir

    def load_all(self):
        """
        Chức năng: Duyệt thư mục dataset và đọc nội dung toàn bộ các file (.doc, .docx, .pdf, .html).
        Input: Không có (Sử dụng đường dẫn thư mục đã khởi tạo trong __init__).
        Output: Một Dictionary {tên_file: nội_dung_văn_bản}.
        """
        print(f"[*] Đang nạp dữ liệu từ: {self.dataset_dir}")
        documents = {}
        files = [f for f in os.listdir(self.dataset_dir) if os.path.isfile(os.path.join(self.dataset_dir, f))]
        for fname in files:
            try:
                text = utils.read_file(os.path.join(self.dataset_dir, fname))
                if text: documents[fname] = text
            except Exception as e:
                print(f"  [Lỗi] {fname}: {e}")
        return documents

class TextProcessor:
    """Lớp thực hiện các bước tiền xử lý ngôn ngữ văn bản."""
    def __init__(self, stopwords_path):
        self.stopwords = utils.load_stopwords(stopwords_path)

    def process(self, text):
        """
        Chức năng: Làm sạch văn bản, tách từ tiếng Việt (Word Segmentation) và loại bỏ từ dừng.
        Input: text (str) - Chuỗi văn bản thô.
        Output: Một danh sách các tokens (list of strings).
        """
        cleaned = utils.clean_text(text)
        return utils.get_tokens(cleaned, self.stopwords)

class VectorModel:
    """Lớp quản lý mô hình không gian vectơ TF-IDF."""
    def __init__(self):
        self.dictionary = None
        self.tfidf_model = None
        self.doc_names = []
        self.doc_vectors = []

    def fit(self, tokenized_docs):
        """
        Chức năng: Xây dựng bộ từ điển và huấn luyện mô hình TF-IDF từ tập tài liệu đã tách từ.
        Input: tokenized_docs (dict) - Dictionary chứa các tài liệu đã được tách từ.
        Output: Không có (Cập nhật các thuộc tính nội bộ dictionary và tfidf_model).
        """
        self.doc_names = list(tokenized_docs.keys())
        texts = [tokenized_docs[name] for name in self.doc_names]
        # 1. Tạo Dictionary (Bản đồ từ vựng <-> ID)
        self.dictionary = corpora.Dictionary(texts)
        # 2. Chuyển văn bản thành dạng Bag-of-Words
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        # 3. Huấn luyện mô hình TF-IDF
        self.tfidf_model = models.TfidfModel(corpus)
        # 4. Chuyển đổi toàn bộ tài liệu sang Vector TF-IDF
        self.doc_vectors = [self.tfidf_model[bow] for bow in corpus]

    def get_tfidf_vector(self, tokens):
        """
        Chức năng: Chuyển đổi một danh sách các từ (tokens) thành vectơ trọng số TF-IDF.
        Input: tokens (list of strings) - Danh sách các từ truy vấn.
        Output: Vectơ thưa (Sparse Vector) dưới dạng list of tuples (token_id, weight).
        """
        return self.tfidf_model[self.dictionary.doc2bow(tokens)]

    def cosine_similarity(self, vec1, vec2):
        """
        Chức năng: Tính độ tương tự Cosine giữa hai vectơ không gian.
        Input: vec1, vec2 (list of tuples) - Hai vectơ TF-IDF cần so khớp.
        Output: Điểm số tương tự (float) nằm trong đoạn [0, 1].
        """
        if not vec1 or not vec2: return 0.0
        v1, v2 = dict(vec1), dict(vec2)
        dot = sum(v1[idx] * v2[idx] for idx in v1 if idx in v2)
        norm1 = np.sqrt(sum(val**2 for val in v1.values()))
        norm2 = np.sqrt(sum(val**2 for val in v2.values()))
        return dot / (norm1 * norm2) if (norm1 * norm2) > 0 else 0.0

class ClusterPruningIndexer:
    """Lớp thực hiện giải thuật phân cụm để tối ưu hóa tìm kiếm (Cluster Pruning)."""
    def __init__(self, vector_model):
        self.vm = vector_model
        self.leaders = []  # Danh sách ID các leaders
        self.clusters = {} # leader_id -> danh sách followers

    def build_index(self):
        """
        Chức năng: Chọn ngẫu nhiên sqrt(N) leaders và gán mỗi tài liệu vào TOP_K cụm gần nhất.
        Input: Không có (Sử dụng dữ liệu vectơ từ vector_model).
        Output: Không có (Cập nhật danh sách leaders và các nhóm clusters).
        """
        n = len(self.vm.doc_names)
        if n == 0: return
        # Tính số lượng cụm k = sqrt(N)
        k = max(1, int(np.sqrt(n)))
        # Bước 1: Chọn ngẫu nhiên k leader từ tập tài liệu
        self.leaders = random.sample(range(n), k)
        self.clusters = {idx: [] for idx in self.leaders}
        print(f"  [*] Số cụm (sqrt(N)={k}), leaders: {[self.vm.doc_names[i] for i in self.leaders]}")

        # Bước 2: Duyệt từng tài liệu (được coi là follower)
        for doc_idx in range(n):
            doc_vec = self.vm.doc_vectors[doc_idx]
            # Tính độ tương tự cosine với tất cả leaders
            sims = sorted(
                [(l_idx, self.vm.cosine_similarity(doc_vec, self.vm.doc_vectors[l_idx]))
                 for l_idx in self.leaders],
                key=lambda x: x[1], reverse=True
            )
            # Gán tài liệu vào TOP_K cụm có leader gần nhất (yêu cầu bài: TOP_K=2)
            for l_idx, _ in sims[:TOP_K]:
                self.clusters[l_idx].append(doc_idx)

class SearchHandler:
    """Lớp điều phối quy trình tìm kiếm nhanh."""
    def __init__(self, processor, vmodel, indexer):
        self.pre = processor
        self.vm = vmodel
        self.idx = indexer

    def search(self, query, top_n=5):
        """
        Chức năng: Thực hiện quy trình tìm kiếm Cluster Pruning.
        Input: query (str) - Chuỗi truy vấn; top_n (int) - Số lượng kết quả muốn lấy.
        Output: Dict gồm 'results', 'top_leaders', 'num_candidates'.
        """
        # 1. Tiền xử lý truy vấn
        tokens = self.pre.process(query)
        if not tokens:
            return {"results": [], "top_leaders": [], "num_candidates": 0}
        # 2. Vector hóa truy vấn sang không gian TF-IDF
        q_vec = self.vm.get_tfidf_vector(tokens)

        # 3. Tìm TOP_K leaders gần nhất với vector truy vấn (yêu cầu bài: TOP_K=2)
        leader_sims = sorted(
            [(l_idx, self.vm.cosine_similarity(q_vec, self.vm.doc_vectors[l_idx]))
             for l_idx in self.idx.leaders],
            key=lambda x: x[1], reverse=True
        )
        top_leaders_idx = leader_sims[:TOP_K]
        top_leaders_info = [(self.vm.doc_names[l], s) for l, s in top_leaders_idx]
        print(f"  [*] {TOP_K} leaders gần nhất: {[(name, f'{s:.4f}') for name, s in top_leaders_info]}")

        # 4. Gom ứng viên từ followers của TOP_K leaders gần nhất
        candidates = set()
        for l_idx, _ in top_leaders_idx:
            candidates.update(self.idx.clusters[l_idx])

        print(f"[*] Tìm kiếm trong {len(candidates)} tài liệu ứng viên (Pruning).")
        # 5. Xếp hạng: Chỉ tính Cosine với tập ứng viên thu gọn
        results = [
            (self.vm.doc_names[idx], self.vm.cosine_similarity(q_vec, self.vm.doc_vectors[idx]))
            for idx in candidates
        ]
        ranked = sorted([r for r in results if r[1] > 0], key=lambda x: x[1], reverse=True)[:top_n]
        return {
            "results":        ranked,
            "top_leaders":    top_leaders_info,
            "num_candidates": len(candidates),
        }

def main():
    """Hàm khởi chạy chính của chương trình."""
    DIR_ROOT = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIR   = utils.DATASET_DIR
    STOPWORDS_PATH = utils.STOPWORDS_PATH
    REPORT_PATH   = os.path.join(DIR_ROOT, "report_05.md")

    # Khởi tạo các thành phần cốt lõi
    processor = TextProcessor(STOPWORDS_PATH)
    vmodel = VectorModel()
    indexer = ClusterPruningIndexer(vmodel)
    search_handler = SearchHandler(processor, vmodel, indexer)

    # Luôn rebuild index (leaders chọn ngẫu nhiên mỗi lần — đặc tính của Cluster Pruning)
    print("\n[*] Đang phân tích văn bản và xây dựng chỉ mục phân cụm...")
    loader = DocumentDataLoader(DATASET_DIR)
    raw_docs = loader.load_all()
    tokenized_docs = {name: processor.process(content) for name, content in raw_docs.items()}
    vmodel.fit(tokenized_docs)
    indexer.build_index()

    print("\n" + "="*50)
    print("HỆ THỐNG TÌM KIẾM NHANH - CLUSTER PRUNING")
    print("="*50)

    queries = ["Ốc gạo Phú Đa", "PGS Văn Như Cương"]
    search_history = []

    for q in queries:
        print(f"\n[*] Truy vấn: '{q}'")
        ret = search_handler.search(q)
        res            = ret["results"]
        top_leaders    = ret["top_leaders"]
        num_candidates = ret["num_candidates"]
        search_history.append((q, res, top_leaders, num_candidates))
        for i, (name, score) in enumerate(res, 1):
            print(f"  {i}. {name} (Score: {score:.4f})")

    # Xuất báo cáo ra file Markdown
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("# BÁO CÁO TÌM KIẾM - CLUSTER PRUNING\n\n")
            f.write(f"- Số cụm mỗi tài liệu thuộc về (TOP\\_K): `{TOP_K}`\n")
            f.write(f"- Số leaders được chọn (sqrt(N)): `{len(indexer.leaders)}`\n\n")
            for q, res, top_leaders, num_candidates in search_history:
                f.write(f"### Truy vấn: `{q}`\n\n")
                f.write(f"- **{TOP_K} leaders gần nhất:** ")
                f.write(", ".join(f"`{name}` (score: {s:.4f})" for name, s in top_leaders) + "\n")
                f.write(f"- **Số tài liệu ứng viên (Pruning):** `{num_candidates}`\n\n")
                if res:
                    f.write("| STT | Tài liệu | Score |\n|:--|:---|:---|\n")
                    for i, (name, score) in enumerate(res, 1):
                        f.write(f"| {i} | {name} | {score:.4f} |\n")
                else:
                    f.write("_Không tìm thấy kết quả._\n")
                f.write("\n")
        print(f"\n[OK] Báo cáo đã cập nhật tại: {REPORT_PATH}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
