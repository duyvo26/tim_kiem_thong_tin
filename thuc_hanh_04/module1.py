from collections import defaultdict, Counter
import sys

# ==========================================
# MODULE 1: SỬA LỖI TỪNG TỪ ĐỘC LẬP
# ==========================================

def remove_accents(c):
    accents = {
        'a': 'aáàảãạăắằẳẵặâấầẩẫậ',
        'e': 'eéèẻẽẹêếềểễệ',
        'i': 'iíìỉĩị',
        'o': 'oóòỏõọôốồổỗộơớờởỡợ',
        'u': 'uúùủũụưứừửữự',
        'y': 'yýỳỷỹỵ',
        'd': 'dđ'
    }
    for k, v in accents.items():
        if c in v:
            return k
    return c

def replace_cost(c1, c2):
    if c1 == c2:
        return 0
    if remove_accents(c1) == remove_accents(c2):
        return 0.5
    return 1

def weighted_edit_distance(s1, s2):
    m = len(s1)
    n = len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = replace_cost(s1[i - 1], s2[j - 1])
            dp[i][j] = min(dp[i - 1][j] + 1,       # Delete cost = 1
                           dp[i][j - 1] + 1,       # Insert cost = 1
                           dp[i - 1][j - 1] + cost) # Replace cost
    return dp[m][n]

def get_kgrams(word, k=2):
    w = "$" + word + "$"
    return [w[i:i+k] for i in range(len(w) - k + 1)]

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0


class Module1_SpellChecker:
    def __init__(self, dict_path):
        self.vocab = set()
        self.kgram_index = defaultdict(list)
        self._load_dict(dict_path)
        
    def _load_dict(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    word = line.lower()
                    if word not in self.vocab:
                        self.vocab.add(word)
                        self._add_to_index(word)
        except Exception as e:
            print(f"Lỗi đọc từ điển: {e}")
            sys.exit(1)
                        
    def _add_to_index(self, word):
        kgrams = get_kgrams(word, k=2)
        for kg in set(kgrams):
            self.kgram_index[kg].append(word)
            
    def pipeline(self, word):
        """
        Thực hiện xử lý Pipeline Module 1
        """
        print(f"\n" + "="*50)
        print(f"--- BẮT ĐẦU PIPELINE MODULE 1 ---")
        print(f"[Input] Từ cần sửa: '{word}'")
        
        word = word.lower()
        
        # 1. Tạo k-grams
        word_kgrams = set(get_kgrams(word, k=2))
        print(f"[Bước 1] K-gram của từ '{word}': {word_kgrams}")
        
        # 2. Retrieve candidates từ chỉ mục + Jaccard >= 0.2
        candidate_counts = Counter()
        for kg in word_kgrams:
            for cand in self.kgram_index.get(kg, []):
                candidate_counts[cand] += 1
                
        candidates = []
        for cand, _ in candidate_counts.items():
            cand_kgrams_set = set(get_kgrams(cand, k=2))
            sim = jaccard_similarity(word_kgrams, cand_kgrams_set)
            if sim >= 0.2:
                candidates.append(cand)
                
        print(f"[Bước 2] Tìm thấy {len(candidates)} candidates qua Jaccard index (>= 0.2).")
        if not candidates:
            print(f"[Output] Không có candidate nào, giữ nguyên: '{word}'")
            return word
            
        # 3. Tính Weighted Edit Distance và chọn từ tốt nhất
        best_cand = word
        min_dist = float('inf')
        
        for cand in candidates:
            dist = weighted_edit_distance(word, cand)
            if dist < min_dist:
                min_dist = dist
                best_cand = cand
                
        print(f"[Bước 3] Tính Weighted Edit Distance (WED) để chọn từ tốt nhất.")
        print(f"  -> Ưu tiên min WED. Chọn: '{best_cand}' (Distance = {min_dist})")
        print(f"[Output] Từ đúng: '{best_cand}'")
        print("="*50)
        
        return best_cand

if __name__ == "__main__":
    DICT_FILE = "vietDict.txt"
    print("⏳ Đang xây dựng Module 1 (k-gram index) từ từ điển...")
    mod1 = Module1_SpellChecker(DICT_FILE)
    print(f"✅ Hoàn tất! Số lượng từ đơn vựng: {len(mod1.vocab)}")
    
    # Input dạng "từ" (word trong tiếng Việt có thể là từ ghép gồm nhiều tiếng)
    input_words = ["quân ngủ", "nghĩ ngơi"]
    for w in input_words:
        mod1.pipeline(w)
