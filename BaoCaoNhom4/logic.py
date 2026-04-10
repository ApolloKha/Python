import re

# Từ điển viết tắt mẫu (Trong thực tế nên dùng file JSON lớn)
ABBREVIATIONS = {
    "ko": "không", "k": "không", "kh": "không",
    "dc": "được", "đc": "được",
    "bít": "biết", "wa": "quá", "j": "gì",
    "hj": "hiện", "nk": "nếu", "ntn": "như thế nào"
}

def clean_elongated(text):
    """Xử lý từ lặp: vuiiiii -> vui"""
    return re.sub(r'([\wÀ-ỹ])\1{2,}', r'\1', text, flags=re.UNICODE)


def remove_duplicate_words(text):
    """Xóa từ lặp liền kề: đi đi đi -> đi"""
    words = text.split()
    result = []
    for w in words:
        if not result or w != result[-1]:
            result.append(w)
    return " ".join(result)


def replace_abbreviations(text):
    """Thay thế từ viết tắt dựa trên từ điển (từ nguyên vẹn, không đụng vào chuỗi con)."""
    if not ABBREVIATIONS:
        return text

    pattern = r"\b(" + "|".join(re.escape(k) for k in ABBREVIATIONS.keys()) + r")\b"

    def _reh(match):
        key = match.group(0).lower()
        return ABBREVIATIONS.get(key, match.group(0))

    return re.sub(pattern, _reh, text, flags=re.IGNORECASE)


def normalize_pipeline(text):
    """Hệ thống Pipeline chạy tuần tự"""
    if not text:
        return ""

    text = text.lower().strip()
    text = clean_elongated(text)
    text = remove_duplicate_words(text)
    text = replace_abbreviations(text)
    # Lưu ý: Thêm dấu câu/đổi sang văn phong chuẩn cần mô hình AI nặng.
    return text.capitalize()
