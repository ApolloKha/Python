# =============================================================================
# VNS-NORM: Trợ lý Chuẩn hóa Tiếng Việt
# Dựa trên nghiên cứu của Nhóm 4 - Trường Đại học Gia Định
# Môn: Lập trình Python | GVHD: Lý Quang Vinh
# =============================================================================
# Cấu trúc code:
#   - Phần 1: VNSNorm (Core Logic) - Toàn bộ xử lý chuỗi
#   - Phần 2: VNSNormApp (GUI)     - Giao diện người dùng
# =============================================================================

import re
import json
import os
import customtkinter as ctk
from tkinter import messagebox
from difflib import SequenceMatcher


# =============================================================================
# PHẦN 1: CORE LOGIC - Lớp xử lý văn bản VNS-NORM
# =============================================================================

class VNSNorm:
    """
    Lớp chính của hệ thống VNS-NORM (Vietnamese Text Normalization System).

    Chứa toàn bộ các phương thức xử lý và chuẩn hóa văn bản tiếng Việt.
    Luồng xử lý theo đúng thứ tự:
        1. Xóa ký tự lặp (De-elongation)
        2. Chuẩn hóa khoảng trắng
        3. Chuẩn hóa viết tắt (Abbreviation Expansion)
    """

    # -------------------------------------------------------------------------
    # Từ điển viết tắt phổ biến (50+ mục mẫu - có thể mở rộng lên 1000)
    # Key: dạng viết tắt | Value: dạng chuẩn
    # -------------------------------------------------------------------------
    DEFAULT_ABBREVIATIONS = {
       
    }

    def __init__(self, dict_path: str = None):
        """
        Khởi tạo đối tượng VNSNorm.

        Args:
            dict_path (str, optional): Đường dẫn tới file JSON chứa từ điển viết tắt.
                                       Nếu không cung cấp, dùng từ điển mặc định có sẵn.
        """
        # Nạp từ điển: ưu tiên file JSON ngoài, fallback về từ điển mặc định
        self.abbreviation_dict = self._load_dictionary(dict_path)

        # Biên dịch sẵn Regex pattern để tăng hiệu suất khi gọi nhiều lần
        # Pattern phát hiện ký tự lặp liên tiếp >= 3 lần (ví dụ: "vui quáaaa")
        self._elongation_pattern = re.compile(r'([a-zàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵýỷỹ])\1{2,}', re.IGNORECASE | re.UNICODE)

        # Pattern phát hiện các khoảng trắng liên tiếp (nhiều space/tab/newline)
        self._whitespace_pattern = re.compile(r'[ \t]+')

        # Pattern phát hiện các dòng trống liên tiếp
        self._multiline_pattern = re.compile(r'\n{3,}')

        # ===== PATTERN PHÁT HIỆN TỪ KÉO DÀI (REGEX MỚI) =====
        # Phát hiện ký tự lặp 2 lần trở lên để xử lý linh hoạt hơn
        self._repeated_chars_pattern = re.compile(r'([a-zàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵýỷỹ])\1{1,}', re.IGNORECASE | re.UNICODE)
        
        # Phát hiện toàn bộ từ có ký tự lặp trong nó (tìm từ lặp, không chỉ ký tự)
        # Ví dụ: "hiiiii", "yeeesss", "okkkkay"
        self._word_with_repetition_pattern = re.compile(r'\b\w*([a-zàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵýỷỹ])\1+\w*\b', re.IGNORECASE | re.UNICODE)

    def _load_dictionary(self, dict_path: str) -> dict:
        """
        Nạp từ điển viết tắt từ file JSON hoặc dùng từ điển mặc định.

        Args:
            dict_path (str): Đường dẫn file JSON. None = dùng mặc định.

        Returns:
            dict: Từ điển ánh xạ viết tắt -> từ đầy đủ.
        """
        if dict_path and os.path.exists(dict_path):
            try:
                with open(dict_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                merged_dict = {}
                # Gộp tất cả category lại thành 1 dict phẳng
                if "teencode" in data:
                    merged_dict.update(data["teencode"])

                # Gộp với default (ưu tiên JSON)
                final_dict = {**self.DEFAULT_ABBREVIATIONS, **merged_dict}
                return final_dict

            except Exception as e:
                print(f"Lỗi nạp từ điển: {e}")
                return dict(self.DEFAULT_ABBREVIATIONS)
        
        return dict(self.DEFAULT_ABBREVIATIONS)


    # =========================================================================
    # CÁC PHƯƠNG THỨC XỬ LÝ ĐƠN LẺ
    # =========================================================================

    def levenshtein_distance(self, word1: str, word2: str) -> int:
        """
        Tính khoảng cách Levenshtein giữa hai từ.
        
        Levenshtein Distance là số lượng phép chỉnh sửa tối thiểu (thêm, xóa, thay thế)
        cần thiết để biến một từ thành từ khác.
        
        Ví dụ:
            "ko" -> "không":   3 phép chỉnh sửa (thêm "h", "n", "g")
            "biet" -> "biết":  1 phép chỉnh sửa (thay "t" -> "t + dấu")
            "hoa" -> "hoi":    1 phép chỉnh sửa (thay "a" -> "i")
        
        Args:
            word1 (str): Từ thứ nhất.
            word2 (str): Từ thứ hai.
            
        Returns:
            int: Khoảng cách Levenshtein (số phép chỉnh sửa).
        """
        m, n = len(word1), len(word2)
        
        # Tạo bảng DP (Dynamic Programming) kích thước (m+1) x (n+1)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Khởi tạo hàng đầu và cột đầu
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Tính toán các ô trong bảng
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    # Ký tự giống nhau - không cần chỉnh sửa
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # Ký tự khác - lấy phép chỉnh sửa tối thiểu
                    # min(thay, xóa, thêm) + 1
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # Xóa ký tự từ word1
                        dp[i][j - 1],      # Thêm ký tự vào word1
                        dp[i - 1][j - 1]   # Thay thế ký tự
                    )
        
        return dp[m][n]

    def find_similar_word(self, word: str, max_distance: int = 2) -> str:
        """
        Tìm từ gần giống nhất trong từ điển dựa trên Levenshtein Distance.
        
        Dùng để nhận diện các từ viết sai, viết tắt không được nhận diện,
        hoặc từ kéo dài không bị bắt bởi regex.
        
        Ví dụ:
            "ko" -> "không"  (distance = 2, tìm được)
            "biet" -> "biết" (distance = 1, tìm được)
            "xyz" -> "xyz"   (không tìm được, giữ nguyên)
        
        Args:
            word (str): Từ cần tìm kiếm.
            max_distance (int): Khoảng cách tối đa cho phép (mặc định 2).
            
        Returns:
            str: Từ gần giống nhất, hoặc từ gốc nếu không tìm được.
        """
        word_lower = word.lower()
        
        # Nếu từ đã có trong từ điển - không cần tìm kiếm
        if word_lower in self.abbreviation_dict:
            return self.abbreviation_dict[word_lower]
        
        best_match = None
        best_distance = max_distance + 1
        
        # Duyệt qua toàn bộ từ điển để tìm từ gần giống nhất
        for dict_word in self.abbreviation_dict.keys():
            # Bỏ qua những từ có chiều dài quá khác biệt (tối ưu hóa)
            if abs(len(word_lower) - len(dict_word)) > max_distance:
                continue
            
            distance = self.levenshtein_distance(word_lower, dict_word)
            
            # Nếu tìm được từ gần giống với distance <= max_distance
            if distance <= max_distance and distance < best_distance:
                best_distance = distance
                best_match = dict_word
        
        # Nếu tìm được - trả về từ chuẩn hóa, nếu không - giữ nguyên từ gốc
        if best_match is not None:
            return self.abbreviation_dict[best_match]
        return word

    def detect_elongated_words(self, text: str) -> list:
        """
        Phát hiện toàn bộ các từ kéo dài trong văn bản.
        
        Trả về danh sách các từ có ký tự lặp liên tiếp để cho phép
        theo dõi và phân tích những từ "vui quáaaa", "hiiiiii" v.v.
        
        Ví dụ:
            "vui quáaaa hiiiiii bạn" -> ["quáaaa", "hiiiiii"]
        
        Args:
            text (str): Văn bản đầu vào.
            
        Returns:
            list: Danh sách các từ kéo dài được phát hiện.
        """
        elongated_words = []
        
        # Tìm tất cả match của pattern từ có ký tự lặp
        matches = self._word_with_repetition_pattern.finditer(text)
        
        for match in matches:
            word = match.group()
            if word not in elongated_words:  # Tránh trùng lặp
                elongated_words.append(word)
        
        return elongated_words

    def get_repeated_char_info(self, word: str) -> dict:
        """
        Lấy thông tin chi tiết về ký tự lặp trong một từ.
        
        Trả về từ điển chứa:
            - ký tự lặp
            - số lần lặp
            - vị trí của ký tự lặp
        
        Ví dụ:
            "quáaaa" -> {
                'char': 'a',
                'count': 3,
                'position': 3
            }
        
        Args:
            word (str): Từ cần phân tích.
            
        Returns:
            dict: Thông tin về ký tự lặp, hoặc {} nếu không tìm thấy.
        """
        match = self._repeated_chars_pattern.search(word)
        
        if match:
            repeated_char = match.group(1)
            # Đếm số lần ký tự lặp liên tiếp
            count = len(match.group()) - 1
            position = match.start()
            
            return {
                'char': repeated_char,
                'count': count,
                'position': position,
                'matched': match.group()
            }
        
        return {}

    def remove_elongation(self, text: str) -> str:
        """
        Xóa ký tự lặp (De-elongation Module).

        Phát hiện và rút gọn các ký tự lặp liên tiếp >= 3 lần về còn 1 ký tự.
        Pattern: r'([a-z])\1{2,}' - bắt nhóm ký tự lặp từ 3 lần trở lên.

        Ví dụ:
            "vui quáaaa"    -> "vui quá"
            "đẹppppppp"     -> "đẹp"
            "hiiiiiii bạn"  -> "hi bạn"
            "yeeeees"       -> "yes"

        Args:
            text (str): Văn bản đầu vào.

        Returns:
            str: Văn bản sau khi loại bỏ ký tự lặp.
        """
        # \1 là back-reference đến nhóm đầu tiên (ký tự bị lặp)
        # {2,} nghĩa là ký tự đó lặp thêm ít nhất 2 lần nữa (tổng >= 3)
        return self._elongation_pattern.sub(r'\1', text)

    def normalize_whitespace(self, text: str) -> str:
        """
        Chuẩn hóa khoảng trắng (Whitespace Normalization).

        Loại bỏ các khoảng trắng thừa, tab liên tiếp, và thu gọn
        các dòng trống liên tiếp thành tối đa 1 dòng trống.

        Ví dụ:
            "xin   chào   bạn"  -> "xin chào bạn"
            "  hello  world  "  -> "hello world"

        Args:
            text (str): Văn bản đầu vào.

        Returns:
            str: Văn bản sau khi chuẩn hóa khoảng trắng.
        """
        # Thay mọi chuỗi space/tab liên tiếp bằng 1 dấu cách
        text = self._whitespace_pattern.sub(' ', text)

        # Thu gọn nhiều dòng trống liên tiếp thành tối đa 2 dòng mới
        text = self._multiline_pattern.sub('\n\n', text)

        # Xóa khoảng trắng thừa ở đầu và cuối mỗi dòng
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)

    def expand_abbreviations(self, text: str) -> str:
        """
        Chuẩn hóa viết tắt (Abbreviation Expansion Module).

        Duyệt qua từng từ trong văn bản và tra cứu trong Hash Map (từ điển).
        Chiến lược: Chỉ chuẩn hóa từ nếu nó có trong từ điển (exact match).
        Nếu từ không có trong từ điển -> giữ nguyên (không cần sửa từ đúng).
        
        Không phân biệt hoa/thường khi tra cứu, nhưng giữ nguyên cấu trúc dòng.

        Ví dụ:
            "ko"        -> "không"         (có trong từ điển)
            "đc"        -> "được"          (có trong từ điển)
            "xin chào"  -> "xin chào"      (không trong từ điển -> giữ nguyên)

        Args:
            text (str): Văn bản đầu vào.

        Returns:
            str: Văn bản sau khi mở rộng các viết tắt.
        """
        # Tách văn bản thành từng dòng để xử lý riêng biệt
        result_lines = []
        for line in text.split('\n'):
            # Tách từng từ ra (split theo khoảng trắng)
            words = line.split(' ')
            expanded_words = []
            for word in words:
                if not word:
                    # Giữ lại khoảng trống nếu có (tránh mất cấu trúc)
                    expanded_words.append(word)
                    continue

                # Tách phần dấu câu ở cuối từ để tra cứu chính xác hơn
                # Ví dụ: "ko," -> tra "ko" rồi thêm lại ","
                suffix = ''
                clean_word = word
                while clean_word and clean_word[-1] in '.,!?;:)("\'…':
                    suffix = clean_word[-1] + suffix
                    clean_word = clean_word[:-1]

                prefix = ''
                while clean_word and clean_word[0] in '.,!?;:)("\'…':
                    prefix += clean_word[0]
                    clean_word = clean_word[1:]

                # Tra cứu không phân biệt hoa/thường
                lookup_key = clean_word.lower()
                
                # ===== CHỈ DÙNG CHIẾN LƯỢC 1: Tra cứu trực tiếp (Exact Match) =====
                # Nếu từ chính xác có trong từ điển -> chuẩn hóa
                # Nếu từ không trong từ điển -> giữ nguyên (không cần sửa từ đúng)
                if lookup_key in self.abbreviation_dict:
                    expanded = self.abbreviation_dict[lookup_key]
                    expanded_words.append(prefix + expanded + suffix)
                else:
                    # Từ không trong từ điển -> không sửa
                    expanded_words.append(word)

            result_lines.append(' '.join(expanded_words))

        return '\n'.join(result_lines)

    # =========================================================================
    # PHƯƠNG THỨC CHUẨN HÓA CHÍNH - Kết hợp tất cả bước theo đúng thứ tự
    # =========================================================================

    def normalize(self, text: str) -> str:
        """
        Hàm chuẩn hóa chính - Pipeline xử lý theo đúng thứ tự VNS-NORM.

        Thứ tự xử lý (quan trọng - không được đảo ngược):
            Bước 1: Xóa ký tự lặp (De-elongation)
                    -> Giải quyết "vui quáaaa" TRƯỚC khi chuẩn hóa
            Bước 2: Chuẩn hóa khoảng trắng
                    -> Dọn sạch khoảng trắng sau khi xóa lặp
            Bước 3: Chuẩn hóa viết tắt
                    -> Mở rộng viết tắt cuối cùng để tra từ điển chính xác

        Args:
            text (str): Văn bản thô đầu vào.

        Returns:
            str: Văn bản đã được chuẩn hóa hoàn toàn.
        """
        if not text or not text.strip():
            return ""

        # Bước 1: Xóa ký tự lặp (De-elongation)
        # Lý do đặt đầu: "kooo" cần thành "ko" trước, rồi mới tra từ điển thành "không"
        result = self.remove_elongation(text)

        # Bước 2: Chuẩn hóa khoảng trắng
        result = self.normalize_whitespace(result)

        # Bước 3: Chuẩn hóa viết tắt (cuối cùng để tra từ điển chính xác)
        result = self.expand_abbreviations(result)

        return result

    def get_statistics(self, original: str, normalized: str) -> dict:
        """
        Tính thống kê so sánh giữa văn bản gốc và đã chuẩn hóa.
        
        Bổ sung thông tin về các từ kéo dài được phát hiện.

        Args:
            original (str): Văn bản gốc.
            normalized (str): Văn bản sau chuẩn hóa.

        Returns:
            dict: Từ điển chứa các thống kê và thông tin chi tiết.
        """
        orig_words = len(original.split())
        norm_words = len(normalized.split())
        orig_chars = len(original)
        norm_chars = len(normalized)
        
        # Phát hiện các từ kéo dài trong văn bản gốc
        elongated_words = self.detect_elongated_words(original)

        return {
            "orig_chars":        orig_chars,
            "norm_chars":        norm_chars,
            "orig_words":        orig_words,
            "norm_words":        norm_words,
            "char_change":       orig_chars - norm_chars,
            "elongated_found":   len(elongated_words),
            "elongated_words":   elongated_words,
        }

    def get_detailed_analysis(self, text: str) -> dict:
        """
        Tạo báo cáo chi tiết về phân tích văn bản.
        
        Gồm:
            - Danh sách từ kéo dài + thông tin ký tự lặp
            - Thông tin các từ có thể được mở rộng
            - Thống kê tổng quát
        
        Args:
            text (str): Văn bản đầu vào.
            
        Returns:
            dict: Báo cáo chi tiết phân tích.
        """
        analysis = {
            "total_words": len(text.split()),
            "total_chars": len(text),
            "elongated_words": [],
            "potentially_abbreviations": [],
        }
        
        # Phân tích từ kéo dài
        elongated = self.detect_elongated_words(text)
        for word in elongated:
            info = self.get_repeated_char_info(word)
            if info:
                analysis["elongated_words"].append({
                    "word": word,
                    "repeated_char": info.get('char'),
                    "repeat_count": info.get('count'),
                    "position": info.get('position')
                })
        
        # Tìm từ có khả năng là viết tắt / từ không chuẩn
        words = text.lower().split()
        for word in words:
            # Loại bỏ dấu câu
            clean_word = ''.join(c for c in word if c.isalnum())
            
            # Nếu từ ngắn và có trong từ điển hoặc gần giống từ trong từ điển
            if 1 < len(clean_word) <= 4:
                if clean_word in self.abbreviation_dict:
                    analysis["potentially_abbreviations"].append({
                        "word": clean_word,
                        "expanded": self.abbreviation_dict[clean_word],
                        "type": "exact_match"
                    })
                else:
                    similar = self.find_similar_word(clean_word, max_distance=1)
                    if similar != clean_word:
                        analysis["potentially_abbreviations"].append({
                            "word": clean_word,
                            "expanded": similar,
                            "type": "levenshtein_match"
                        })
        
        return analysis


# =============================================================================
# PHẦN 2: GUI - Lớp giao diện người dùng VNSNormApp
# =============================================================================

class VNSNormApp(ctk.CTk):
    """
    Lớp giao diện ứng dụng Desktop "VNS-NORM: Trợ lý Chuẩn hóa Tiếng Việt".

    Kế thừa từ customtkinter.CTk để tận dụng các widget hiện đại.
    Tách biệt hoàn toàn với phần Logic xử lý (VNSNorm).
    """

    # -------------------------------------------------------------------------
    # Hằng số cấu hình giao diện
    # -------------------------------------------------------------------------
    APP_TITLE       = "VNS-NORM — Trợ lý Chuẩn hóa Tiếng Việt"
    WINDOW_SIZE     = "1100x700"
    WINDOW_MIN_W    = 800
    WINDOW_MIN_H    = 550

    # Màu sắc chủ đề (Ocean Dark)
    COLOR_PRIMARY   = "#2B7FDD"   # Xanh dương nổi bật - nút chính
    COLOR_DANGER    = "#E05252"   # Đỏ cam - nút xóa
    COLOR_SUCCESS   = "#27AE60"   # Xanh lá - nút copy
    COLOR_BG_DARK   = "#1A1A2E"   # Nền tối chính
    COLOR_CARD      = "#16213E"   # Nền card
    COLOR_TEXT_BOX  = "#0F3460"   # Nền textbox
    COLOR_LABEL     = "#A8C0DD"   # Màu chữ label phụ

    def __init__(self, norm_engine: VNSNorm):
        """
        Khởi tạo cửa sổ ứng dụng.

        Args:
            norm_engine (VNSNorm): Đối tượng xử lý văn bản đã khởi tạo sẵn.
        """
        super().__init__()

        # Lưu tham chiếu tới engine xử lý
        self.norm_engine = norm_engine

        # ---- Cấu hình cửa sổ ----
        self.title(self.APP_TITLE)
        self.geometry(self.WINDOW_SIZE)
        self.minsize(self.WINDOW_MIN_W, self.WINDOW_MIN_H)

        # Đặt chủ đề tối (Dark) với bảng màu xanh dương
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Màu nền cửa sổ chính
        self.configure(fg_color=self.COLOR_BG_DARK)

        # ---- Dựng giao diện ----
        self._build_ui()

    # =========================================================================
    # CÁC PHƯƠNG THỨC XÂY DỰNG GIAO DIỆN
    # =========================================================================

    def _build_ui(self):
        """
        Phương thức tổng hợp - gọi các hàm con để xây dựng từng phần giao diện.
        Đảm bảo thứ tự: Header -> Nội dung chính -> Footer.
        """
        # Cấu hình grid của cửa sổ chính để responsive
        self.grid_rowconfigure(0, weight=0)   # Header - cố định
        self.grid_rowconfigure(1, weight=1)   # Nội dung - co giãn
        self.grid_rowconfigure(2, weight=0)   # Nút bấm - cố định
        self.grid_rowconfigure(3, weight=0)   # Footer - cố định
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_main_content()
        self._build_buttons()
        self._build_footer()

    def _build_header(self):
        """
        Xây dựng phần tiêu đề ứng dụng (Header).
        Gồm: Logo/Icon chữ, tên ứng dụng, và tagline mô tả.
        """
        header_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_CARD,
            corner_radius=0
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)

        # Dòng tiêu đề chính với icon
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡  VNS-NORM — Chuẩn Hóa Văn Bản Tiếng Việt",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.grid(row=0, column=0, padx=30, pady=(18, 4), sticky="w")

        # Tagline / mô tả ngắn
        tagline_label = ctk.CTkLabel(
            header_frame,
            text="Vietnamese Text Normalization System  ·  Nhóm 4 - ĐH Gia Định  ·  GVHD: Lý Quang Vinh",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=self.COLOR_LABEL
        )
        tagline_label.grid(row=1, column=0, padx=30, pady=(0, 14), sticky="w")

    def _build_main_content(self):
        """
        Xây dựng phần nội dung chính: hai ô nhập/xuất văn bản nằm cạnh nhau.
        Sử dụng grid để đảm bảo responsive khi thay đổi kích thước cửa sổ.
        """
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=10)

        # Hai cột bằng nhau, co giãn theo chiều ngang
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=0)  # cột divider
        content_frame.grid_columnconfigure(2, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # ---------- CỘT TRÁI: Văn bản thô ----------
        left_label = ctk.CTkLabel(
            content_frame,
            text="📝   Văn bản thô (Nhập vào)",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color=self.COLOR_LABEL
        )
        left_label.grid(row=0, column=0, sticky="w", padx=(4, 0), pady=(4, 6))

        self.input_textbox = ctk.CTkTextbox(
            content_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=self.COLOR_TEXT_BOX,
            text_color="#E8F4FD",
            border_color="#2B4F7A",
            border_width=1,
            corner_radius=10,
            wrap="word",
            scrollbar_button_color="#2B7FDD",
            scrollbar_button_hover_color="#1A6ABF"
        )
        self.input_textbox.grid(row=1, column=0, sticky="nsew", padx=(4, 8))

        # Placeholder text
        self._set_placeholder(self.input_textbox,
            "Nhập văn bản tiếng Việt cần chuẩn hóa vào đây...\n\n"
            "Ví dụ:\n"
            "  ko đc nha mn ơi, tui hok bít lm vc này đâu\n"
            "  vui quáaaa, tuyệt vờiiiiii vs ae\n"
            "  xin   chào    bạn   ơi!!!"
        )

        # ---------- DIVIDER giữa ----------
        divider = ctk.CTkFrame(
            content_frame,
            width=2,
            fg_color="#2B4F7A",
            corner_radius=2
        )
        divider.grid(row=0, column=1, rowspan=2, sticky="ns", padx=4, pady=4)

        # ---------- CỘT PHẢI: Văn bản đã chuẩn hóa ----------
        right_label = ctk.CTkLabel(
            content_frame,
            text="✅   Văn bản đã chuẩn hóa (Kết quả)",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color="#5BBFAD"
        )
        right_label.grid(row=0, column=2, sticky="w", padx=(8, 4), pady=(4, 6))

        self.output_textbox = ctk.CTkTextbox(
            content_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#0A2A1E",            # Nền xanh lá tối
            text_color="#A8FFDA",          # Chữ xanh mint sáng
            border_color="#1E5440",
            border_width=1,
            corner_radius=10,
            wrap="word",
            state="disabled",             # Chỉ đọc - người dùng không sửa được
            scrollbar_button_color="#27AE60",
            scrollbar_button_hover_color="#1E8449"
        )
        self.output_textbox.grid(row=1, column=2, sticky="nsew", padx=(8, 4))

    def _build_buttons(self):
        """
        Xây dựng cụm nút bấm điều khiển ở giữa, bên dưới hai ô văn bản.
        Gồm 3 nút: Chuẩn hóa | Xóa nội dung | Copy kết quả.
        """
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=14)

        # Nút "Chuẩn hóa" - màu xanh nổi bật, là hành động chính
        self.btn_normalize = ctk.CTkButton(
            btn_frame,
            text="⚡  Chuẩn hóa",
            command=self._on_normalize,
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            fg_color=self.COLOR_PRIMARY,
            hover_color="#1A6ABF",
            text_color="#FFFFFF",
            corner_radius=8,
            height=42,
            width=160
        )
        self.btn_normalize.grid(row=0, column=0, padx=10)

        # Nút "Xóa nội dung" - màu đỏ cảnh báo
        self.btn_clear = ctk.CTkButton(
            btn_frame,
            text="🗑  Xóa nội dung",
            command=self._on_clear,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.COLOR_DANGER,
            hover_color="#C0392B",
            text_color="#FFFFFF",
            corner_radius=8,
            height=42,
            width=155
        )
        self.btn_clear.grid(row=0, column=1, padx=10)

        # Nút "Copy kết quả" - màu xanh lá thành công
        self.btn_copy = ctk.CTkButton(
            btn_frame,
            text="📋  Copy kết quả",
            command=self._on_copy,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.COLOR_SUCCESS,
            hover_color="#1E8449",
            text_color="#FFFFFF",
            corner_radius=8,
            height=42,
            width=155
        )
        self.btn_copy.grid(row=0, column=2, padx=10)

    def _build_footer(self):
        """
        Xây dựng thanh trạng thái (Status Bar) ở phía dưới cùng.
        Hiển thị thông tin xử lý và thống kê sau mỗi lần chuẩn hóa.
        """
        footer_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_CARD,
            corner_radius=0,
            height=34
        )
        footer_frame.grid(row=3, column=0, sticky="ew")
        footer_frame.grid_propagate(False)
        footer_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="💡  Nhập văn bản vào ô bên trái, sau đó nhấn nút \"Chuẩn hóa\" để bắt đầu.",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=self.COLOR_LABEL,
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=16, pady=6, sticky="w")

        # Label phiên bản bên phải
        ver_label = ctk.CTkLabel(
            footer_frame,
            text="VNS-NORM v1.0  |  Nhóm 4",
            font=ctk.CTkFont(family="Arial", size=10),
            text_color="#4A6A8A"
        )
        ver_label.grid(row=0, column=1, padx=16, pady=6, sticky="e")

    # =========================================================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN (Event Handlers)
    # =========================================================================

    def _on_normalize(self):
        """
        Xử lý sự kiện nhấn nút "Chuẩn hóa".

        Lấy nội dung từ ô nhập, gọi VNSNorm.normalize(), rồi hiển thị
        kết quả vào ô xuất và cập nhật thanh trạng thái.
        """
        # Lấy toàn bộ văn bản từ ô nhập
        raw_text = self.input_textbox.get("1.0", "end-1c")

        # Kiểm tra nếu rỗng
        if not raw_text.strip():
            self._update_status("⚠️  Vui lòng nhập văn bản trước khi chuẩn hóa.", color="#E0A050")
            return

        # Gọi engine xử lý chính
        normalized_text = self.norm_engine.normalize(raw_text)

        # Hiển thị kết quả vào ô xuất (phải mở khóa trước, khóa lại sau)
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", normalized_text)
        self.output_textbox.configure(state="disabled")

        # Tính và hiển thị thống kê
        stats = self.norm_engine.get_statistics(raw_text, normalized_text)
        status_msg = (
            f"✅  Chuẩn hóa thành công!  |  "
            f"Ký tự: {stats['orig_chars']} → {stats['norm_chars']}  |  "
            f"Từ: {stats['orig_words']} → {stats['norm_words']}  |  "
            f"Giảm {stats['char_change']} ký tự"
        )
        self._update_status(status_msg, color="#5BBFAD")

    def _on_clear(self):
        """
        Xử lý sự kiện nhấn nút "Xóa nội dung".
        Xóa cả hai ô văn bản và reset thanh trạng thái.
        """
        self.input_textbox.delete("1.0", "end")

        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")

        self._update_status("🗑  Đã xóa toàn bộ nội dung.", color=self.COLOR_LABEL)

    def _on_copy(self):
        """
        Xử lý sự kiện nhấn nút "Copy kết quả".
        Sao chép nội dung ô kết quả vào clipboard hệ thống.
        """
        # Lấy nội dung từ ô xuất
        self.output_textbox.configure(state="normal")
        result_text = self.output_textbox.get("1.0", "end-1c")
        self.output_textbox.configure(state="disabled")

        if not result_text.strip():
            self._update_status("⚠️  Chưa có kết quả để copy. Hãy chuẩn hóa trước!", color="#E0A050")
            return

        # Ghi vào clipboard
        self.clipboard_clear()
        self.clipboard_append(result_text)
        self.update()  # Cập nhật clipboard ngay lập tức

        self._update_status(f"📋  Đã copy {len(result_text)} ký tự vào clipboard!", color="#A8FFDA")

    # =========================================================================
    # CÁC HÀM TIỆN ÍCH (Helper Methods)
    # =========================================================================

    def _update_status(self, message: str, color: str = None):
        """
        Cập nhật nội dung thanh trạng thái ở chân trang.

        Args:
            message (str): Nội dung hiển thị.
            color (str, optional): Màu chữ (hex string). Mặc định dùng màu label.
        """
        self.status_label.configure(
            text=message,
            text_color=color if color else self.COLOR_LABEL
        )

    def _set_placeholder(self, textbox: ctk.CTkTextbox, placeholder: str):
        """
        Đặt placeholder text vào textbox với màu xám nhạt.

        Args:
            textbox (CTkTextbox): Widget cần đặt placeholder.
            placeholder (str): Nội dung placeholder.
        """
        textbox.insert("1.0", placeholder)
        textbox.configure(text_color="#4A6A8A")  # Màu xám nhạt cho placeholder

        def on_focus_in(event):
            """Xóa placeholder khi người dùng click vào."""
            if textbox.get("1.0", "end-1c") == placeholder:
                textbox.delete("1.0", "end")
                textbox.configure(text_color="#E8F4FD")  # Màu chữ bình thường

        def on_focus_out(event):
            """Khôi phục placeholder nếu ô trống."""
            if not textbox.get("1.0", "end-1c").strip():
                textbox.insert("1.0", placeholder)
                textbox.configure(text_color="#4A6A8A")

        textbox.bind("<FocusIn>", on_focus_in)
        textbox.bind("<FocusOut>", on_focus_out)


# =============================================================================
# ĐIỂM KHỞI CHẠY CHƯƠNG TRÌNH (Entry Point)
# =============================================================================

def main():
    """
    Hàm main - Điểm khởi chạy duy nhất của ứng dụng.

    Thứ tự khởi tạo:
        1. Tạo VNSNorm engine (Core Logic)
        2. Tạo VNSNormApp GUI và truyền engine vào
        3. Chạy vòng lặp sự kiện (event loop)
    """
    # Bước 1: Khởi tạo engine chuẩn hóa
    # Tải từ điển từ file JSON
    dict_path = os.path.join(os.path.dirname(__file__), "dictionary.json")
    norm_engine = VNSNorm(dict_path=dict_path)

    # Bước 2: Khởi tạo và chạy giao diện
    app = VNSNormApp(norm_engine=norm_engine)
    app.mainloop()


if __name__ == "__main__":
    main()