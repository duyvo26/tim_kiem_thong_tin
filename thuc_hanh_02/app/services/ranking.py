import math
from typing import Dict, List

class RankingCalculator:
    """
    Utility class implementing TF-IDF weighting and Cosine Similarity ranking.
    Used for Information Retrieval tasks.
    """

    @staticmethod
    def calculate_tf_weight(tf: int) -> float:
        """
        Calculates logarithmic Term Frequency (TF) weight.
        Formula: 1 + log10(tf) if tf > 0 else 0
        """
        if tf > 0:
            return 1.0 + math.log10(tf)
        return 0.0

    @staticmethod
    def calculate_tfidf(tf: int, idf: float) -> float:
        """
        Calculates TF-IDF weight.
        Formula: TF_weight * IDF
        """
        return RankingCalculator.calculate_tf_weight(tf) * idf

    @staticmethod
    def calculate_cosine_similarity(query_vector: Dict[str, float], doc_vector: Dict[str, float], doc_norm: float | None = None) -> float:
        """
        Calculates Cosine Similarity between a query vector and a document vector.
        Formula: DotProduct(Q, D) / (|Q| * |D|)
        
        :param query_vector: Dict mapping term to its weight in query
        :param doc_vector: Dict mapping term to its weight in doc (only for terms in query)
        :param doc_norm: Pre-calculated norm (Euclidean length) of the document vector
        :return: Cosine Similarity score [0, 1]
        """
        # Calculate Dot Product
        dot_product: float = 0.0
        for term, q_weight in query_vector.items():
            if term in doc_vector:
                dot_product += float(q_weight * doc_vector[term])
        
        # Calculate Query Norm
        q_norm_sq: float = sum(float(w**2) for w in query_vector.values())
        query_norm: float = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0
        
        # Use provided doc_norm or calculate it (though usually pre-stored for speed)
        actual_doc_norm: float = 0.0
        if doc_norm is not None:
            actual_doc_norm = doc_norm
        else:
            d_norm_sq: float = sum(float(w**2) for w in doc_vector.values())
            actual_doc_norm = math.sqrt(d_norm_sq) if d_norm_sq > 0 else 1.0
            
        if query_norm * actual_doc_norm == 0:
            return 0.0
            
        return dot_product / (query_norm * actual_doc_norm)

if __name__ == "__main__":
    # Demonstration of the logic
    calc = RankingCalculator()
    
    # Mock data
    # Query: "thông tin"
    # Doc 1: "tìm kiếm thông tin"
    # Doc 2: "thông tin là quan trọng"
    
    # Let's assume IDF values (pre-calculated from corpus)
    idf_values = {"thông": 0.5, "tin": 0.5, "kiếm": 1.2, "quan": 1.5, "trọng": 1.5}
    
    # 1. Query Vector (Q)
    # tf("thông")=1, tf("tin")=1
    q_weights = {
        "thông": calc.calculate_tfidf(1, idf_values["thông"]),
        "tin": calc.calculate_tfidf(1, idf_values["tin"])
    }
    
    # 2. Doc Vector (D1) for "tìm kiếm thông tin"
    # tf("thông")=1, tf("tin")=1
    d1_weights_matching = {
        "thông": calc.calculate_tfidf(1, idf_values["thông"]),
        "tin": calc.calculate_tfidf(1, idf_values["tin"])
    }
    # Pre-calculated norm for Doc 1 (including all terms in doc, not just query matches)
    # d1 = ["tìm", "kiếm", "thông", "tin"]
    d1_all_terms = {"tìm": 1.2, "kiếm": 1.2, "thông": 0.5, "tin": 0.5} 
    d1_norm = math.sqrt(sum(v**2 for v in d1_all_terms.values()))
    
    # Calculate Similarity
    score = calc.calculate_cosine_similarity(q_weights, d1_weights_matching, d1_norm)
    
    print(f"Query Weights: {q_weights}")
    print(f"Doc weights (matches): {d1_weights_matching}")
    print(f"Doc Norm: {d1_norm:.4f}")
    print(f"Cosine Similarity Score: {score:.4f}")
