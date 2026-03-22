import math
from collections import Counter

# ==========================================
# MODULE 2: PHÁT HIỆN LỖI SAI THEO NGỮ CẢNH
# ==========================================

class Module2_ContextChecker:
    def __init__(self, corpus_sentences):
        self.trigram_counts = Counter()
        self.bigram_counts = Counter()
        self.vocab = set()
        self.threshold = 0
        self._build_lm(corpus_sentences)
        
    def _build_lm(self, corpus):
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
        tokens = ["<s>", "<s>"] + sentence.strip().split() + ["</s>"]
        log_prob = 0
        V = len(self.vocab)
        if V == 0: return float('-inf')
        
        for i in range(2, len(tokens)):
            w1, w2, w3 = tokens[i-2], tokens[i-1], tokens[i]
            tri_count = self.trigram_counts.get((w1, w2, w3), 0)
            bi_count = self.bigram_counts.get((w1, w2), 0)
            
            p = (tri_count + 1) / (bi_count + V)
            log_prob += math.log(p)
        return log_prob
        
    def pipeline(self, query):
        """
        Thực hiện quy trình Module 2.
        """
        print(f"\n" + "="*50)
        print(f"--- BẮT ĐẦU PIPELINE MODULE 2 ---")
        print(f"[Input] Câu truy vấn: '{query}'")
        
        print(f"[Bước 1] Thêm token <s> và </s>, tiến hành đếm Trigram...")
        
        # 2. Tính log probability
        prob = self.calculate_log_prob(query)
        print(f"[Bước 2] Tổng Log Probability của câu là: {prob:.4f}")
        
        # 3. So sánh Threshold
        print(f"[Bước 3] So sánh với Threshold tham chiếu từ tập dữ liệu đúng: {self.threshold:.4f}")
        is_error = prob < self.threshold
        
        # 4. Output kết luận
        if is_error:
            print(f"[Output] KHÁNG ĐỊNH: Câu '{query}' CÓ KHẢ NĂNG SAI (LogProb < Threshold)")
        else:
            print(f"[Output] KHÁNG ĐỊNH: Câu '{query}' CHÍNH XÁC (LogProb >= Threshold)")
        print("="*50)
        
        return is_error

if __name__ == "__main__":
    print("⏳ Đang huấn luyện mô hình Trigram Language Model...")
    
    # Tập corpus giả định làm ngữ liệu
    CORPUS_DATA = [
        "quân ngũ",
        "quân đội việt nam",
        "nghỉ ngơi dưỡng sức",
        "suy nghĩ",
        "đi bộ",
        "buổi tối đi ngủ",
        "tôi nghĩ nghỉ ngơi là tốt nhất",
        "nhà cửa", 
        "làm việc",
        "công tác",
        "đời lính",
        "quân đội anh dũng",
        "ngủ ngon"
    ]
    mod2 = Module2_ContextChecker(CORPUS_DATA)
    print(f"✅ Hoàn tất! (Threshold = {mod2.threshold:.4f})")
    
    queries = [
        "quân phòng không", # test câu có tính hợp lệ cao
        "quân ngủ", 
        "nghĩ ngơi"
    ]
    
    for q in queries:
        mod2.pipeline(q)
