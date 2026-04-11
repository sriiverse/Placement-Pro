import zipfile
import re
import sys

def extract_text_from_pptx(filepath):
    try:
        with zipfile.ZipFile(filepath, 'r') as slide_zip:
            slide_names = [n for n in slide_zip.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            # Sort slides numerically based on the filename
            def extract_slide_num(name):
                match = re.search(r'slide(\d+)', name)
                return int(match.group(1)) if match else 0
            
            slide_names.sort(key=extract_slide_num)
            
            for slide in slide_names:
                content = slide_zip.read(slide).decode('utf-8')
                # Extract text inside <a:t> tags
                texts = re.findall(r'<a:t>(.*?)</a:t>', content)
                print(f"=== {slide} ===")
                for t in texts:
                    if t.strip():
                        print("-", t)
                print()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

if __name__ == '__main__':
    extract_text_from_pptx(sys.argv[1])
