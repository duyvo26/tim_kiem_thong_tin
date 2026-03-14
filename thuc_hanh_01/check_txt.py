import math

dictionary_file = "dictionary.txt"
index_file = "invertedIndex.txt"

TOTAL_DOCS = 12


def load_dictionary():
    dictionary = {}

    with open(dictionary_file, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) < 4:
                print("Sai format dictionary:", line)
                continue

            term = parts[0]
            if term == "Term":
                continue # Skip header

            df = int(parts[1])

            dictionary[term] = df

    return dictionary


def check_index(dictionary):
    with open(index_file, encoding="utf-8") as f:
        for line in f:

            parts = line.strip().split()

            if len(parts) < 2:
                print("Sai format index:", line)
                continue

            term = parts[0]

            if term not in dictionary:
                print("Term không có trong dictionary:", term)
                continue

            df = dictionary[term]
            postings = parts[1:]

            if len(postings) != df:
                print("DF mismatch:", term, "dictionary:", df, "index:", len(postings))

            for p in postings:

                if ":" not in p:
                    print("Posting sai format:", p)
                    continue

                docID, tfidf_str = p.split(":")
                tfidf_index = float(tfidf_str)

                # Lưu ý: TF-IDF hiện đã được lưu trực tiếp vào file invertedIndex.txt
                # File bài cũ lấy TF rồi tự nhân với idf on the fly.
                print(f"{term} -> doc {docID} TF-IDF (indexed) = {tfidf_index:.5f}")


dictionary = load_dictionary()
check_index(dictionary)