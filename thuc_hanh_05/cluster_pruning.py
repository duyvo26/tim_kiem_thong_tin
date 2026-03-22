import os
import random
import numpy as np
import pickle
from gensim import corpora, models
import utils

class DocumentDataLoader:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir

    def load_all(self):
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
    def __init__(self, stopwords_path):
        self.stopwords = utils.load_stopwords(stopwords_path)

    def process(self, text):
        cleaned = utils.clean_text(text)
        return utils.get_tokens(cleaned, self.stopwords)

class VectorModel:
    def __init__(self):
        self.dictionary = None
        self.tfidf_model = None
        self.doc_names = []
        self.doc_vectors = []

    def fit(self, tokenized_docs):
        self.doc_names = list(tokenized_docs.keys())
        texts = [tokenized_docs[name] for name in self.doc_names]
        self.dictionary = corpora.Dictionary(texts)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        self.tfidf_model = models.TfidfModel(corpus)
        self.doc_vectors = [self.tfidf_model[bow] for bow in corpus]

    def get_tfidf_vector(self, tokens):
        return self.tfidf_model[self.dictionary.doc2bow(tokens)]

    def cosine_similarity(self, vec1, vec2):
        if not vec1 or not vec2: return 0.0
        v1, v2 = dict(vec1), dict(vec2)
        dot = sum(v1[idx] * v2[idx] for idx in v1 if idx in v2)
        norm1 = np.sqrt(sum(val**2 for val in v1.values()))
        norm2 = np.sqrt(sum(val**2 for val in v2.values()))
        return dot / (norm1 * norm2) if (norm1 * norm2) > 0 else 0.0

class ClusterPruningIndexer:
    def __init__(self, vector_model):
        self.vm = vector_model
        self.leaders = [] 
        self.clusters = {}

    def build_index(self):
        n = len(self.vm.doc_names)
        if n == 0: return
        k = max(1, int(np.sqrt(n)))
        self.leaders = random.sample(range(n), k)
        self.clusters = {idx: [] for idx in self.leaders}
        
        for doc_idx in range(n):
            doc_vec = self.vm.doc_vectors[doc_idx]
            sims = sorted([(l_idx, self.vm.cosine_similarity(doc_vec, self.vm.doc_vectors[l_idx])) 
                          for l_idx in self.leaders], key=lambda x: x[1], reverse=True)
            for l_idx, _ in sims[:2]:
                self.clusters[l_idx].append(doc_idx)

class SearchHandler:
    def __init__(self, processor, vmodel, indexer):
        self.pre = processor
        self.vm = vmodel
        self.idx = indexer

    def search(self, query, top_n=5):
        tokens = self.pre.process(query)
        if not tokens: return []
        q_vec = self.vm.get_tfidf_vector(tokens)
        
        # Tìm 2 leader gần nhất
        leader_sims = sorted([(l_idx, self.vm.cosine_similarity(q_vec, self.vm.doc_vectors[l_idx])) 
                             for l_idx in self.idx.leaders], key=lambda x: x[1], reverse=True)
        
        candidates = set()
        for l_idx, _ in leader_sims[:2]:
            candidates.update(self.idx.clusters[l_idx])
        
        print(f"[*] Tìm kiếm trong {len(candidates)} tài liệu (Pruning).")
        results = [(self.vm.doc_names[idx], self.vm.cosine_similarity(q_vec, self.vm.doc_vectors[idx])) 
                   for idx in candidates]
        return sorted([r for r in results if r[1] > 0], key=lambda x: x[1], reverse=True)[:top_n]

def main():
    DIR_ROOT = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIR = utils.DATASET_DIR
    STOPWORDS_PATH = utils.STOPWORDS_PATH
    REPORT_PATH = os.path.join(DIR_ROOT, "report_05.md")
    INDEX_PATH = os.path.join(DIR_ROOT, "index.pkl")

    processor = TextProcessor(STOPWORDS_PATH)
    vmodel = VectorModel()
    indexer = ClusterPruningIndexer(vmodel)
    search_handler = SearchHandler(processor, vmodel, indexer)

    # CHIẾN LƯỢC: CHỈ LOAD LẠI KHI KHÔNG CÓ FILE TĨNH (CACHE)
    if os.path.exists(INDEX_PATH):
        print(f"\n[*] Đang nạp chỉ mục từ file tĩnh: {INDEX_PATH}")
        with open(INDEX_PATH, "rb") as f:
            data = pickle.load(f)
            vmodel.dictionary = data['dictionary']
            vmodel.tfidf_model = data['tfidf_model']
            vmodel.doc_names = data['doc_names']
            vmodel.doc_vectors = data['doc_vectors']
            indexer.leaders = data['leaders']
            indexer.clusters = data['clusters']
        print("[OK] Đã nạp thành công, hệ thống sẵn sàng tìm kiếm ngay.")
    else:
        print("\n[*] Lần đầu khởi tạo: Đang chạy quy trình phân tích văn bản...")
        loader = DocumentDataLoader(DATASET_DIR)
        raw_docs = loader.load_all()
        tokenized_docs = {name: processor.process(content) for name, content in raw_docs.items()}
        
        vmodel.fit(tokenized_docs)
        indexer.build_index()
        
        # Lưu file để các lần chạy sau không phải load lại VnCoreNLP
        print(f"[*] Đang lưu chỉ mục vào: {INDEX_PATH}...")
        with open(INDEX_PATH, "wb") as f:
            pickle.dump({
                'dictionary': vmodel.dictionary,
                'tfidf_model': vmodel.tfidf_model,
                'doc_names': vmodel.doc_names,
                'doc_vectors': vmodel.doc_vectors,
                'leaders': indexer.leaders,
                'clusters': indexer.clusters
            }, f)

    # Truy vấn tự động
    print("\n" + "="*30)
    print("HỆ THỐNG TÌM KIẾM CLUSTER PRUNING (CACHE ENABLED)")
    print("="*30)
    
    queries = ["windows xp", "bảng lương công an"]
    search_history = []
    
    for q in queries:
        print(f"\n[*] Truy vấn: '{q}'")
        res = search_handler.search(q)
        search_history.append((q, res))
        for i, (name, score) in enumerate(res, 1):
            print(f"  {i}. {name} (Score: {score:.4f})")

    # Tạo báo cáo nhanh
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("# BÁO CÁO TÌM KIẾM (CÓ SỬ DỤNG CACHE)\n\n")
            f.write(f"- Trạng thái index: {'Loaded from Cache' if os.path.exists(INDEX_PATH) else 'Newly Created'}\n\n")
            for q, res in search_history:
                f.write(f"### `{q}`\n")
                if res:
                    f.write("| STT | Tài liệu | Score |\n|:--|:---|:---|\n")
                    for i, (name, score) in enumerate(res, 1):
                        f.write(f"| {i} | {name} | {score:.4f} |\n")
                f.write("\n")
        print(f"\n[OK] Báo cáo đã cập nhật tại: {REPORT_PATH}")
    except Exception as e: print(f"Lỗi lưu báo cáo: {e}")

if __name__ == "__main__":
    main()
