# BÁO CÁO THỰC HÀNH: TÌM KIẾM NHANH VỚI CLUSTER PRUNING

## 1. Yêu cầu và Giải thuật
- **Cụm tài liệu**: Sử dụng Cosine Similarity.
- **Số lượng cụm (k)**: 6 (Căn bậc hai của số lượng tài liệu).
- **Gán Follower**: Mỗi tài liệu thuộc về 2 cụm (2 leaders gần nhất).

## 2. Giai đoạn Tìm kiếm nhanh (Fast Search)
- **Bước 1**: Tạo vec-tơ biểu diễn cho truy vấn.
- **Bước 2**: Tìm 2 leaders gần nhất.
- **Bước 3**: Chỉ tìm kiếm trong các followers của 2 leader này.

## 3. Kết quả Thực nghiệm (Search Logs)
### Truy vấn: `Buổi 5 – Tìm kiếm nhanh sử dụng kỹ thuật Cluster pruning`
| STT | Tên tài liệu | Điểm số (Score) |
| :-- | :--- | :--- |
| 1 | 1006.pdf | 0.1517 |
| 2 | 1001.docx | 0.0848 |
| 3 | 1007.pdf | 0.0749 |
| 4 | 1002.docx | 0.0355 |
| 5 | 1010.pdf | 0.0325 |

### Truy vấn: `windows xp`
| STT | Tên tài liệu | Điểm số (Score) |
| :-- | :--- | :--- |
| 1 | 1003.docx | 0.4620 |
| 2 | 1005.docx | 0.3375 |
| 3 | 1002.docx | 0.2681 |
| 4 | 1001.docx | 0.2509 |
| 5 | 1008.pdf | 0.0995 |

### Truy vấn: `bảng lương công an`
- *Không tìm thấy kết quả.*

### Truy vấn: `Sử dụng thuật toán cải tiến để tạo các cụm tài liệu`
| STT | Tên tài liệu | Điểm số (Score) |
| :-- | :--- | :--- |
| 1 | 1006.pdf | 0.1829 |
| 2 | 1002.docx | 0.0969 |
| 3 | 1010.pdf | 0.0887 |
| 4 | 1009.pdf | 0.0531 |
| 5 | 1001.docx | 0.0450 |


---
*Báo cáo được tạo tự động và kết thúc quy trình.*