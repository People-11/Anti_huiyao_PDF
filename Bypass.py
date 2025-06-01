import pikepdf
import re

def modify_pdf_openaction_javascript(input_pdf, output_pdf):
    with pikepdf.Pdf.open(input_pdf) as pdf:
        # 检查是否存在 /OpenAction
        if '/OpenAction' in pdf.Root:
            open_action = pdf.Root.OpenAction
            # 确认这是一个 JavaScript 动作
            if isinstance(open_action, pikepdf.Dictionary) and open_action.get('/S') == '/JavaScript':
                js_code = open_action.get('/JS')
                if js_code:
                    # 处理 /JS 字段的内容
                    if isinstance(js_code, pikepdf.Stream):
                        # 如果是流对象，解压并解码
                        js_bytes = js_code.read_bytes()
                        try:
                            js_str = js_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            js_str = js_bytes.decode('latin1')  # 尝试其他编码
                    elif isinstance(js_code, pikepdf.String):
                        js_str = str(js_code)
                    else:
                        print("无法识别的 /JS 类型。")
                        return

                    # 修改 JavaScript：将 if 条件改为 if (false)
                    modified_js = re.sub(r'if\s*\(.*?\)', 'if (false)', js_str)

                    # 写回修改后的 JavaScript
                    if isinstance(js_code, pikepdf.Stream):
                        open_action.JS = pikepdf.Stream(pdf, modified_js.encode('utf-8'))
                    else:
                        open_action.JS = pikepdf.String(modified_js)
                    print("成功修改 /OpenAction 中的 JavaScript！")
                else:
                    print("未找到 /JS 字段。")
            else:
                print("/OpenAction 不是 JavaScript 动作。")
        else:
            print("PDF 中未找到 /OpenAction。")

        # 保存修改后的 PDF
        pdf.save(output_pdf)
        print(f"已生成修改后的 PDF: {output_pdf}")

# 使用示例
if __name__ == "__main__":
    input_file = "input.pdf"  # 替换为您的 PDF 文件路径
    output_file = "output.pdf"  # 输出文件路径
    modify_pdf_openaction_javascript(input_file, output_file)