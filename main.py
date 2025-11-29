import pypdfium2 as pdfium
import json
import argparse
from pathlib import Path


def parse_pdf_toc(file_path):
    """解析 PDF 目錄結構，返回多階層的巢狀字典"""
    pdf = pdfium.PdfDocument(file_path)
    toc = pdf.get_toc()

    toc_items = []
    for item in toc:
        level = item.level
        title = item.get_title() or "無標題"

        page_idx = None
        try:
            dest = item.get_dest()
            if dest:
                page_idx = dest.get_index()
        except:
            pass

        toc_items.append(
            {
                "level": level,
                "title": title,
                "page": page_idx + 1 if page_idx is not None else None,
            }
        )

    return pdf, toc_items


def build_hierarchy(toc_items):
    """將扁平的 TOC 項目建立成多階層巢狀結構"""
    root = {"children": {}}
    stack = [(-1, root)]

    for item in toc_items:
        level = item["level"]
        title = item["title"]
        page = item["page"]

        while stack and stack[-1][0] >= level:
            stack.pop()

        parent = stack[-1][1]

        new_node = {"page": page, "children": {}, "content": None}

        if "children" not in parent:
            parent["children"] = {}
        parent["children"][title] = new_node

        stack.append((level, new_node))

    return root["children"]


def collect_all_pages(structure, result=None, order_counter=None):
    """收集所有頁碼資訊，用於計算內容範圍，保留原始順序"""
    if result is None:
        result = []
    if order_counter is None:
        order_counter = [0]

    for title, data in structure.items():
        current_order = order_counter[0]
        order_counter[0] += 1

        if data["page"]:
            result.append((title, data["page"], data, current_order))

        if data.get("children"):
            collect_all_pages(data["children"], result, order_counter)

    return result


def extract_text_by_page_range(pdf, start_page, end_page):
    """提取指定頁碼範圍的文字內容"""
    text = ""
    for page_idx in range(start_page - 1, min(end_page, len(pdf))):
        page = pdf[page_idx]
        textpage = page.get_textpage()
        text += textpage.get_text_bounded() + "\n"
    return text.strip()


def extract_section_text(pdf, start_page, end_page, current_title, next_title=None):
    """提取章節內容，如果同頁有多個章節則用標題來分割"""
    full_text = extract_text_by_page_range(pdf, start_page, end_page)

    # 先找到當前標題的位置，從該位置開始提取
    current_title_pos = full_text.find(current_title)
    if current_title_pos > 0:
        full_text = full_text[current_title_pos:]

    # 如果有下一個標題，找到下一個標題的位置來截斷
    if next_title:
        # 在剩餘文字中找下一個標題
        search_start = len(current_title)
        next_title_pos = full_text.find(next_title, search_start)
        if next_title_pos > 0:
            return full_text[:next_title_pos].strip()

    return full_text.strip()


def fill_leaf_content(pdf, structure, all_pages_list):
    """為沒有子節點的標題填充內容"""
    for title, data in structure.items():
        has_children = data.get("children") and len(data["children"]) > 0

        if has_children:
            # 有子節點，遞迴處理
            fill_leaf_content(pdf, data["children"], all_pages_list)
        else:
            # 沒有子節點，填充內容
            if data["page"]:
                start_page = data["page"]
                current_order = None
                next_title = None
                next_page = None

                # 先找到當前項目的順序
                for i, (t, p, d, order) in enumerate(all_pages_list):
                    if d is data:
                        current_order = order
                        break

                # 找到順序上的下一個項目
                if current_order is not None:
                    for t, p, d, order in all_pages_list:
                        if order == current_order + 1:
                            next_title = t
                            next_page = p
                            break

                # 決定結束頁碼
                if next_page is not None:
                    end_page = next_page
                else:
                    end_page = len(pdf) + 1

                # 提取內容，使用標題分割
                data["content"] = extract_section_text(
                    pdf, start_page, end_page, title, next_title
                )


def clean_structure_for_json(structure):
    """清理結構，移除空的 children 並整理格式"""
    result = {}
    for title, data in structure.items():
        node = {"page": data["page"]}

        if data.get("children") and len(data["children"]) > 0:
            node["children"] = clean_structure_for_json(data["children"])

        if data.get("content"):
            node["content"] = data["content"]

        result[title] = node

    return result


def save_toc_to_json(toc_structure, output_path):
    """儲存結構化資料到JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(toc_structure, f, ensure_ascii=False, indent=2)
    print(f"目錄已儲存至: {output_path}")


def print_structure(structure, indent=0):
    """遞迴顯示目錄結構"""
    for title, data in structure.items():
        prefix = "    " * indent
        page_info = f"[p.{data['page']}]" if data.get("page") else ""
        has_content = "[有內容]" if data.get("content") else ""
        print(f"{prefix}- {title} {page_info} {has_content}")

        if data.get("children"):
            print_structure(data["children"], indent + 1)


def main(file_path: str):
    pdf, toc_items = parse_pdf_toc(file_path)
    structure = build_hierarchy(toc_items)

    all_pages = collect_all_pages(structure)
    print(structure)

    fill_leaf_content(pdf, structure, all_pages)

    clean_structure = clean_structure_for_json(structure)

    save_toc_to_json(clean_structure, f"output/{Path(file_path).stem}_structured.json")

    print("\n=== 目錄結構 ===")
    print_structure(clean_structure)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert PDF into structured file for RAG system"
    )
    parser.add_argument("file_path", help="Which file you want to convert")
    args = parser.parse_args()

    main(args.file_path)
