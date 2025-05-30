import os
import fitz  # PyMuPDF
import glob

# 设置工作目录为doc
doc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc')
os.chdir(doc_dir)
print(f"工作目录已设置为: {doc_dir}")

# 获取当前目录下所有PDF文件
pdf_files = glob.glob('*.pdf')
print(f"找到 {len(pdf_files)} 个PDF文件")

for pdf_file in pdf_files:
    try:
        print(f"处理文件: {pdf_file}")
        # 提取文件名（不含扩展名）
        file_name = os.path.splitext(pdf_file)[0]
        md_file = f"{file_name}.md"
        
        # 打开PDF文件
        doc = fitz.open(os.path.join(doc_dir, pdf_file))
        
        # 创建或清空markdown文件
        with open(os.path.join(doc_dir, md_file), 'w', encoding='utf-8') as f:
            f.write(f"# {file_name}\n\n")
        
        # 提取文本并写入markdown
        print(f"提取文本并写入 {md_file}...")
        for i, page in enumerate(doc):
            print(f"  处理第 {i+1}/{len(doc)} 页...")
            text = page.get_text()
            with open(os.path.join(doc_dir, md_file), 'a', encoding='utf-8') as f:
                f.write(f"## 第 {i+1} 页\n\n")
                f.write(text + "\n\n")
        
        # 关闭PDF文件
        doc.close()
        
        print(f"完成: {pdf_file} -> {md_file}")
        print("-" * 50)
    except Exception as e:
        print(f"处理 {pdf_file} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()

print("所有PDF文件处理完成！") 