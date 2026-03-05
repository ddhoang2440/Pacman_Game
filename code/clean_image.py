import os
from PIL import Image

def strip_icc_profile(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.png'):
                path = os.path.join(root, file)
                try:
                    img = Image.open(path)
                    # Xóa dữ liệu ICC profile bằng cách lưu lại mà không kèm theo nó
                    img.save(path, icc_profile=None)
                    print(f"Fixed: {path}")
                except Exception as e:
                    print(f"Error fixing {path}: {e}")

# Chạy cho thư mục images của bạn
strip_icc_profile('../images')