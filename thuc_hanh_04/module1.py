from collections import defaultdict, Counter
import sys

# ==========================================
# MODULE 1: SUA LOI TUNG TU DOC LAP
# ==========================================

def remove_accents(c):
    """
    Loai bo dau tieng Viet cua mot ky tu.
    
    Args:
        c (str): Ky tu can bo dau.
        
    Returns:
        str: Ky tu da duoc loai bo dau.
    """
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
    """
    Tinh chi phi thay the giua hai ky tu.
    
    Args:
        c1 (str): Ky tu thu nhat.
        c2 (str): Ky tu thu hai.
        
    Returns:
        float: Chi phi thay the (0 neu giong, 0.5 neu khac dau, 1 neu khac hoan toan).
    """
    if c1 == c2:
        return 0
    if remove_accents(c1) == remove_accents(c2):
        return 0.5
    return 1

def weighted_edit_distance(s1, s2):
    """
    Tinh khoang cach hieu chinh co trong so (Weighted Edit Distance) giua hai chuoi.
    
    Args:
        s1 (str): Chuoi thu nhat.
        s2 (str): Chuoi thu hai.
        
    Returns:
        float: Khoang cach WED giua hai chuoi.
    """
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
    """
    Tao danh sach k-gram cho mot tu.
    
    Args:
        word (str): Tu can tao k-gram.
        k (int): Do dai k-gram. Mac dinh la 2.
        
    Returns:
        list: Danh sach cac k-gram cua tu.
    """
    w = "$" + word + "$"
    return [w[i:i+k] for i in range(len(w) - k + 1)]

def jaccard_similarity(set1, set2):
    """
    Tinh do tuong dong Jaccard giua hai tap hop.
    
    Args:
        set1 (set): Tap hop thu nhat.
        set2 (set): Tap hop thu hai.
        
    Returns:
        float: Gia tri do tuong dong Jaccard (tu 0 den 1).
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0


class Module1_SpellChecker:
    """
    Lop thuc hien viec sua loi chinh ta tung tu doc lap su dung k-gram va WED.
    """
    def __init__(self, dict_path):
        """
        Khoi tao Module 1 voi duong dan den tu dien.
        
        Args:
            dict_path (str): Duong dan den tep tu dien (vi du: vietDict.txt).
        """
        self.vocab = set()
        self.kgram_index = defaultdict(list)
        self._load_dict(dict_path)
        
    def _load_dict(self, path):
        """
        Tai tu dien vao bo nho va xay dung chi muc k-gram.
        
        Args:
            path (str): Duong dan tep tu dien.
        """
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
            print(f"Loi doc tu dien: {e}")
            sys.exit(1)
                        
    def _add_to_index(self, word):
        """
        Them mot tu vao chi muc k-gram.
        
        Args:
            word (str): Tu can them vao chi muc.
        """
        kgrams = get_kgrams(word, k=2)
        for kg in set(kgrams):
            self.kgram_index[kg].append(word)
            
    def pipeline(self, word):
        """
        Thuc hien quy trinh sua loi cho mot tu (input).
        
        Args:
            word (str): Tu can kiem tra va sua loi.
            
        Returns:
            str: Tu da duoc sua loi (hoac tu goc neu khong tim thay ung vien tot hon).
        """
        print(f"\n" + "="*50)
        print(f"--- BAT DAU PIPELINE MODULE 1 ---")
        print(f"[Input] Tu can sua: '{word}'")
        
        word = word.lower()
        
        # 1. Tao k-grams
        word_kgrams = set(get_kgrams(word, k=2))
        print(f"[Buoc 1] K-gram cua tu '{word}': {word_kgrams}")
        
        # 2. Retrieve candidates tu chi muc + Jaccard >= 0.2
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
                
        print(f"[Buoc 2] Tim thay {len(candidates)} candidates qua Jaccard index (>= 0.2).")
        if not candidates:
            print(f"[Output] Khong co candidate nao, giu nguyen: '{word}'")
            return word
            
        # 3. Tinh Weighted Edit Distance va chon tu tot nhat
        best_cand = word
        min_dist = float('inf')
        
        for cand in candidates:
            dist = weighted_edit_distance(word, cand)
            if dist < min_dist:
                min_dist = dist
                best_cand = cand
                
        print(f"[Buoc 3] Tinh Weighted Edit Distance (WED) de chon tu tot nhat.")
        print(f"  -> Uu tien min WED. Chon: '{best_cand}' (Distance = {min_dist})")
        print(f"[Output] Tu dung: '{best_cand}'")
        print("="*50)
        
        return best_cand

if __name__ == "__main__":
    DICT_FILE = "vietDict.txt"
    print("Dang xay dung Module 1 (k-gram index) tu tu dien...")
    mod1 = Module1_SpellChecker(DICT_FILE)
    print(f"Hoan tat! So luong tu don vung: {len(mod1.vocab)}")
    
    # Input dang "tu" (word trong tieng Viet co the la tu ghep gom nhieu tieng)
    input_words = ["quân ngủ", "nghĩ ngơi"]
    for w in input_words:
        mod1.pipeline(w)
