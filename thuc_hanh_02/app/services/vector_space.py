import os
import math
import collections
import py_vncorenlp
import docx
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
import re
from typing import List, Dict, Set, Any
from app.config import settings

class VectorSpaceService:
    def __init__(self, dataset_dir: str, storage_dir: str, stopwords_path: str, vncorenlp_dir: str, java_home: str):
        self.dataset_dir = dataset_dir
        self.storage_dir = storage_dir
        self.stopwords_path = stopwords_path
        self.vncorenlp_dir = vncorenlp_dir
        
        # Setup environment for Java
        os.environ["JAVA_HOME"] = java_home
        os.environ["PATH"] = os.path.join(java_home, "bin") + os.pathsep + os.environ["PATH"]
        
        self.dict_path = os.path.join(storage_dir, "dictionary.txt")
        self.index_path = os.path.join(storage_dir, "invertedIndex.txt")
        self.lengths_path = os.path.join(storage_dir, "docLengths.txt")
        
        self.stopwords = self._load_stopwords()
        self.model = None # Lazy load
        
        self.dictionary: Dict[str, Dict[str, int]] = {}
        self.doc_lengths: Dict[str, float] = {}
        self.load_index()

    def _get_model(self):
        if self.model is None:
            print("Loading VnCoreNLP model (Lazy)...")
            try:
                self.model = py_vncorenlp.VnCoreNLP(save_dir=self.vncorenlp_dir, annotators=["wseg"])
            except Exception as e:
                print(f"FAILED to load VnCoreNLP: {e}")
                raise e
        return self.model

    def _load_stopwords(self) -> Set[str]:
        if not os.path.exists(self.stopwords_path):
            return set()
        with open(self.stopwords_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())

    def load_index(self):
        """Loads index metadata from existing .txt files."""
        self.dictionary = {}
        self.doc_lengths = {}
        try:
            if os.path.exists(self.dict_path):
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 3 and parts[0] != "Term":
                            term, df, offset = parts[0], parts[1], parts[2]
                            self.dictionary[term] = {"df": int(df), "offset": int(offset)}
            
            if os.path.exists(self.lengths_path):
                with open(self.lengths_path, "r", encoding="utf-8") as f:
                    for line in f:
                        v = line.strip().split(":")
                        if len(v) == 2:
                            self.doc_lengths[v[0]] = float(v[1])
            print(f"Index Active: {len(self.dictionary)} terms, {len(self.doc_lengths)} docs.")
        except Exception as e:
            print(f"Error loading index: {e}")

    def tokenize(self, text: str) -> List[str]:
        if not text: return []
        try:
            model = self._get_model()
            annotated = model.annotate_text(text)
            sentences = annotated.values() if isinstance(annotated, dict) else annotated
            tokens = []
            for sentence in sentences:
                for w in sentence:
                    word = str(w.get("wordForm", "")).lower()
                    if not word: continue
                    # Clean tokens: words and underscores only (Vietnamese supported)
                    if word not in self.stopwords and re.match(r"^[a-zA-Z0-9_\u00C0-\u1EF9]+$", word):
                        tokens.append(word)
            return tokens
        except Exception as e:
            print(f"Tokenization error: {e}")
            return []

    def build_index(self):
        """Builds a Positional Index and calculates Cosine Normalization lengths."""
        print("Starting indexing process...")
        raw_index: Dict[str, Dict[str, List[int]]] = {}
        doc_count = 0
        
        if not os.path.exists(self.dataset_dir):
            print(f"Dataset directory not found: {self.dataset_dir}")
            return

        files = [f for f in os.listdir(self.dataset_dir) if os.path.isfile(os.path.join(self.dataset_dir, f))]
        for name in files:
            p = os.path.join(self.dataset_dir, name)
            content = self._read_file(p)
            tokens = self.tokenize(content)
            if not tokens: continue
            
            doc_count += 1
            for pos, t in enumerate(tokens):
                if t not in raw_index: raw_index[t] = {}
                if name not in raw_index[t]: raw_index[t][name] = []
                raw_index[t][name].append(pos)
            print(f"Indexed: {name}")

        if doc_count == 0: 
            print("No documents found to index.")
            return

        os.makedirs(self.storage_dir, exist_ok=True)
        doc_vector_sums: Dict[str, float] = {}
        
        with open(self.index_path, "w", encoding="utf-8", newline="\n") as f_inv, \
             open(self.dict_path, "w", encoding="utf-8", newline="\n") as f_dict:
            
            f_dict.write("Term\tDF\tOffset\n")
            offset = 0
            for term in sorted(raw_index.keys()):
                postings = raw_index[term]
                df = len(postings)
                idf = math.log10(doc_count / df) if df > 0 else 0.0
                
                # Format: doc_id:tf:pos1,pos2...
                p_strs = []
                for d_id, positions in postings.items():
                    tf = len(positions)
                    p_strs.append(f"{d_id}:{tf}:{','.join(map(str, positions))}")
                    w_d = (1.0 + math.log10(tf)) * idf
                    doc_vector_sums[d_id] = doc_vector_sums.get(d_id, 0.0) + (w_d * w_d)
                
                line = f"{idf:.5f}\t" + " ".join(p_strs) + "\n"
                f_inv.write(line)
                f_dict.write(f"{term}\t{df}\t{offset}\n")
                offset += len(line.encode("utf-8"))

        # Save normalization lengths
        with open(self.lengths_path, "w", encoding="utf-8") as f:
            for d_id in sorted(doc_vector_sums.keys()):
                length = math.sqrt(doc_vector_sums[d_id])
                f.write(f"{d_id}:{length:.5f}\n")
        
        self.load_index()
        print("Indexing completed successfully.")

    def _read_file(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".docx":
                doc = docx.Document(path)
                return "\n".join([str(p.text) for p in doc.paragraphs])
            elif ext == ".pdf":
                return str(extract_text(path))
            elif ext in [".html", ".htm"]:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return BeautifulSoup(f, "html.parser").get_text()
            return ""
        except Exception: 
            return ""

    def search(self, query: str, query_type: str = "keyword") -> List[Dict[str, Any]]:
        """
        1. Find candidate documents matching query criteria.
        2. Rank ONLY candidates using Cosine Similarity.
        """
        try:
            tokens = self.tokenize(query)
            if not tokens: return []
            
            # Step 1: Get candidate document IDs (Normal or Phrase)
            candidates = self._get_candidates(tokens, query_type)
            if not candidates: return []

            # Step 2: Rank ONLY candidates
            q_weights: Dict[str, float] = {}
            doc_scores: Dict[str, float] = {}
            q_tf = collections.Counter(tokens)
            q_norm_sq = 0.0
            
            for t, tf in q_tf.items():
                if t in self.dictionary:
                    idf = self._get_idf_file(t)
                    w_q = (1.0 + math.log10(tf)) * idf
                    q_weights[t] = w_q
                    q_norm_sq += (w_q * w_q)
            
            q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0

            if os.path.exists(self.index_path):
                with open(self.index_path, "r", encoding="utf-8") as f:
                    for t, w_q in q_weights.items():
                        meta = self.dictionary.get(t)
                        if not meta: continue
                        
                        f.seek(meta["offset"])
                        line = f.readline().strip()
                        parts = line.split("\t")
                        if len(parts) < 2: continue
                        
                        idf_d = float(parts[0])
                        p_raw = parts[1].split(" ")
                        for p in p_raw:
                            bits = p.split(":")
                            if len(bits) < 2: continue
                            d_id = bits[0]
                            # IMPORTANT: Only calculate for candidates
                            if d_id in candidates:
                                tf_d = int(bits[1])
                                w_d = (1.0 + math.log10(tf_d)) * idf_d
                                doc_scores[d_id] = doc_scores.get(d_id, 0.0) + (w_q * w_d)

            results = []
            for d_id in candidates:
                d_norm = self.doc_lengths.get(d_id, 1.0)
                score = doc_scores.get(d_id, 0.0) / (q_norm * d_norm) if (q_norm * d_norm) > 0 else 0.0
                results.append({"doc_id": d_id, "score": score})
            
            return sorted(results, key=lambda x: x["score"], reverse=True)
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _get_idf_file(self, t: str) -> float:
        meta = self.dictionary.get(t)
        if not meta: return 0.0
        with open(self.index_path, "r", encoding="utf-8") as f:
            f.seek(meta["offset"])
            line = f.readline()
            parts = line.split("\t")
            return float(parts[0]) if parts else 0.0

    def _get_candidates(self, tokens: List[str], q_type: str) -> Set[str]:
        """Returns set of doc IDs matching search type logic."""
        term_postings = []
        for t in tokens:
            if t not in self.dictionary: return set()
            term_postings.append(self._load_postings_file(t))
        
        doc_sets = [set(p.keys()) for p in term_postings]
        if not doc_sets: return set()
        
        common = doc_sets[0]
        for s in doc_sets[1:]:
            common = common.intersection(s)
        
        if q_type == "phrase" and common:
            # Case 2: Clause/Phrase search (Chapter 2)
            final = set()
            for d in common:
                if self._has_phrase(d, term_postings): final.add(d)
            return final
        
        # Case 1: Normal retrieval (Chapter 1)
        return common

    def _load_postings_file(self, t: str) -> Dict[str, List[int]]:
        meta = self.dictionary.get(t)
        if not meta: return {}
        with open(self.index_path, "r", encoding="utf-8") as f:
            f.seek(meta["offset"])
            line = f.readline().strip()
            parts = line.split("\t")
            if len(parts) < 2: return {}
            raw = parts[1].split(" ")
            res = {}
            for p in raw:
                bits = p.split(":")
                if len(bits) >= 2:
                    doc_id = bits[0]
                    # Attempt to load positions if available
                    pos = [int(x) for x in bits[2].split(",")] if len(bits) >= 3 else []
                    res[doc_id] = pos
            return res

    def _has_phrase(self, d: str, term_postings: List[Dict[str, List[int]]]) -> bool:
        """Checks if words appear consecutively in document d."""
        curr = term_postings[0][d]
        if not curr: return False
        for i in range(1, len(term_postings)):
            nxt = set(term_postings[i][d])
            valid = [p + 1 for p in curr if (p + 1) in nxt]
            if not valid: return False
            curr = valid
        return len(curr) > 0

# Singleton instance
search_service = VectorSpaceService(
    dataset_dir=settings.DATASET_DIR,
    storage_dir=settings.STORAGE_DIR,
    stopwords_path=settings.STOPWORDS_PATH,
    vncorenlp_dir=settings.VNCORENLP_DIR,
    java_home=settings.JAVA_HOME
)
