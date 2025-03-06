import os
import pyautogui
import time
import tkinter as tk
from tkinter import messagebox

def auto_scroll_screenshot(start_pos, end_pos, max_scrolls, interval = 0.5, scroll_step = 100):
    try:
        # 创建保存目录
        save_dir = "./picture_get"
        os.makedirs(save_dir, exist_ok=True)
        
        # 计算截图区域参数
        x1, y1 = start_pos
        x2, y2 = end_pos
        region_width = x2 - x1
        region_height = y2 - y1
        region = (x1, y1, region_width, region_height)

        screen_height = pyautogui.size()[1]  # 获取屏幕高度
        
        # 每次滚动像素（根据用户说明）
        scroll_step = scroll_step  # 默认每次滚动100像素
        
        # 禁用按钮
        start_btn.config(state=tk.DISABLED)
        
        for i in range(max_scrolls):
            # 截图并保存0
            filename = f"x{i}y1.jpg"
            save_path = os.path.join(save_dir, filename)
            pyautogui.screenshot(save_path, region=region)
                
            # 执行滚动
            times = region_height//scroll_step
            pyautogui.vscroll(region_height,x = x1,y = y1)  # 向下滚动100像素
            time.sleep(interval)  # 等待滚动完成
            y1 -= region_height%scroll_step·
            # 检查当前截图区域是否超出屏幕
            if (y1 + region_height) > screen_height:
                # 超出屏幕，回滚一次并终止
                pyautogui.vscroll(pixels=scroll_step)  # 向上回滚
                y1 -= scroll_step
            region = (x1, y1, region_width, region_height)
                    
            # 更新日志
            root.after(0, log_text.insert, tk.END, f"已保存：{filename}\n")
            root.after(0, log_text.see, tk.END)

        # 恢复按钮状态
        root.after(0, lambda: start_btn.config(state=tk.NORMAL))
        root.after(0, lambda: messagebox.showinfo("完成", f"已完成 {max_scrolls} 次截图"))

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("错误", str(e)))
        root.after(0, lambda: start_btn.config(state=tk.NORMAL))
def start_automation():
    try:
        # 坐标参数
        start_pos = (
            int(x1_entry.get()),
            int(y1_entry.get())
        )
        end_pos = (
            int(x2_entry.get()),
            int(y2_entry.get())
        )
        
        # 滚动参数
        max_scrolls = int(scroll_times_entry.get())
        interval = float(interval_entry.get())
        scroll_step = int(scroll_step_entry.get())

        # 参数验证
        if max_scrolls < 1:
            raise ValueError("滚动次数必须大于0")
        
        # 调用核心功能
        auto_scroll_screenshot(start_pos, end_pos, max_scrolls, interval, scroll_step)
    except Exception as e:
        messagebox.showerror("输入错误", str(e))

def select_region():
    # 使用局部变量替代全局变量（方案一）
    x1, y1, x2, y2 = None, None, None, None  # 局部变量声明

    # 创建覆盖全屏的透明画布
    capture_win = tk.Toplevel(root)
    capture_win.attributes('-alpha', 0.3)       # 设置透明度
    capture_win.attributes('-topmost', True)    # 置顶显示
    capture_win.overrideredirect(True)          # 移除窗口边框
    capture_win.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

    canvas = tk.Canvas(capture_win, bg='white', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # 绘制选区框的变量
    rect_id = None

    def on_mouse_down(event):
        nonlocal x1, y1  # 声明访问外层函数变量
        x1, y1 = event.x, event.y

    def on_mouse_move(event):
        nonlocal rect_id, x1, y1  # 显式声明需要的变量
        if x1 is not None and y1 is not None:
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(x1, y1, event.x, event.y, outline='red', width=2)

    def on_mouse_up(event):
        nonlocal x2, y2
        x2, y2 = event.x, event.y
        capture_win.destroy()

    # 绑定鼠标事件
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    canvas.focus_set()

    # 进入事件循环
    capture_win.grab_set()
    capture_win.wait_window()

    # 更新主界面坐标
    if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
        # 确保坐标顺序正确
        x_min = min(x1, x2)
        y_min = min(y1, y2)
        x_max = max(x1, x2)
        y_max = max(y1, y2)
        
        # 更新输入框
        x1_entry.delete(0, tk.END)
        y1_entry.delete(0, tk.END)
        x2_entry.delete(0, tk.END)
        y2_entry.delete(0, tk.END)
        
        x1_entry.insert(0, str(x_min))
        y1_entry.insert(0, str(y_min))
        x2_entry.insert(0, str(x_max))
        y2_entry.insert(0, str(y_max))
        
        messagebox.showinfo("完成", f"已选择区域：({x_min},{y_min})到({x_max},{y_max})")
    else:
        messagebox.showwarning("警告", "未检测到有效选择区域")

from fpdf import FPDF

def generate_pdf():
    pdf = FPDF()
    for filename in os.listdir("./picture_get"):
        if filename.endswith(".jpg"):
            pdf.add_page()
            pdf.image(os.path.join("./picture_get", filename), x=10, y=8, w=190)
    pdf.output("screenshots.pdf")
    messagebox.showinfo("完成", "PDF已生成")

# 创建图形界面
root = tk.Tk()
root.title("滚动截图工具 v1.2")
root.geometry("450x400")

# 输入区域布局
# --- 坐标设置 ---
tk.Label(root, text="起始坐标（左上角）").grid(row=0, column=0, columnspan=2, pady=5)
tk.Label(root, text="X1:").grid(row=1, column=0, sticky="e")
x1_entry = tk.Entry(root, width=8)
x1_entry.insert(0, "0")
x1_entry.grid(row=1, column=1, sticky="w")

tk.Label(root, text="Y1:").grid(row=2, column=0, sticky="e")
y1_entry = tk.Entry(root, width=8)
y1_entry.insert(0, "0")
y1_entry.grid(row=2, column=1, sticky="w")

tk.Label(root, text="结束坐标（右下角）").grid(row=3, column=0, columnspan=2, pady=5)
tk.Label(root, text="X2:").grid(row=4, column=0, sticky="e")
x2_entry = tk.Entry(root, width=8)
x2_entry.insert(0, "800")
x2_entry.grid(row=4, column=1, sticky="w")

tk.Label(root, text="Y2:").grid(row=5, column=0, sticky="e")
y2_entry = tk.Entry(root, width=8)
y2_entry.insert(0, "600")
y2_entry.grid(row=5, column=1, sticky="w")

# --- 滚动参数 ---
tk.Label(root, text="滚动设置").grid(row=6, column=0, columnspan=2, pady=10)
tk.Label(root, text="最大滚动次数:").grid(row=7, column=0, sticky="e")
scroll_times_entry = tk.Entry(root, width=8)
scroll_times_entry.insert(0, "5")
scroll_times_entry.grid(row=7, column=1, sticky="w")

tk.Label(root, text="间隔时间(s):").grid(row=8, column=0, sticky="e")
interval_entry = tk.Entry(root, width=8)
interval_entry.insert(0, "1.0")
interval_entry.grid(row=8, column=1, sticky="w")

tk.Label(root, text="滚动步长(px):").grid(row=9, column=0, sticky="e")
scroll_step_entry = tk.Entry(root, width=8)
scroll_step_entry.insert(0, "100")
scroll_step_entry.grid(row=9, column=1, sticky="w")

# --- 操作按钮 ---
btn_frame = tk.Frame(root)
btn_frame.grid(row=9, column=0, columnspan=2, pady=15)

start_btn = tk.Button(btn_frame, text="开始执行", command=start_automation, width=12)
start_btn.pack(side=tk.LEFT, padx=5)

region_btn = tk.Button(btn_frame, text="选择截图区域", command=select_region, width=12)
region_btn.pack(side=tk.LEFT, padx=5)

pdf_btn = tk.Button(btn_frame, text="输出为PDF", command=generate_pdf, state=tk.DISABLED, width=12)
pdf_btn.pack(side=tk.LEFT, padx=5)

# --- 日志区域 ---
log_text = tk.Text(root, height=10, width=50)
log_text.grid(row=10, column=0, columnspan=3, padx=10, pady=5)

# 窗口居中显示
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - root.winfo_width()) // 2
y = (screen_height - root.winfo_height()) // 2
root.geometry(f"+{x}+{y}")

root.mainloop()