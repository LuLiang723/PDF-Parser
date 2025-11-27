import pypdfium2 as pdfium

def print_asus_manual_toc(file_path):
    try:
        pdf = pdfium.PdfDocument(file_path)
        toc = pdf.get_toc()

        for item in toc:
            # 1.取得層級
            level = item.level 
            
            # 2.取得標題
            title = item.get_title()
            if not title:
                title = "(無標題)"

            # 3.取得頁碼
            page_display = ""
            try:
                dest = item.get_dest()
                
                if dest:
                    page_idx = dest.get_index()
                    
                    if page_idx is not None:
                        page_display = f"p.{page_idx + 1}"
                    else:
                        page_display = "(無對應頁碼)"
                else:
                    page_display = ""
            except Exception as e:
                page_display = f"解析頁碼失敗: {e}"

            indent = "    " * level
            page_info = f" [{page_display}]" if page_display else ""
            
            print(f"{indent}- {title}{page_info}")

    except Exception as e:
        print(f"發生錯誤: {e}")

file_path = "E20198_TUF_GAMING_B650M-PLUS_UM_WEB.pdf"
print_asus_manual_toc(file_path)