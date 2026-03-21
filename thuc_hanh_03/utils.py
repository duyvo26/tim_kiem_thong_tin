"""
Thực hành 03 - Utilities dùng chung
Đọc corpus, tokenize và tách câu bằng VnCoreNLP
"""

import os
import re
import docx
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
import py_vncorenlp

# ─────────────────────────────────────────────
# Cấu hình đường dẫn
# ─────────────────────────────────────────────
DIR_ROOT = os.path.dirname(os.path.abspath(__file__))

JAVA_HOME       = r"C:\Program Files\Java\jdk1.8.0_202"
VNCORENLP_DIR   = os.path.join(DIR_ROOT, "vncorenlp")
DATASET_DIR     = os.path.join(DIR_ROOT, "dataset")
STOPWORDS_PATH  = os.path.join(DIR_ROOT, "vietnamese-stopwords.txt")

# Set JAVA env trước khi load model
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PATH"] = os.path.join(JAVA_HOME, "bin") + os.pathsep + os.environ.get("PATH", "")

# ─────────────────────────────────────────────
# Load model VnCoreNLP (lazy – chỉ gọi 1 lần)
# ─────────────────────────────────────────────
_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(VNCORENLP_DIR):
            print("Đang tải VnCoreNLP model...")
            py_vncorenlp.download_model(save_dir=VNCORENLP_DIR)
        print("Đang nạp VnCoreNLP model (wseg)...")
        _model = py_vncorenlp.VnCoreNLP(save_dir=VNCORENLP_DIR, annotators=["wseg"])
        print("VnCoreNLP model đã sẵn sàng.")
    return _model


# ─────────────────────────────────────────────
# Đọc file
# ─────────────────────────────────────────────
def read_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def read_pdf(path: str) -> str:
    return extract_text(path)


def read_html(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    texts = []
    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]):
        t = tag.get_text(separator=" ", strip=True)
        if t:
            texts.append(t)
    return "\n".join(texts)


def read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".doc", ".docx"):
        return read_docx(path)
    elif ext == ".pdf":
        return read_pdf(path)
    elif ext in (".html", ".htm"):
        return read_html(path)
    else:
        raise ValueError(f"Không hỗ trợ định dạng file: {ext}")


# ─────────────────────────────────────────────
# Stopwords
# ─────────────────────────────────────────────
def load_stopwords(path: str = STOPWORDS_PATH):
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


# ─────────────────────────────────────────────
# Tokenize MỨC CÂU (quan trọng cho bài 03)
# Trả về: list[list[str]] – mỗi phần tử là 1 câu (danh sách token)
# ─────────────────────────────────────────────
def tokenize_sentences(text: str, stopwords: set, remove_stopwords: bool = False) -> list[list[str]]:
    """
    Dùng VnCoreNLP tách thành TỪNG CÂU, mỗi câu là list[str] các token.
    
    Args:
        text: chuỗi văn bản thô
        stopwords: tập từ dừng
        remove_stopwords: có loại stopword khỏi token không (mặc định False)
    
    Returns:
        list[list[str]] – danh sách các câu, mỗi câu là danh sách token lowercase
    """
    if not text.strip():
        return []
    try:
        model = get_model()
        annotated = model.annotate_text(text)
        sentences_raw = list(annotated.values()) if isinstance(annotated, dict) else annotated

        sentences = []
        for sent in sentences_raw:
            tokens = []
            for w in sent:
                word = str(w.get("wordForm", "")).lower().strip()
                if not word:
                    continue
                # Chỉ giữ token có chữ cái / số / gạch dưới (loại bỏ dấu câu)
                if not re.match(r"^[\w\u00C0-\u1EF9]+$", word):
                    continue
                if remove_stopwords and word in stopwords:
                    continue
                tokens.append(word)
            if tokens:
                sentences.append(tokens)
        return sentences
    except Exception as e:
        print(f"  [WARN] Lỗi tokenize: {e}")
        return []


# ─────────────────────────────────────────────
# Load toàn bộ corpus thành list câu
# ─────────────────────────────────────────────
def load_corpus_sentences(dataset_dir: str = DATASET_DIR,
                          stopwords_path: str = STOPWORDS_PATH,
                          remove_stopwords: bool = False) -> list[list[str]]:
    """
    Đọc tất cả file trong dataset_dir, tokenize mức câu.
    
    Returns:
        list[list[str]] – toàn bộ corpus dưới dạng danh sách câu-token
    """
    stopwords = load_stopwords(stopwords_path)
    all_sentences = []

    files = sorted(f for f in os.listdir(dataset_dir)
                   if os.path.isfile(os.path.join(dataset_dir, f))
                   and not f.startswith("."))

    for fname in files:
        fpath = os.path.join(dataset_dir, fname)
        try:
            text = read_file(fpath)
            sents = tokenize_sentences(text, stopwords, remove_stopwords)
            all_sentences.extend(sents)
            print(f"  ✓ {fname}: {len(sents)} câu")
        except Exception as e:
            print(f"  ✗ {fname}: {e}")

    print(f"\nTổng số câu: {len(all_sentences)}")
    return all_sentences
