import pypdfium2 as pdfium

def print_asus_manual_toc(file_path):
    try:
        pdf = pdfium.PdfDocument(file_path)
        toc = pdf.get_toc()

        for item in toc:
            level = item.level 
            
            title = item.get_title()
            if not title:
                title = "無標題"

            page_display = ""
            try:
                dest = item.get_dest()
                if dest:
                    page_idx = dest.get_index()
                    
                    if page_idx is not None:
                        page_display = f"p.{page_idx + 1}"
                    else:
                        page_display = "無對應頁碼"
                else:
                    page_display = ""
            except Exception as e:
                page_display = f"無法獲取頁碼"

            indent = "    " * level
            page_info = f" [{page_display}]" if page_display else ""
            
            print(f"{indent}- {title}{page_info}")

    except Exception as e:
        print(f"Error: {e}")

file_path = "E20198_TUF_GAMING_B650M-PLUS_UM_WEB.pdf"
print_asus_manual_toc(file_path)