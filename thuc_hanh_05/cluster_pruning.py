import os
import random
import numpy as np
import pickle
from gensim import corpora, models
import utils

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
        # Lấy danh sách tất cả các file trong thư mục
        files = [f for f in os.listdir(self.dataset_dir) if os.path.isfile(os.path.join(self.dataset_dir, f))]
        
        for fname in files:
            try:
                # Gọi hàm đọc file đa định dạng từ utils.py
                text = utils.read_file(os.path.join(self.dataset_dir, fname))
                if text: documents[fname] = text
            except Exception as e:
                print(f"  [Lỗi] {fname}: {e}")
        return documents

class TextProcessor:
    """Lớp thực hiện các bước tiền xử lý ngôn ngữ văn bản."""
    def __init__(self, stopwords_path):
        # Tải danh sách từ dừng (stopwords) từ file
        self.stopwords = utils.load_stopwords(stopwords_path)

    def process(self, text):
        """
        Chức năng: Làm sạch văn bản, tách từ tiếng Việt (Word Segmentation) và loại bỏ từ dừng.
        Input: text (str) - Chuỗi văn bản thô.
        Output: Một danh sách các tokens (list of strings).
        """
        # Loại bỏ các ký tự đặc biệt, chuyển về chữ thường
        cleaned = utils.clean_text(text)
        # Sử dụng VnCoreNLP để tách từ và lọc stopwords
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
        # Lưu lại tên các tài liệu theo thứ tự
        self.doc_names = list(tokenized_docs.keys())
        texts = [tokenized_docs[name] for name in self.doc_names]
        
        # 1. Tạo Dictionary (Bản đồ từ vựng <-> ID)
        self.dictionary = corpora.Dictionary(texts)
        # 2. Chuyển văn bản thành dạng Bag-of-Words (Tuples ID-Tần suất)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        # 3. Huấn luyện mô hình TF-IDF dựa trên corpus vừa tạo
        self.tfidf_model = models.TfidfModel(corpus)
        # 4. Chuyển đổi toàn bộ tài liệu sang dạng Vector TF-IDF
        self.doc_vectors = [self.tfidf_model[bow] for bow in corpus]

    def get_tfidf_vector(self, tokens):
        """
        Chức năng: Chuyển đổi một danh sách các từ (tokens) thành vectơ trọng số TF-IDF.
        Input: tokens (list of strings) - Danh sách các từ truy vấn.
        Output: Vectơ thưa (Sparse Vector) dưới dạng list of tuples (token_id, weight).
        """
        # Chuyển tokens sang BoW rồi áp dụng mô hình TF-IDF
        return self.tfidf_model[self.dictionary.doc2bow(tokens)]

    def cosine_similarity(self, vec1, vec2):
        """
        Chức năng: Tính độ tương tự Cosine giữa hai vectơ không gian.
        Input: vec1, vec2 (list of tuples) - Hai vectơ TF-IDF cần so khớp.
        Output: Điểm số tương tự (float) nằm trong đoạn [0, 1].
        """
        if not vec1 or not vec2: return 0.0
        # Chuyển vector sang dạng dictionary để truy xuất theo ID nhanh hơn
        v1, v2 = dict(vec1), dict(vec2)
        # Tính tích vô hướng (Dot Product) của các từ chung
        dot = sum(v1[idx] * v2[idx] for idx in v1 if idx in v2)
        # Tính độ dài (Norm) của từng vector
        norm1 = np.sqrt(sum(val**2 for val in v1.values()))
        norm2 = np.sqrt(sum(val**2 for val in v2.values()))
        # Kết quả = Tích vô hướng / (Tích độ dài)
        return dot / (norm1 * norm2) if (norm1 * norm2) > 0 else 0.0

class ClusterPruningIndexer:
    """Lớp thực hiện giải thuật phân cụm để tối ưu hóa tìm kiếm (Cluster Pruning)."""
    def __init__(self, vector_model):
        self.vm = vector_model
        self.leaders = []  # Danh sách ID các leaders
        self.clusters = {} # leader_id -> danh sách followers

    def build_index(self):
        """
        Chức năng: Chọn ngẫu nhiên sqrt(N) leaders và gán mỗi tài liệu vào 2 cụm gần nhất.
        Input: Không có (Sử dụng dữ liệu vectơ từ vector_model).
        Output: Không có (Cập nhật danh sách leaders và các nhóm clusters).
        """
        n = len(self.vm.doc_names)
        if n == 0: return
        # Tính số lượng cụm k = căn bậc 2 của N
        k = max(1, int(np.sqrt(n)))
        # Bước 1: Chọn ngẫu nhiên k leader từ tập tài liệu
        self.leaders = random.sample(range(n), k)
        self.clusters = {idx: [] for idx in self.leaders}
        
        # Bước 2: Duyệt từng tài liệu (được coi là follower)
        for doc_idx in range(n):
            doc_vec = self.vm.doc_vectors[doc_idx]
            # Tính tương quan với tất cả leaders đã chọn
            sims = sorted([(l_idx, self.vm.cosine_similarity(doc_vec, self.vm.doc_vectors[l_idx])) 
                          for l_idx in self.leaders], key=lambda x: x[1], reverse=True)
            # Gán tài liệu này vào 2 cụm có leader gần nó nhất (Top 2)
            for l_idx, _ in sims[:2]:
                self.clusters[l_idx].append(doc_idx)

class SearchHandler:
    """Lớp điều phối quy trình tìm kiếm nhanh."""
    def __init__(self, processor, vmodel, indexer):
        self.pre = processor
        self.vm = vmodel
        self.idx = indexer

    def search(self, query, top_n=5):
        """
        Chức năng: Thực hiện quy trình tìm kiếm Cluster Pruning (Tìm 2 leader gần nhất -> Tìm trong cụm của họ).
        Input: query (str) - Chuỗi truy vấn; top_n (int) - Số lượng kết quả muốn lấy.
        Output: Danh sách các tuples (tên_file, điểm_cosine) đã được sắp xếp giảm dần.
        """
        # 1. Tiền xử lý truy vấn
        tokens = self.pre.process(query)
        if not tokens: return []
        # 2. Vector hóa truy vấn sang không gian TF-IDF
        q_vec = self.vm.get_tfidf_vector(tokens)
        
        # 3. Tìm 2 leader gần nhất với vector truy vấn của người dùng
        leader_sims = sorted([(l_idx, self.vm.cosine_similarity(q_vec, self.vm.doc_vectors[l_idx])) 
                             for l_idx in self.idx.leaders], key=lambda x: x[1], reverse=True)
        
        # 4. Gom tập hợp ứng viên từ followers của 2 leader tốt nhất này
        candidates = set()
        for l_idx, _ in leader_sims[:2]:
            candidates.update(self.idx.clusters[l_idx])
        
        print(f"[*] Tìm kiếm trong {len(candidates)} tài liệu ứng viên (Pruning).")
        # 5. Xếp hạng: Chỉ tính Cosine với tập ứng viên thu gọn
        results = [(self.vm.doc_names[idx], self.vm.cosine_similarity(q_vec, self.vm.doc_vectors[idx])) 
                   for idx in candidates]
        # Sắp xếp kết quả giảm dần theo điểm số
        return sorted([r for r in results if r[1] > 0], key=lambda x: x[1], reverse=True)[:top_n]

def main():
    """Hàm khởi chạy chính của chương trình, điều phối giữa việc nạp cache và xử lý mới."""
    DIR_ROOT = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIR = utils.DATASET_DIR
    STOPWORDS_PATH = utils.STOPWORDS_PATH
    REPORT_PATH = os.path.join(DIR_ROOT, "report_05.md")
    INDEX_PATH = os.path.join(DIR_ROOT, "index.pkl")

    # Khởi tạo các thành phần cốt lõi
    processor = TextProcessor(STOPWORDS_PATH)
    vmodel = VectorModel()
    indexer = ClusterPruningIndexer(vmodel)
    search_handler = SearchHandler(processor, vmodel, indexer)

    # CHIẾN LƯỢC CACHE: Kiểm tra xem đã có dữ liệu chỉ mục lưu từ trước chưa
    if os.path.exists(INDEX_PATH):
        print(f"\n[*] Đang nạp chỉ mục từ file tĩnh: {INDEX_PATH}")
        with open(INDEX_PATH, "rb") as f:
            data = pickle.load(f)
            # Khôi phục trạng thái từ file pkl
            vmodel.dictionary = data['dictionary']
            vmodel.tfidf_model = data['tfidf_model']
            vmodel.doc_names = data['doc_names']
            vmodel.doc_vectors = data['doc_vectors']
            indexer.leaders = data['leaders']
            indexer.clusters = data['clusters']
        print("[OK] Đã nạp thành công, hệ thống sẵn sàng tìm kiếm ngay.")
    else:
        # Nếu chưa có index, thực thực hiện quy trình phân tích và gán cụm từ đầu
        print("\n[*] Lần đầu khởi tạo: Đang chạy quy trình phân tích văn bản...")
        loader = DocumentDataLoader(DATASET_DIR)
        raw_docs = loader.load_all()
        # Chuyển đổi toàn bộ text sang tokens
        tokenized_docs = {name: processor.process(content) for name, content in raw_docs.items()}
        # Xây dựng TF-IDF và chọn leaders
        vmodel.fit(tokenized_docs)
        indexer.build_index()
        # Lưu lại kết quả xuống file để lần sau dùng luôn
        with open(INDEX_PATH, "wb") as f:
            pickle.dump({
                'dictionary': vmodel.dictionary, 'tfidf_model': vmodel.tfidf_model,
                'doc_names': vmodel.doc_names, 'doc_vectors': vmodel.doc_vectors,
                'leaders': indexer.leaders, 'clusters': indexer.clusters
            }, f)

    print("\n" + "="*30)
    print("HỆ THỐNG TÌM KIẾM CLUSTER PRUNING (CACHE ENABLED)")
    print("="*30)
    
    # Danh sách các truy vấn demo
    queries = ["windows xp", "bảng lương công an"]
    search_history = []
    
    for q in queries:
        print(f"\n[*] Truy vấn: '{q}'")
        res = search_handler.search(q)
        search_history.append((q, res))
        for i, (name, score) in enumerate(res, 1):
            print(f"  {i}. {name} (Score: {score:.4f})")

    # Tự động xuất báo cáo kết quả ra file Markdown
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("# BÁO CÁO TÌM KIẾM (CÓ SỬ DỤNG CACHE)\n\n")
            f.write(f"- Trạng thái index: {'Loaded from Cache' if os.path.exists(INDEX_PATH) else 'Newly Created'}\n\n")
            for q, res in search_history:
                f.write(f"### `Truy vấn: {q}`\n")
                if res:
                    f.write("| STT | Tài liệu | Score |\n|:--|:---|:---|\n")
                    for i, (name, score) in enumerate(res, 1):
                        f.write(f"| {i} | {name} | {score:.4f} |\n")
                f.write("\n")
        print(f"\n[OK] Báo cáo đã cập nhật tại: {REPORT_PATH}")
    except Exception as e: print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
