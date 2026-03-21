"""
Thực hành 03 – Phương pháp 2: Word Embedding (Word2Vec CBOW)
============================================================
Pipeline:
  1. Chuẩn bị dữ liệu huấn luyện: corpus mức câu
  2. Train Word2Vec với sg=0 (CBOW), window=3
  3. Với mỗi từ: dùng most_similar() để lấy top-10 từ tương đồng ngữ nghĩa
"""

from gensim.models import Word2Vec


class WordEmbeddingModel:
    """
    Wrapper cho Word2Vec CBOW (sg=0).

    Tham số theo đề bài:
        - CBOW: sg=0
        - window=3 (3 từ bên trái + 3 từ bên phải)
        - vector_size=100
        - min_count=1 (giữ nguyên từ ít gặp trong corpus nhỏ)
    """

    def __init__(self,
                 vector_size: int = 15,
                 window: int = 3,
                 min_count: int = 1,
                 workers: int = 4,
                 epochs: int = 100):
        self.vector_size = vector_size
        self.window      = window
        self.min_count   = min_count
        self.workers     = workers
        self.epochs      = epochs
        self.model: Word2Vec | None = None

    def fit(self, sentences: list[list[str]]):
        """
        Huấn luyện Word2Vec CBOW trên corpus (danh sách câu-token).

        Args:
            sentences: list[list[str]] – mỗi phần tử là danh sách token của 1 câu
        """
        print("[Method 2] Đang huấn luyện Word2Vec (CBOW, window=3)...")
        print(f"  Số câu huấn luyện: {len(sentences)}")

        self.model = Word2Vec(
            sentences=sentences,
            vector_size=self.vector_size,
            window=self.window,
            sg=0,                   # CBOW
            min_count=self.min_count,
            workers=self.workers,
            epochs=self.epochs,
            seed=42,                # reproducible
        )

        vocab_size = len(self.model.wv.key_to_index)
        print(f"  Vocabulary Word2Vec: {vocab_size} từ")
        print("[Method 2] Huấn luyện hoàn thành!\n")

    def most_similar(self, word: str, topn: int = 10) -> list[tuple[str, float]]:
        """
        Trả về top-N từ tương đồng ngữ nghĩa cao nhất cho từ `word`.
        Tự động thử cả dạng gạch dưới (ví dụ "phần mềm" -> "phần_mềm").

        Returns:
            list[(word, similarity_score)]  – similarity ∈ [-1, 1]
        """
        if self.model is None:
            raise RuntimeError("Chưa gọi fit(). Hãy train model trước.")

        # Thử tìm trực tiếp
        word_norm = word.lower().strip()
        if word_norm in self.model.wv:
            return self.model.wv.most_similar(word_norm, topn=topn)

        # Thử dạng gạch dưới (VnCoreNLP ghép từ ghép bằng _)
        word_underscore = word_norm.replace(" ", "_")
        if word_underscore in self.model.wv:
            return self.model.wv.most_similar(word_underscore, topn=topn)

        return []

    def save(self, path: str):
        """Lưu model để tái sử dụng."""
        if self.model:
            self.model.save(path)
            print(f"  Model đã lưu tại: {path}")

    @classmethod
    def load(cls, path: str) -> "WordEmbeddingModel":
        """Nạp model đã lưu."""
        obj = cls()
        obj.model = Word2Vec.load(path)
        print(f"  Model đã nạp từ: {path}")
        return obj
