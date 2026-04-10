import streamlit as st
from logic import normalize_pipeline

# Cấu hình trang
st.set_page_config(page_title="VN-Text Normalizer", page_icon="📝")

st.title("🚀 Vietnamese Text Normalization Tool")
st.subheader("Công cụ Chuẩn hóa & Sửa lỗi Chính tả Tiếng Việt")

# Vùng nhập liệu
input_text = st.text_area("Nhập văn bản thô (viết tắt, lặp từ, không dấu...):", 
                          placeholder="vd: hnay tui vuiiiii wa di học ko mệt...")

if st.button("Xử lý ngay"):
    if input_text:
        with st.spinner('Đang phân tích và chuẩn hóa...'):
            result = normalize_pipeline(input_text)
            
            # Hiển thị kết quả
            st.success("Kết quả chuẩn hóa:")
            st.info(result)
            
            # So sánh
            col1, col2 = st.columns(2)
            col1.metric("Độ dài gốc", len(input_text))
            col2.metric("Độ dài sau xử lý", len(result))
    else:
        st.warning("Vui lòng nhập văn bản!")

st.sidebar.markdown("""
### Hướng dẫn sử dụng:
1. Nhập văn bản cần xử lý.
2. Nhấn nút **Xử lý ngay**.
3. Hệ thống sẽ tự động lọc từ lặp và giải mã viết tắt.
""")