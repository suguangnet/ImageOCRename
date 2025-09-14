import hashlib
import tkinter as tk
from tkinter import scrolledtext  # 导入滚动文本模块
from tkinter import messagebox, ttk
import psutil
import os
from PPOCR_api import GetOcrApi
import sys
import configparser

# 获取.exe文件的目录
if getattr(sys, 'frozen', False):
    # 如果程序被"冷冻"（即被PyInstaller打包）
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# 使用这个路径来确定pic目录的位置
pic_directory = os.path.join(application_path, "pic")

# 初始化识别器对象，传入 PaddleOCR-json.exe 的路径。
ocr = GetOcrApi(os.path.join(application_path, r"PaddleOCR-json/PaddleOCR-json.exe"))

def center_window(window, width=460, height=300):
    """Center a tkinter window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

def start_image_processor():
    global root, text, progress
    root = tk.Tk()
    root.title("批量图片识别和重命名进度")
    center_window(root, 600, 550)   # 设置窗口大小

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10, expand=True, fill='both')  # 使框架填充整个窗口

    text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=70, height=20)  # 调整文本框的大小
    text.pack(pady=20, expand=True, fill='both')  # 使文本框填充框架

    progress = ttk.Progressbar(frame, orient='horizontal', length=550, mode='determinate')  # 调整进度条的长度
    progress.pack(pady=20)

    start_button = ttk.Button(frame, text="开始处理", command=start_processing)
    start_button.pack(pady=20)

    root.mainloop()

# 图片识别和重命名的逻辑
def start_processing():
    global progress
    files_to_process = [f for f in os.listdir(pic_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_files = len(files_to_process)
    
    for idx, file in enumerate(files_to_process, start=1):
        img_path = os.path.join(pic_directory, file)
        res = ocr.run(img_path)
        
        if res["code"] == 100 and res["data"]:
            new_name = res["data"][0]["text"][:100] + os.path.splitext(file)[-1]
            new_path = os.path.join(pic_directory, new_name)
            
            if not os.path.exists(new_path):
                try:
                    os.rename(img_path, new_path)
                    text.insert(tk.END, f"{file} 已重命名为 {new_name}\n")
                    text.see(tk.END)  # 这将使文本组件滚动到底部
                except Exception as e:
                    text.insert(tk.END, f"重命名 {file} 为 {new_name} 时出错: {str(e)}\n")
                    text.see(tk.END)  # 这将使文本组件滚动到底部
            else:
                text.insert(tk.END, f"{new_name} 已存在, {file} 没有被重命名。\n")
                text.see(tk.END)  # 这将使文本组件滚动到底部

        else:
            text.insert(tk.END, f"{file} 无法识别。\n")
            text.see(tk.END)  # 这将使文本组件滚动到底部
        
        progress['value'] = (idx / total_files) * 100
        root.update_idletasks()

# 直接启动图像处理器
start_image_processor()