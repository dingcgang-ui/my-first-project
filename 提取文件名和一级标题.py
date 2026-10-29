import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


def clean_title(title):
    """清除标题开头的序号和符号（取自 删除标题符号.py 的格式要求）"""
    pattern = (
        r"^\s*"
        r"(?:"
        r"\d+[\(（][一二三四五六七八九十百千万零〇\d]+[\)）]"
        r"|"
        r"[一二三四五六七八九十百千万零〇\d]+[、.．）)]"
        r"|"
        r"[\(（][一二三四五六七八九十百千万零〇\d]+[\)）]"
        r")"
        r"[\s、,，.．。:：;；）)]*"
    )

    cleaned = re.sub(pattern, "", str(title))
    while True:
        new_cleaned = re.sub(pattern, "", cleaned)
        if new_cleaned == cleaned:
            break
        cleaned = new_cleaned

    return cleaned.strip() if cleaned.strip() else str(title).strip()


def main():
    # 隐藏主窗口
    root = tk.Tk()
    root.withdraw()

    # 选择 JSON 文件
    file_path = filedialog.askopenfilename(
        title="选择 JSON 文件",
        filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
    )

    if not file_path:
        messagebox.showinfo("提示", "未选择文件，程序退出。")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("错误", f"读取 JSON 文件失败：\n{e}")
        return

    # 直接遍历原始 JSON：维护当前"文件名"上下文，
    # 遇到"一级标题"就归入最近的父级文件名；
    # 遇到新的"文件名"则更新上下文，其下的"一级标题"归入新文件。
    grouped = {}

    def walk(obj, current_file):
        if isinstance(obj, dict):
            # 先看当前 dict 是否带"文件名"，有则更新上下文
            if '文件名' in obj and obj['文件名'] is not None:
                current_file = obj['文件名']
                grouped.setdefault(current_file, [])
            # 当前 dict 自身的"一级标题"清洗后归入 current_file
            if '一级标题' in obj and obj['一级标题'] is not None and current_file is not None:
                cleaned = clean_title(obj['一级标题'])
                titles = grouped.setdefault(current_file, [])
                if cleaned not in titles:
                    titles.append(cleaned)
            # 递归子项，沿用（或子项内更新过的）current_file
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    walk(v, current_file)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    walk(item, current_file)

    walk(data, None)

    # 生成输出路径（与源文件同目录，文件名加后缀）
    src_dir = os.path.dirname(file_path)
    src_name = os.path.splitext(os.path.basename(file_path))[0]
    out_path = os.path.join(src_dir, f"{src_name}_extracted.json")

    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(grouped, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("错误", f"保存 JSON 文件失败：\n{e}")
        return

    total_files = len(grouped)
    total_titles = sum(len(v) for v in grouped.values())
    messagebox.showinfo(
        "完成",
        f"提取完成！\n\n共 {total_files} 个文件，{total_titles} 个一级标题\n保存路径：\n{out_path}"
    )


if __name__ == "__main__":
    main()