import math
from app.services.ranking import RankingCalculator

def main():
    print("--- Demo: TF-IDF & Cosine Similarity Ranking ---")
    
    # Giả sử chúng ta có 1 tập các từ khóa (vocabulary) và giá trị IDF tương ứng
    # IDF = log10(N/df)
    idf_map = {
        "tìm_kiếm": 0.5,
        "thông_tin": 0.3,
        "thuật_toán": 0.8,
        "cosine": 1.2
    }
    
    # 1. Xử lý Truy vấn (Query): "tìm kiếm thông tin cosine"
    # Giả sử truy vấn đã được tokenize thành: ["tìm_kiếm", "thông_tin", "cosine"]
    query_tokens = ["tìm_kiếm", "thông_tin", "cosine"]
    query_tf = {"tìm_kiếm": 1, "thông_tin": 1, "cosine": 1}
    
    query_vector = {}
    for term, tf in query_tf.items():
        if term in idf_map:
            weight = RankingCalculator.calculate_tfidf(tf, idf_map[term])
            query_vector[term] = weight
            
    print(f"Query Vector (weights): {query_vector}")

    # 2. Xử lý Tài liệu (Document): "hệ thống tìm kiếm thông tin bằng thuật toán"
    # Tokenized: ["hệ_thống", "tìm_kiếm", "thông_tin", "thuật_toán"]
    doc_tf = {"hệ_thống": 1, "tìm_kiếm": 1, "thông_tin": 1, "thuật_toán": 1}
    
    # Trọng số tài liệu cho các từ khớp với truy vấn
    doc_matching_vector = {}
    for term in query_vector:
        tf = doc_tf.get(term, 0)
        weight = RankingCalculator.calculate_tfidf(tf, idf_map.get(term, 0))
        doc_matching_vector[term] = weight

    # Tính Norm (độ dài) của toàn bộ tài liệu (để chuẩn hóa Cosine)
    doc_full_vector_sq_sum = 0.0
    for term, tf in doc_tf.items():
        idf = idf_map.get(term, 1.0) # Mặc định IDF=1 nếu không có trong map demo
        w = RankingCalculator.calculate_tfidf(tf, idf)
        doc_full_vector_sq_sum += w*w
    doc_norm = math.sqrt(doc_full_vector_sq_sum)

    print(f"Doc Matching Vector: {doc_matching_vector}")
    print(f"Doc Norm: {doc_norm:.4f}")

    # 3. Tính điểm xếp hạng (Ranking Score) bằng Cosine Similarity
    score = RankingCalculator.calculate_cosine_similarity(query_vector, doc_matching_vector, doc_norm)
    
    print(f"\n=> Kết quả điểm Cosine Similarity: {score:.4f}")

if __name__ == "__main__":
    main()
