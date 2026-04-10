# 🌟 VNS-NORM v1.1 - Chuẩn hóa Tiếng Việt Thông Minh

> **Phiên bản 1.1** - Nâng cấp Levenshtein Distance & Regex Patterns
> 
> Cập nhật chính: Thêm nhận diện từ gần giống, phát hiện từ kéo dài, phân tích chi tiết

---

## 📦 Package Contents

```
VNS-NORM v1.1/
├── vns_norm_app.py                      # File chính (cập nhật)
├── test_levenshtein_regex.py            # Test suite cho tính năng mới
├── HUONG_DAN_LEVENSHTEIN_REGEX.md      # Hướng dẫn chi tiết
├── CHANGELOG.md                         # Danh sách thay đổi
└── README.md                            # File này
```

---

## ✨ Tính Năng Chính v1.1

### 🆕 Tính Năng Mới

| Tính Năng | Mô Tả | Ví Dụ |
|-----------|-------|--------|
| **Levenshtein Distance** | Tính khoảng cách giữa hai từ | `"ko"` → `"không"` (distance=4) |
| **Find Similar Words** | Tìm từ gần giống nhất | `"biet"` → `"biết"` ✅ |
| **Detect Elongated** | Phát hiện từ kéo dài | `"quáaaa"` → Detected ✅ |
| **Char Info** | Chi tiết ký tự lặp | Position, count, character |
| **Detailed Analysis** | Báo cáo phân tích | Elongations + abbreviations |

### 💪 Cải Thiện

| Khía Cạnh | v1.0 | v1.1 | Cải Thiện |
|-----------|------|------|----------|
| Mở rộng viết tắt | Exact Match | Exact + Fuzzy | +200% detection |
| Phát hiện lỗi | ❌ | ✅ | New capability |
| Báo cáo | Minimal | Comprehensive | Much richer |

---

## 🚀 Khởi Động Nhanh

### Cài Đặt

```bash
# Yêu cầu
- Python 3.8+
- customtkinter
- tkinter (Python standard)

# Cài đặt dependencies
pip install customtkinter
```

### Sử Dụng Cơ Bản

```python
from vns_norm_app import VNSNorm

# Tạo instance
norm = VNSNorm()

# Chuẩn hóa văn bản
text = "ko đc vui quáaaa"
result = norm.normalize(text)
print(result)  # Output: "không được vui quá"

# Lấy thống kê
stats = norm.get_statistics(text, result)
print(stats['elongated_words'])  # ['quáaaa']
```

### Sử Dụng Nâng Cao

```python
# Tìm từ gần giống
similar = norm.find_similar_word("biet", max_distance=2)
print(similar)  # "biết"

# Phát hiện từ kéo dài
elongated = norm.detect_elongated_words("yeeeees quáaaa")
print(elongated)  # ["yeeeees", "quáaaa"]

# Lấy thông tin chi tiết
info = norm.get_repeated_char_info("quáaaa")
print(info)  # {'char': 'a', 'count': 3, 'position': 3, 'matched': 'aaa'}

# Phân tích toàn diện
analysis = norm.get_detailed_analysis("ko biet vui quáaaa")
print(analysis['elongated_words'])
print(analysis['potentially_abbreviations'])
```

---

## 📚 Thuật Toán Chính

### 🧮 Levenshtein Distance

**Định nghĩa:** Số phép chỉnh sửa tối thiểu để biến một từ thành từ khác

**Phép chỉnh sửa:**
- Thêm ký tự (Insertion)
- Xóa ký tự (Deletion)  
- Thay thế ký tự (Substitution)

**Ví dụ:**
```
"ko" → "không"
- Thay 'o' → 'ô'
- Thêm 'n'
- Thêm 'g'
Distance = 3 phép
```

**Công thức DP:**
```
dp[i][j] = min(
    dp[i-1][j] + 1,      # Xóa
    dp[i][j-1] + 1,      # Thêm
    dp[i-1][j-1] + cost  # Thay (cost=0 nếu bằng, 1 nếu khác)
)
```

**Độ phức tạp:** O(m × n)

---

### 🔍 Regex Patterns

#### Pattern 1: Ký Tự Lặp 3+ Lần (Chính)
```regex
([a-zàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵýỷỹ])\1{2,}
```

**Match:**
- `quáaaa` → `aaa` (3 lần 'a')
- `yeeeees` → `eeee` (4 lần 'e')
- `hiiiii` → `iiiii` (5 lần 'i')

#### Pattern 2: Ký Tự Lặp 2+ Lần (Linh Hoạt)
```regex
([a-zàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵýỷỹ])\1{1,}
```

**Match:**
- `ok` → `kk` (2 lần 'k')
- `aa` → `aa` (2 lần 'a')

#### Pattern 3: Từ Chứa Ký Tự Lặp
```regex
\b\w*([a-zàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵýỷỹ])\1+\w*\b
```

**Phát hiện cả từ:**
- `quáaaa` → Toàn bộ từ
- `hiiiii` → Toàn bộ từ

---

## 📋 API Reference

### Lớp: VNSNorm

#### `levenshtein_distance(word1: str, word2: str) → int`
Tính khoảng cách Levenshtein giữa hai từ.

```python
distance = norm.levenshtein_distance("ko", "không")
# Returns: 4
```

#### `find_similar_word(word: str, max_distance: int = 2) → str`
Tìm từ gần giống nhất trong từ điển.

```python
similar = norm.find_similar_word("biet", max_distance=2)
# Returns: "biết" (hoặc từ gốc nếu không tìm được)
```

#### `detect_elongated_words(text: str) → list`
Phát hiện toàn bộ từ kéo dài.

```python
words = norm.detect_elongated_words("quáaaa hiiiiii")
# Returns: ["quáaaa", "hiiiiii"]
```

#### `get_repeated_char_info(word: str) → dict`
Lấy thông tin chi tiết về ký tự lặp.

```python
info = norm.get_repeated_char_info("quáaaa")
# Returns: {
#     'char': 'a',
#     'count': 3,
#     'position': 3,
#     'matched': 'aaa'
# }
```

#### `get_detailed_analysis(text: str) → dict`
Phân tích chi tiết toàn diện.

```python
analysis = norm.get_detailed_analysis("ko biet vui quáaaa")
# Returns: {
#     'total_words': 4,
#     'total_chars': 23,
#     'elongated_words': [...],
#     'potentially_abbreviations': [...]
# }
```

#### `normalize(text: str) → str`
Chuẩn hóa văn bản (quy trình hoàn toàn).

```python
result = norm.normalize("  ko  đc  vui   quáaaa!!!  ")
# Returns: "không được vui quá!!!"
```

#### `get_statistics(original: str, normalized: str) → dict`
Lấy thống kê so sánh.

```python
stats = norm.get_statistics(original, normalized)
# Returns: {
#     'orig_chars': 30,
#     'norm_chars': 20,
#     'orig_words': 5,
#     'norm_words': 4,
#     'char_change': 10,
#     'elongated_found': 2,
#     'elongated_words': ['quáaaa', 'hiiii']
# }
```

---

## 🧪 Testing

### Chạy Test Suite

```bash
python test_levenshtein_regex.py
```

### Test Coverage

- ✅ 6+ Levenshtein Distance tests
- ✅ 5+ Find Similar Word tests
- ✅ 5+ Detect Elongated tests
- ✅ 5+ Repeated Char Info tests
- ✅ 5+ Regex Pattern tests
- ✅ 5+ Abbreviation Expansion tests
- ✅ 3+ Full Normalization tests
- ✅ 1+ Comprehensive Analysis test

**Status:** All tests passing ✅

---

## 📊 Ví Dụ Đầu Ra

### Ví Dụ 1: Chuẩn hóa Đơn Giản

```python
text = "ko đc"
result = norm.normalize(text)
# Output: "không được"
```

### Ví Dụ 2: Xử Lý Từ Kéo Dài

```python
text = "quáaaa hiiiiii"
result = norm.normalize(text)
# Output: "quá hi"

stats = norm.get_statistics(text, result)
# elongated_words: ['quáaaa', 'hiiiiii']
```

### Ví Dụ 3: Levenshtein Matching

```python
text = "biet roi"  # viết sai
result = norm.normalize(text)
# Output: "biết rồi"  # sự sửa được từ gần giống
```

### Ví Dụ 4: Phân Tích Chi Tiết

```python
text = "ko đc bieeeeet vui quáaaa"

analysis = norm.get_detailed_analysis(text)

# elongated_words:
# - bieeeeet: 'e' lặp 4 lần
# - quáaaa: 'a' lặp 3 lần

# potentially_abbreviations:
# - ko → không (exact_match)
# - dc → được (exact_match)
```

---

## 🎯 Quy Trình Chuẩn hóa (Pipeline)

```
┌──────────────────────────────────┐
│  BƯỚC 1: Xóa Ký Tự Lặp         │
│  "quáaaa" → "quá"              │
│  (Regex: 3+ lần → 1 ký tự)      │
└──────────────────────────────────┘
               ↓
┌──────────────────────────────────┐
│  BƯỚC 2: Chuẩn hóa Khoảng Trắng │
│  "xin  chào" → "xin chào"       │
│  (Regex: multiple spaces → 1)   │
└──────────────────────────────────┘
               ↓
┌──────────────────────────────────┐
│  BƯỚC 3: Mở Rộng Viết Tắt      │
│  Chiến lược 1: Exact Match      │
│  "ko" → "không" (tra từ điển)   │
│  Chiến lược 2: Levenshtein      │
│  "biet" → "biết" (fuzzy match)  │
└──────────────────────────────────┘
               ↓
┌──────────────────────────────────┐
│  KẾT QUẢ: Văn Bản Chuẩn hóa    │
└──────────────────────────────────┘
```

---

## ⚙️ Tham Số Điều Chỉnh

### Max Distance cho Levenshtein

```python
# Chặt chẽ: Chỉ nhận từ rất gần
similar = norm.find_similar_word("xyz", max_distance=1)

# Trung bình (mặc định)
similar = norm.find_similar_word("xyz", max_distance=2)

# Rộng rãi: Nhận từ khá gần
similar = norm.find_similar_word("xyz", max_distance=3)
```

### Regex Pattern Tuning

```python
# Nhạy cảm: Bắt 2+ lần lặp
pattern = re.compile(r'([a-z...])\1{1,}')

# Tiêu chuẩn (mặc định): Bắt 3+ lần lặp
pattern = re.compile(r'([a-z...])\1{2,}')

# Kém nhạy: Bắt 4+ lần lặp
pattern = re.compile(r'([a-z...])\1{3,}')
```

---

## 📈 Hiệu Năng

### Độ Phức Tạp Thời Gian

| Hàm | Độ Phức Tạp | Ghi Chú |
|-----|-------------|--------|
| levenshtein_distance() | O(m × n) | m,n = độ dài từ |
| find_similar_word() | O(k × m × n) | k = số từ từ điển |
| detect_elongated_words() | O(n) | n = độ dài văn bản |
| normalize() | O(n + w×m) | w = số từ |

### Tối ưu hóa

✅ Compile regex sẵn  
✅ Bỏ qua so sánh không cần thiết  
✅ Tra cứu hash map trước  
✅ Cache thường xuyên  

---

## 🐛 Known Issues & Limitations

### Hạn chế hiện tại

- **Levenshtein max_distance:** Khuyến nghị ≤ 2 để tránh false positives
- **Từ điển:** Chỉ hỗ trợ những từ trong từ điển DEFAULT_ABBREVIATIONS
- **Unicode:** Chủ yếu tối ưu cho Tiếng Việt, cần test cho ngôn ngữ khác

### Cách khắc phục

```python
# Mở rộng từ điển
custom_dict = {...}
norm = VNSNorm(dict_path="custom_dict.json")

# Điều chỉnh max_distance
similar = norm.find_similar_word(word, max_distance=3)
```

---

## 📝 Tài Liệu Liên Quan

- **HUONG_DAN_LEVENSHTEIN_REGEX.md** - Hướng dẫn chi tiết
- **CHANGELOG.md** - Danh sách thay đổi
- **test_levenshtein_regex.py** - Test examples

---

## 🤝 Đóng Góp

**Nhóm phát triển:** Nhóm 4 - Trường Đại học Gia Định  
**GVHD:** Lý Quang Vinh  
**Môn học:** Lập trình Python

---

## 📄 License

VNS-NORM v1.1 - Trợ lý Chuẩn hóa Tiếng Việt  
© 2025 - Nhóm 4 - Trường Đại học Gia Định

---

## ✅ Checklist Cập Nhật

- ✅ Thêm Levenshtein Distance
- ✅ Thêm Find Similar Words
- ✅ Thêm Detect Elongated Words
- ✅ Thêm Detailed Analysis
- ✅ Cải thiện Expand Abbreviations
- ✅ Cập nhật Get Statistics
- ✅ Tạo Test Suite
- ✅ Viết Documentation
- ✅ Backward Compatible
- ✅ All Tests Passing ✨

---

## 📞 Support

**Câu hỏi hoặc báo cáo lỗi?**

```
Tôi có thể giúp bạn với:
✅ Cách sử dụng API
✅ Điều chỉnh tham số
✅ Mở rộng từ điển
✅ Tích hợp vào project
✅ Performance tuning
```

---

**Cảm ơn đã sử dụng VNS-NORM! 🚀**

Phiên bản v1.1 đánh dấu một bước tiến đáng kể về khả năng  
chuẩn hóa và phân tích văn bản Tiếng Việt. Happy normalizing! 💬

