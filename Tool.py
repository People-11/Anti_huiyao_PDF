import pikepdf
import re
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

class PDFJavaScriptProcessor:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("PDF JavaScript 处理工具")
        self.root.geometry("300x400")
        self.root.resizable(True, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主标题
        title_label = tk.Label(self.root, text="PDF JavaScript 处理工具", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 操作选择框架
        operation_frame = tk.LabelFrame(self.root, text="选择操作", font=("Arial", 12))
        operation_frame.pack(pady=10, padx=20, fill="x")
        
        self.operation_var = tk.StringVar(value="extract")
        
        extract_radio = tk.Radiobutton(operation_frame, text="提取 JavaScript 代码", 
                                     variable=self.operation_var, value="extract",
                                     font=("Arial", 10))
        extract_radio.pack(anchor="w", padx=10, pady=5)
        
        bypass_radio = tk.Radiobutton(operation_frame, text="绕过 JavaScript 限制", 
                                    variable=self.operation_var, value="bypass",
                                    font=("Arial", 10))
        bypass_radio.pack(anchor="w", padx=10, pady=5)
        
        # 文件选择框架
        file_frame = tk.LabelFrame(self.root, text="选择 PDF 文件", font=("Arial", 12))
        file_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 拖拽区域
        self.drop_frame = tk.Frame(file_frame, bg="#E8F4FD", relief="groove", bd=3)
        self.drop_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        drop_label = tk.Label(self.drop_frame, text="📁 将 PDF 文件拖拽到此处 📁\n或点击下方按钮选择文件", 
                             bg="#E8F4FD", font=("Arial", 12), fg="#2E86AB")
        drop_label.pack(expand=True)
        
        # 启用拖拽功能
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # 文件路径显示
        self.file_path_var = tk.StringVar()
        self.file_path_label = tk.Label(file_frame, textvariable=self.file_path_var, 
                                       wraplength=500, justify="left")
        self.file_path_label.pack(pady=5, padx=10, fill="x")
        
        # 按钮框架
        button_frame = tk.Frame(file_frame)
        button_frame.pack(pady=10)
        
        select_button = tk.Button(button_frame, text="选择文件", command=self.select_file,
                                font=("Arial", 10))
        select_button.pack(side="left", padx=5)
        
        process_button = tk.Button(button_frame, text="开始处理", command=self.process_file,
                                 font=("Arial", 10), bg="green", fg="white")
        process_button.pack(side="left", padx=5)
        
        clear_button = tk.Button(button_frame, text="清除", command=self.clear_file,
                               font=("Arial", 10))
        clear_button.pack(side="left", padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_label = tk.Label(self.root, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_label.pack(side="bottom", fill="x")
        
    def on_drop(self, event):
        """处理文件拖拽事件"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.pdf'):
                self.file_path_var.set(f"已选择: {file_path}")
                self.current_file = file_path
                self.status_var.set("文件已加载，可以开始处理")
            else:
                messagebox.showerror("错误", "请选择 PDF 文件")
                
    def select_file(self):
        """通过文件对话框选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(f"已选择: {file_path}")
            self.current_file = file_path
            self.status_var.set("文件已加载，可以开始处理")
            
    def clear_file(self):
        """清除已选择的文件"""
        self.file_path_var.set("")
        self.current_file = None
        self.status_var.set("就绪")
        
    def process_file(self):
        """处理文件"""
        if not hasattr(self, 'current_file') or not self.current_file:
            messagebox.showerror("错误", "请先选择一个 PDF 文件")
            return
            
        if not os.path.exists(self.current_file):
            messagebox.showerror("错误", "选择的文件不存在")
            return
            
        operation = self.operation_var.get()
        
        try:
            if operation == "extract":
                self.extract_javascript()
            else:
                self.bypass_javascript()
        except Exception as e:
            messagebox.showerror("错误", f"处理文件时发生错误:\n{str(e)}")
            self.status_var.set("处理失败")
            
    def extract_javascript(self):
        """提取 JavaScript 代码"""
        self.status_var.set("正在提取 JavaScript...")
        
        javascript_code = []
        try:
            with pikepdf.Pdf.open(self.current_file) as pdf:
                # 检查 /Names/JavaScript
                for name in pdf.Root.get("/Names", {}).get("/JavaScript", {}).get("/Names", []):
                    if isinstance(name, pikepdf.String):
                        obj_ref = name
                        try:
                            js_action = pdf.get_object(obj_ref)
                            if js_action and isinstance(js_action, pikepdf.Dictionary) and '/JS' in js_action:
                                js_code = js_action.JS
                                if isinstance(js_code, pikepdf.String):
                                    javascript_code.append(str(js_code))
                                elif isinstance(js_code, pikepdf.Stream):
                                    javascript_code.append(js_code.read_bytes().decode('utf-8', errors='ignore'))
                        except Exception:
                            pass

                # 检查 OpenAction
                if '/OpenAction' in pdf.Root:
                    open_action = pdf.Root.OpenAction
                    if open_action and isinstance(open_action, pikepdf.Dictionary) and open_action.get('/S') == '/JavaScript' and '/JS' in open_action:
                        js_code = open_action.JS
                        if isinstance(js_code, pikepdf.String):
                            javascript_code.append(str(js_code))
                        elif isinstance(js_code, pikepdf.Stream):
                            javascript_code.append(js_code.read_bytes().decode('utf-8', errors='ignore'))
                
                # 搜索其他对象中的 JavaScript
                for obj in pdf.objects:
                    if isinstance(obj, pikepdf.Dictionary):
                        # 检查 Additional Actions
                        if '/AA' in obj:
                            additional_actions = obj.AA
                            if isinstance(additional_actions, pikepdf.Dictionary):
                                for action_type in additional_actions:
                                    action_dict = additional_actions.get(action_type)
                                    if isinstance(action_dict, pikepdf.Dictionary) and action_dict.get('/S') == '/JavaScript' and '/JS' in action_dict:
                                        js_code = action_dict.JS
                                        if isinstance(js_code, pikepdf.String):
                                            code_str = str(js_code)
                                            if code_str not in javascript_code:
                                                javascript_code.append(code_str)
                                        elif isinstance(js_code, pikepdf.Stream):
                                            code_bytes = js_code.read_bytes().decode('utf-8', errors='ignore')
                                            if code_bytes not in javascript_code:
                                                javascript_code.append(code_bytes)
                        
                        # 直接检查 JavaScript 动作
                        if obj.get('/S') == '/JavaScript' and '/JS' in obj:
                            js_code = obj.JS
                            if isinstance(js_code, pikepdf.String):
                                code_str = str(js_code)
                                if code_str not in javascript_code:
                                    javascript_code.append(code_str)
                            elif isinstance(js_code, pikepdf.Stream):
                                code_bytes = js_code.read_bytes().decode('utf-8', errors='ignore')
                                if code_bytes not in javascript_code:
                                    javascript_code.append(code_bytes)

        except Exception as e:
            raise e
        
        # 去重处理
        unique_javascript_code = []
        seen_code = set()
        for code in javascript_code:
            normalized_code = code.strip()
            if normalized_code and normalized_code not in seen_code:
                unique_javascript_code.append(normalized_code)
                seen_code.add(normalized_code)
        
        if unique_javascript_code:
            # 保存到文件
            base_name = os.path.splitext(self.current_file)[0]
            output_file = f"{base_name}_extracted_javascript.js"
            
            with open(output_file, "w", encoding="utf-8") as f:
                for i, js in enumerate(unique_javascript_code):
                    f.write(f"// --- Script {i+1} ---\n")
                    f.write(js)
                    f.write("\n\n")
            
            messagebox.showinfo("成功", f"找到 {len(unique_javascript_code)} 个 JavaScript 脚本\n"
                                      f"已保存到: {output_file}")
            self.status_var.set(f"提取完成，共 {len(unique_javascript_code)} 个脚本")
        else:
            messagebox.showinfo("结果", "未在 PDF 中找到 JavaScript 代码")
            self.status_var.set("未找到 JavaScript")
            
    def bypass_javascript(self):
        """绕过 JavaScript 限制"""
        self.status_var.set("正在绕过 JavaScript 限制...")
        
        base_name = os.path.splitext(self.current_file)[0]
        output_file = f"{base_name}_bypassed.pdf"
        
        modified = False
        
        with pikepdf.Pdf.open(self.current_file) as pdf:
            # 检查并修改 OpenAction
            if '/OpenAction' in pdf.Root:
                open_action = pdf.Root.OpenAction
                if isinstance(open_action, pikepdf.Dictionary) and open_action.get('/S') == '/JavaScript':
                    js_code = open_action.get('/JS')
                    if js_code:
                        if isinstance(js_code, pikepdf.Stream):
                            js_bytes = js_code.read_bytes()
                            try:
                                js_str = js_bytes.decode('utf-8')
                            except UnicodeDecodeError:
                                js_str = js_bytes.decode('latin1')
                        elif isinstance(js_code, pikepdf.String):
                            js_str = str(js_code)
                        else:
                            js_str = None
                        
                        if js_str:
                            # 修改 JavaScript：将 if 条件改为 if (false)
                            modified_js = re.sub(r'if\s*\(.*?\)', 'if (false)', js_str)
                            
                            if isinstance(js_code, pikepdf.Stream):
                                open_action.JS = pikepdf.Stream(pdf, modified_js.encode('utf-8'))
                            else:
                                open_action.JS = pikepdf.String(modified_js)
                            modified = True
            
            # 检查并修改其他 JavaScript 动作
            for obj in pdf.objects:
                if isinstance(obj, pikepdf.Dictionary):
                    # 修改 Additional Actions
                    if '/AA' in obj:
                        additional_actions = obj.AA
                        if isinstance(additional_actions, pikepdf.Dictionary):
                            for action_type in additional_actions:
                                action_dict = additional_actions.get(action_type)
                                if isinstance(action_dict, pikepdf.Dictionary) and action_dict.get('/S') == '/JavaScript' and '/JS' in action_dict:
                                    js_code = action_dict.JS
                                    if isinstance(js_code, pikepdf.String):
                                        js_str = str(js_code)
                                        modified_js = re.sub(r'if\s*\(.*?\)', 'if (false)', js_str)
                                        action_dict.JS = pikepdf.String(modified_js)
                                        modified = True
                                    elif isinstance(js_code, pikepdf.Stream):
                                        js_bytes = js_code.read_bytes()
                                        try:
                                            js_str = js_bytes.decode('utf-8')
                                        except UnicodeDecodeError:
                                            js_str = js_bytes.decode('latin1')
                                        modified_js = re.sub(r'if\s*\(.*?\)', 'if (false)', js_str)
                                        action_dict.JS = pikepdf.Stream(pdf, modified_js.encode('utf-8'))
                                        modified = True
                    
                    # 修改直接的 JavaScript 动作
                    if obj.get('/S') == '/JavaScript' and '/JS' in obj:
                        js_code = obj.JS
                        if isinstance(js_code, pikepdf.String):
                            js_str = str(js_code)
                            modified_js = re.sub(r'if\s*\(.*?\)', 'if (false)', js_str)
                            obj.JS = pikepdf.String(modified_js)
                            modified = True
                        elif isinstance(js_code, pikepdf.Stream):
                            js_bytes = js_code.read_bytes()
                            try:
                                js_str = js_bytes.decode('utf-8')
                            except UnicodeDecodeError:
                                js_str = js_bytes.decode('latin1')
                            modified_js = re.sub(r'if\s*\(.*?\)', 'if (false)', js_str)
                            obj.JS = pikepdf.Stream(pdf, modified_js.encode('utf-8'))
                            modified = True

            # 保存修改后的 PDF
            pdf.save(output_file)
        
        if modified:
            messagebox.showinfo("成功", f"已成功绕过 JavaScript 限制\n"
                                      f"修改后的文件保存为: {output_file}")
            self.status_var.set("绕过限制完成")
        else:
            messagebox.showinfo("结果", "未在 PDF 中找到需要修改的 JavaScript 限制")
            self.status_var.set("未找到需要修改的限制")
            
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = PDFJavaScriptProcessor()
        app.run()
    except ImportError as e:
        if "tkinterdnd2" in str(e):
            print("错误: 需要安装 tkinterdnd2 库来支持拖拽功能")
            print("请运行: pip install tkinterdnd2")
        else:
            print(f"导入错误: {e}")
        input("按 Enter 键退出...")
    except Exception as e:
        print(f"程序运行错误: {e}")
        input("按 Enter 键退出...")

if __name__ == "__main__":
    main()