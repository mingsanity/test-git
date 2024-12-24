import os
from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as genai
from PIL import Image  # Để hiển thị hình ảnh

# Cấu hình API key từ file config.py
from config import API_KEY

# Cấu hình API Google Generative AI
genai.configure(api_key=API_KEY)

# Tạo ứng dụng Flask
app = Flask(__name__)

# Tạo thư mục để lưu trữ hình ảnh
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Đường dẫn file HTML cố định
BLOG_FILE = 'blog.html'

# Trang chủ: Hiển thị form để tải lên tệp hình ảnh
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 1️⃣ Lấy tệp ảnh người dùng tải lên
        if 'image' not in request.files:
            return 'Không tìm thấy tệp hình ảnh nào.'

        image = request.files['image']
        
        if image.filename == '':
            return 'Không có tệp nào được chọn.'

        # 2️⃣ Lưu tệp hình ảnh vào thư mục static
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)

        # 3️⃣ Gửi yêu cầu đến API để tạo nội dung
        prompt = "Write a short, engaging blog post based on this picture. It should include a description of the meal in the photo and talk about my journey meal prepping."
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Sử dụng API để tạo nội dung
        image = Image.open(image_path)  # Mở hình ảnh bằng PIL
        response = model.generate_content([prompt, image], stream=True)
        response.resolve()  # Đợi cho nội dung hoàn tất
        blog_content = response.text  # Lấy nội dung bài viết

        # 4️⃣ Thay thế ảnh và nội dung vào file HTML
        with open(BLOG_FILE, 'w', encoding='utf-8') as file:
            file.write(f"""
            <!DOCTYPE html>
            <html lang="vi">
            <head>
                <meta charset="UTF-8">
                <title>Bài Blog Tự Động</title>
            </head>
            <body>
                <h1>Bài Blog Tự Động</h1>
                <img src="static/{image.filename}" alt="Hình ảnh của bạn" width="400px"><br><br>
                <h2>Nội dung bài viết</h2>
                <p>{blog_content}</p>
                <a href="/">Quay lại trang chủ</a>
            </body>
            </html>
            """)

        return redirect(url_for('view_blog'))

    return render_template('index.html')

# Trang để hiển thị bài blog
@app.route('/view-blog')
def view_blog():
    with open(BLOG_FILE, 'r', encoding='utf-8') as file:
        blog_content = file.read()
    return blog_content

# Khởi chạy ứng dụng Flask
if __name__ == '__main__':
    app.run(debug=True)
