import os
import py_vncorenlp
import asyncio
import docx
import math
import collections
from pdfminer.high_level import extract_text
from crawl4ai import AsyncWebCrawler


DIR_ROOT = os.path.dirname(os.path.abspath(".env"))
java_path = r"C:\Program Files\Java\jdk1.8.0_202"
vncorenlp_model_path = os.path.join(DIR_ROOT, "vncorenlp")

os.environ["JAVA_HOME"] = java_path
os.environ["PATH"] = os.environ["JAVA_HOME"] + r"\bin;" + os.environ["PATH"]

if not os.path.exists(vncorenlp_model_path):
    py_vncorenlp.download_model(save_dir=vncorenlp_model_path)
    
# model = py_vncorenlp.VnCoreNLP(save_dir=vncorenlp_model_path)
model = py_vncorenlp.VnCoreNLP(
    save_dir=vncorenlp_model_path,
    annotators=["wseg"]  # chỉ tách từ
)


def read_doc(file_path):
    """
    Đọc nội dung từ tệp tin Word (.docx).
    
    Args:
        file_path (str): Đường dẫn đến file .docx
        
    Returns:
        str: Chuỗi văn bản chứa toàn bộ nội dung của file (các đoạn văn bản cách nhau bởi xuống dòng).
    """
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def read_pdf(file_path):
    """
    Đọc và trích xuất nội dung văn bản thô từ tệp tin PDF (.pdf).
    
    Args:
        file_path (str): Đường dẫn đến file .pdf
        
    Returns:
        str: Chuỗi văn bản được trích xuất từ file.
    """
    return extract_text(file_path)


async def process_html(file_path):
    """
    Đọc nội dung và làm sạch tệp tin HTML thông qua thư viện Crawl4AI.
    
    Args:
        file_path (str): Đường dẫn đến file .html hoặc .htm
        
    Returns:
        str: Nội dung file đã được lọc bỏ các thẻ HTML, chỉ giữ lại văn bản dưới chuẩn Markdown.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=f"file://{os.path.abspath(file_path)}", bypass_cache=True
        )

        # Sử dụng thuộc tính mới thay vì fit_markdown đã deprecated
        return result.markdown if type(result.markdown) == str else getattr(result.markdown, 'fit_markdown', getattr(result, 'markdown', ''))


def read_file(file_path):
    """
    Hàm tiện ích nhận diện file và chọn đúng hàm đọc tương ứng theo phần mở rộng của định dạng tệp.
    
    Args:
        file_path (str): Đường dẫn đến file cần đọc (.doc, .docx, .pdf, .html, .htm)
        
    Returns:
        str: Nội dung văn bản thô của file đã đọc.
        
    Raises:
        ValueError: Nếu định dạng file không nằm trong danh sách được hỗ trợ.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".doc", ".docx"]:
        return read_doc(file_path)

    elif ext == ".pdf":
        return read_pdf(file_path)

    elif ext in [".html"]:
        return asyncio.run(process_html(file_path))

    else:
        raise ValueError("Unsupported file type")


# load stopwords
def load_stopwords(path):
    """
    Đọc danh sách các từ dừng (stopwords) tiếng Việt.
    
    Args:
        path (str): Đường dẫn đến file text chứa danh sách stopwords.
        
    Returns:
        set: Tập hợp (set) chứa danh sách các từ dừng (giúp tra cứu độ phức tạp O(1)).
    """
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


# lọc stopwords từ json vncorenlp
def filter_stopwords(vncorenlp_json, stopwords):
    """
    Trích xuất từ (token) từ kết quả phân tách của VnCoreNLP, đưa về chữ thường và loại bỏ danh từ trong stopwords.
    
    Args:
        vncorenlp_json (dict|list): Cấu trúc dữ liệu trả về từ model py_vncorenlp sau khi gọi annotate_text()
        stopwords (set): Tập hợp các từ dừng để bị loại bỏ.
        
    Returns:
        list: Danh sách mảng các từ khóa (tokens) cuối cùng hợp lệ để bắt đầu đếm.
    """
    filtered_tokens = []

    # get sentences depending on the type of vncorenlp_json
    sentences = vncorenlp_json.values() if isinstance(vncorenlp_json, dict) else vncorenlp_json

    for sentence in sentences:
        for token in sentence:
            word = token["wordForm"].lower()
            if word not in stopwords:
                filtered_tokens.append(word)

    return filtered_tokens


def process_single_file(file_path, stopwords):
    """
    Xử lý vòng đời trọn vẹn cho 1 tài liệu nguyên bản: Đọc file -> Tách từ bằng vncorenlp -> Lọc stopwords.
    
    Args:
        file_path (str): Đường dẫn đến một file tài liệu cụ thể
        stopwords (set): Tập hợp các từ dừng stopwords
        
    Returns:
        list: Một danh sách mảng chứa các từ vựng hợp pháp của file đó. Trả về mảng rỗng [] nếu có lỗi xuất hiện.
    """
    try:
        data_text = read_file(file_path)
        data_model = model.annotate_text(data_text)
        return filter_stopwords(data_model, stopwords)
    except Exception as e:
        print(f"Lỗi khi xử lý {file_path}: {e}")
        return []

def build_inverted_index(dataset_dir, output_dir, stopwords_path):
    """
    Tạo bộ chỉ mục nghịch đảo Inverted Index tối ưu thời gian IO với cách đọc nạp 1 lần chạy (One Pass Indexing). 
    Kết quả ghi ra 2 tệp tin: dictionary.txt và invertedIndex.txt lưu các tham số cấu trúc TF-IDF cần thiết.
    
    Args:
        dataset_dir (str): Thư mục dữ liệu chứa kho văn bản tài liệu dạng hỗn hợp (.doc, .pdf, .html, ...).
        output_dir (str): Thư mục đích mà 2 cấu trúc tệp tin từ điển và chỉ mục sẽ được lưu xuất.
        stopwords_path (str): File text liệt kê stopwords để lọc.
    """
    stopwords = load_stopwords(stopwords_path)
    
    # dictionary trung gian lưu: term -> {doc_id: term_frequency}
    # Việc này giúp ta chỉ đọc và xử lý mỗi tài liệu 1 lần duy nhất
    inverted_index_raw = collections.defaultdict(dict)
    
    doc_count = 0
    # 1. Đọc qua thư mục tài liệu
    for filename in os.listdir(dataset_dir):
        file_path = os.path.join(dataset_dir, filename)
        if os.path.isfile(file_path):
            tokens = process_single_file(file_path, stopwords)
            if not tokens:
                continue
            
            # Tính TF thô (số lượng của từng từ trong tài liệu)
            term_freqs = collections.Counter(tokens)
            
            for term, count in term_freqs.items():
                inverted_index_raw[term][filename] = count
                
            doc_count += 1
            print(f"Đã xử lý xong: {filename}")

    if doc_count == 0:
        print("Không có tài liệu nào để lập chỉ mục.")
        return

    # 2. Xây dựng và ghi ra hai tập tin dictionary.txt, invertedIndex.txt
    os.makedirs(output_dir, exist_ok=True)
    dict_path = os.path.join(output_dir, "dictionary.txt")
    inv_path = os.path.join(output_dir, "invertedIndex.txt")
    
    with open(dict_path, "w", encoding="utf-8") as f_dict, \
         open(inv_path, "w", encoding="utf-8") as f_inv:
        
        # Tiêu đề cột
        f_dict.write("Term\tDF\tIDF\tOffset_trong_InvertedIndex(byte)\n")
        
        offset = 0
        for term, postings in inverted_index_raw.items():
            df = len(postings)
            idf = math.log10(doc_count / df) # công thức log cơ số 10
            
            # Xây dựng xâu lưu danh sách posting của "term"
            posting_strs = []
            for doc_id, tf in postings.items():
                # Tính TF-IDF
                tf_idf = tf * idf
                posting_strs.append(f"{doc_id}:{tf_idf:.5f}")
                
            # Cấu trúc ghi: <docId1>:<tfidf1> <docId2>:<tfidf2> ...
            posting_line = " ".join(posting_strs) + "\n"
            
            # Tính độ dài của chuỗi được mã hóa UTF-8 để trỏ đến đầu chuỗi kế tiếp
            byte_len = len(posting_line.encode("utf-8"))
            
            f_inv.write(posting_line)
            f_dict.write(f"{term}\t{df}\t{idf:.5f}\t{offset}\n")
            
            offset += byte_len


if __name__ == "__main__":
    dataset_folder = r"F:\thac_si\tim_kiem_thong_tin\thuc_hanh_01\dataset"
    output_folder = r"F:\thac_si\tim_kiem_thong_tin\thuc_hanh_01"
    stopwords_path = r"F:\thac_si\tim_kiem_thong_tin\thuc_hanh_01\vietnamese-stopwords.txt"
    build_inverted_index(dataset_folder, output_folder, stopwords_path)
