"""
Thực hành 03 – Phương pháp 1: Ma trận đồng xuất hiện
=====================================================
Pipeline:
  1. Xây dựng vocabulary từ corpus
  2. Xây dựng ma trận A (từ × câu) – nhị phân
  3. Tính C = A × A^T (ma trận đồng xuất hiện)
  4. Với mỗi từ: trả về top-10 từ đồng xuất hiện cao nhất
"""

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix


def build_vocab(sentences: list[list[str]]) -> tuple[list[str], dict[str, int]]:
    """
    Tạo vocabulary từ toàn bộ corpus.

    Returns:
        vocab: list các từ (sorted)
        word2idx: dict từ -> chỉ số hàng
    """
    words = set()
    for sent in sentences:
        words.update(sent)
    vocab = sorted(words)
    word2idx = {w: i for i, w in enumerate(vocab)}
    return vocab, word2idx


def build_matrix_A(sentences: list[list[str]], word2idx: dict[str, int]) -> csr_matrix:
    """
    Xây dựng ma trận A (từ × câu) – nhị phân (0/1).
    
    Hàng: từ (vocab)
    Cột: câu (mức document trong bài này)
    Giá trị: 1 nếu từ xuất hiện trong câu, 0 nếu không.
    
    Dùng sparse matrix để tiết kiệm bộ nhớ với corpus lớn.
    """
    V = len(word2idx)   # số từ
    S = len(sentences)  # số câu

    A = lil_matrix((V, S), dtype=np.float32)

    for j, sent in enumerate(sentences):
        for word in sent:
            if word in word2idx:
                A[word2idx[word], j] = 1.0  # nhị phân – chỉ đánh dấu xuất hiện

    return A.tocsr()


def build_cooccurrence_matrix(A: csr_matrix) -> np.ndarray:
    """
    Tính ma trận đồng xuất hiện C = A × A^T.
    
    C[i][j] = số câu mà từ i và từ j cùng xuất hiện.
    Đường chéo C[i][i] = số câu từ i xuất hiện (bỏ qua khi truy vấn).
    """
    C_sparse = A @ A.T          # (V×S) × (S×V) = (V×V)
    return np.asarray(C_sparse.todense())


def get_top_cooccurrence(word: str,
                         C: np.ndarray,
                         vocab: list[str],
                         word2idx: dict[str, int],
                         topn: int = 10) -> list[tuple[str, float]]:
    """
    Với một từ cho trước, trả về top-N từ đồng xuất hiện cao nhất.

    Args:
        word: từ truy vấn (đã lowercase / underscore)
        C: ma trận đồng xuất hiện (V×V)
        vocab: danh sách từ
        word2idx: dict từ -> idx
        topn: số từ trả về (mặc định 10)

    Returns:
        list[(word, score)] sắp xếp giảm dần theo score
    """
    if word not in word2idx:
        return []

    idx = word2idx[word]
    row = C[idx].copy()
    row[idx] = 0  # bỏ chính nó

    # Lấy top-N chỉ số (argsort giảm dần)
    top_indices = np.argsort(-row)[:topn]

    results = []
    for i in top_indices:
        score = float(row[i])
        if score > 0:
            results.append((vocab[i], score))

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Giao diện công khai – sử dụng trong main.py
# ─────────────────────────────────────────────────────────────────────────────

class CoOccurrenceModel:
    """
    Wrapper tiện dụng cho pipeline đồng xuất hiện truyền thống.
    """

    def __init__(self):
        self.vocab: list[str] = []
        self.word2idx: dict[str, int] = {}
        self.C: np.ndarray | None = None

    def fit(self, sentences: list[list[str]]):
        """
        Huấn luyện mô hình từ corpus (danh sách câu-token).
        """
        print("[Method 1] Đang xây dựng vocabulary...")
        self.vocab, self.word2idx = build_vocab(sentences)
        print(f"  Vocabulary: {len(self.vocab)} từ")

        print("[Method 1] Đang xây dựng ma trận A (từ × câu)...")
        A = build_matrix_A(sentences, self.word2idx)
        print(f"  Ma trận A: {A.shape[0]} × {A.shape[1]}, {A.nnz} phần tử khác 0")

        print("[Method 1] Đang tính C = A × A^T ...")
        self.C = build_cooccurrence_matrix(A)
        print(f"  Ma trận C: {self.C.shape}")
        print("[Method 1] Hoàn thành!\n")

    def most_similar(self, word: str, topn: int = 10) -> list[tuple[str, float]]:
        """
        Trả về top-N từ đồng xuất hiện cao nhất cho từ `word`.
        Tự động thử cả dạng gạch dưới (ví dụ "phần mềm" -> "phần_mềm").
        """
        if self.C is None:
            raise RuntimeError("Chưa gọi fit(). Hãy train model trước.")

        # Thử tìm trực tiếp
        word_norm = word.lower().strip()
        if word_norm in self.word2idx:
            return get_top_cooccurrence(word_norm, self.C, self.vocab, self.word2idx, topn)

        # Thử dạng gạch dưới (VnCoreNLP ghép từ ghép bằng _)
        word_underscore = word_norm.replace(" ", "_")
        if word_underscore in self.word2idx:
            return get_top_cooccurrence(word_underscore, self.C, self.vocab, self.word2idx, topn)

        return []
