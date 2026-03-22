import math
import pickle
import os
from collections import Counter
from datasets import load_dataset

# ==========================================
# MODULE 2: PHAT HIEN LOI SAI THEO NGU CANH
# ==========================================

class Module2_ContextChecker:
    """
    Lop thuc hien viec xac dinh loi sai chinh ta theo ngu canh su dung mo hinh Trigram Language Model.
    """
    def __init__(self, corpus_sentences=None, model_path="trigram_lm.pkl"):
        """
        Khoi tao Module 2. Neu co model san thi load, neu khong thi huan luyen tu corpus.
        
        Args:
            corpus_sentences (list, optional): Danh sach cac cau chuan de huan luyen model.
            model_path (str): Duong dan de luu/load model. Mac dinh la "trigram_lm.pkl".
        """
        self.trigram_counts = Counter()
        self.bigram_counts = Counter()
        self.vocab = set()
        self.threshold = 0.0
        
        if os.path.exists(model_path):
            self.load_model(model_path)
        elif corpus_sentences is not None:
            self._build_lm(corpus_sentences)
            self.save_model(model_path)
        else:
            raise ValueError("Khong co model_path va khong co corpus_sentences de huan luyen.")
            
    def save_model(self, path):
        """
        Luu model hien tai vao tep pickle.
        
        Args:
            path (str): Duong dan tep luu model.
        """
        with open(path, 'wb') as f:
            pickle.dump({
                'trigram_counts': self.trigram_counts,
                'bigram_counts': self.bigram_counts,
                'vocab': self.vocab,
                'threshold': self.threshold
            }, f)
            print(f"Da luu model tai: {path}")
            
    def load_model(self, path):
        """
        Tai model tu tep pickle vao bo nho.
        
        Args:
            path (str): Duong dan tep model.
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.trigram_counts = data['trigram_counts']
            self.bigram_counts = data['bigram_counts']
            self.vocab = data['vocab']
            self.threshold = data['threshold']
        
    def _build_lm(self, corpus):
        """
        Xay dung mo hinh ngon ngu Trigram tu tap corpus va tinh toan Threshold.
        
        Args:
            corpus (list): Danh sach cac cau chuan de huan luyen.
        """
        log_probs = []
        for sentence in corpus:
            tokens = ["<s>", "<s>"] + sentence.lower().split() + ["</s>"]
            for i in range(2, len(tokens)):
                w1, w2, w3 = tokens[i-2], tokens[i-1], tokens[i]
                self.trigram_counts[(w1, w2, w3)] += 1
                self.bigram_counts[(w1, w2)] += 1
                self.vocab.add(w3)
                
        for sentence in corpus:
            log_probs.append(self.calculate_log_prob(sentence.lower()))
            
        if log_probs:
            mean = sum(log_probs) / len(log_probs)
            if len(log_probs) > 1:
                std = math.sqrt(sum((x - mean)**2 for x in log_probs) / len(log_probs)) 
            else:
                std = 0
            self.threshold = mean - 2 * std
            
    def calculate_log_prob(self, sentence):
        """
        Tinh Log Probability cho mot cau dua tren mo hinh Trigram voi Laplace smoothing.
        
        Args:
            sentence (str): Cau can tinh xac suat.
            
        Returns:
            float: Gia tri Log Probability trung binh tren moi trigram.
        """
        tokens = ["<s>", "<s>"] + sentence.strip().split() + ["</s>"]
        log_prob = 0
        V = len(self.vocab)
        if V == 0: return float('-inf')
        
        num_trigrams = len(tokens) - 2
        
        for i in range(2, len(tokens)):
            w1, w2, w3 = tokens[i-2], tokens[i-1], tokens[i]
            tri_count = self.trigram_counts.get((w1, w2, w3), 0)
            bi_count = self.bigram_counts.get((w1, w2), 0)
            
            p = (tri_count + 1) / (bi_count + V)
            log_prob += math.log(p)
            
        return log_prob / num_trigrams if num_trigrams > 0 else 0
        
    def pipeline(self, query):
        """
        Thuc hien quy trinh kiem tra ngu canh cho mot cau truy van.
        
        Args:
            query (str): Cau truy van can kiem tra.
            
        Returns:
            bool: True neu phat hien loi sai ngu canh (prob < threshold), False neu binh thuong.
        """
        print(f"\n" + "="*50)
        print(f"--- BAT DAU PIPELINE MODULE 2 ---")
        print(f"[Input] Cau truy van: '{query}'")
        
        prob = self.calculate_log_prob(query)
        print(f"[Buoc 1] Trung binh LogProb/Trigram cua cau la: {prob:.4f}")
        print(f"[Buoc 2] So sanh voi Threshold tham chieu: {self.threshold:.4f}")
        
        is_error = prob < self.threshold
        
        if is_error:
            print(f"[Output] KHANG DINH: Truy van '{query}' CO LOI SAI NGU CANH")
        else:
            print(f"[Output] KHANG DINH: Truy vấn '{query}' hop ngu canh")
        print("="*50)
        
        return is_error

if __name__ == "__main__":
    MODEL_PATH = "trigram_lm.pkl"
    CORPUS_DATA = []
    
    if not os.path.exists(MODEL_PATH):
        print("Chua co model huan luyen. Lay dataset mau tu Hugging Face (undertheseanlp/UVB-v0.1)...")
        # Lay 10 records cho demo nhanh
        ds = load_dataset("undertheseanlp/UVB-v0.1", split="train[:50]")
        
        for item in ds:
            text_content = item.get('content', '')
            if text_content:
                sentences = text_content.replace('\n', '.').replace('!', '.').replace('?', '.').split('.')
                for s in sentences:
                    s = s.strip()
                    if s and len(s.split()) >= 3:
                        CORPUS_DATA.append(s)
        
        print(f"Hoan tat trich xuat {len(CORPUS_DATA)} mau cau.")
        mod2 = Module2_ContextChecker(corpus_sentences=CORPUS_DATA, model_path=MODEL_PATH)
    else:
        print(f"Da tim thay Model '{MODEL_PATH}'. Loading...")
        mod2 = Module2_ContextChecker(model_path=MODEL_PATH)
        
    print(f"San sang! Threshold hien tai cua LM: {mod2.threshold:.4f}")
    
    queries = [
        "phát triển kinh tế xã hội",
        "phát triển kinh tế ngủ",
        "quân ngủ",
        "nghĩ ngơi",
    ]
    
    for q in queries:
        mod2.pipeline(q)
