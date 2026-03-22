# Cần cài đặt: pip install aspose-words
import aspose.words as aw
import os

def read_doc_with_aspose(file_path):
    try:
        # Load tài liệu .doc hoặc .docx
        doc = aw.Document(file_path)
        
        # Trích xuất toàn bộ text (có thể dùng get_text() hoặc lưu tạm ra .txt)
        text = doc.get_text()
        
        # Aspose thường thêm thông tin bản quyền ở đầu/cuối nếu dùng bản free
        return text
    except Exception as e:
        print(f"Lỗi khi đọc file bằng Aspose: {e}")
        return None

if __name__ == "__main__":
    # Test với một file .doc bất kỳ
    test_file = r"f:\thac_si\tim_kiem_thong_tin\thuc_hanh_05\dataset _B5_1\dataset _B5\10004.doc"
    if os.path.exists(test_file):
        content = read_doc_with_aspose(test_file)
        if content:
            print(f"--- Nội dung file (Aspose) ---")
            print(content[:500])
        else:
            print("Không đọc được nội dung.")
    else:
        print("Không tìm thấy file.")
