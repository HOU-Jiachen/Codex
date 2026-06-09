import json
import re
from pathlib import Path

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None


ROOT = Path(__file__).resolve().parents[3]
STANDARDS_TEMPLATE_DIR = ROOT / "standards_templates"
OCR_MD_DIR = STANDARDS_TEMPLATE_DIR / "work" / "template_ocr"
OUTPUT = ROOT / "REPORT_TEMPLATE_PROFILE.json"
OCR_THRESHOLD = 500


HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*|[一二三四五六七八九十]+、|第[一二三四五六七八九十]+章)\s*(.{2,80})$")


def extract_pdf_text(path):
    if PdfReader is None:
        return ""
    chunks = []
    try:
        reader = PdfReader(str(path))
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            if text.strip():
                chunks.append(text)
    except Exception:
        return ""
    return "\n".join(chunks)


def style_for_number(number):
    if number.startswith("第") or number.count(".") == 0:
        return "标题一"
    if number.count(".") == 1:
        return "标题二"
    if number.count(".") == 2:
        return "标题三"
    return "标题四"


def read_ocr_markdown():
    if not OCR_MD_DIR.exists():
        return ""
    chunks = []
    for path in sorted(OCR_MD_DIR.glob("*.md")):
        chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def report_book_content(text):
    start_match = re.search(r"(?m)^#+\s*生产建设项目水土保持方案报告书编制内容\s*$", text)
    if not start_match:
        return text
    start = start_match.start()
    end = len(text)
    end_match = re.search(
        r"(?m)^#+\s*(生产建设项目水土保持方案报告书编制格式|生产建设项目水土保持方案报告表编制|附件3)\s*$",
        text[start_match.end():],
    )
    if end_match:
        end = start_match.end() + end_match.start()
    return text[start:end]


def extract_headings(text):
    headings = []
    seen = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("#"):
            continue
        line = re.sub(r"^#+\s*", "", line).strip()
        if not line or len(line) > 90:
            continue
        line = re.sub(r"\.{3,}\s*\d+$", "", line).strip()
        match = HEADING_RE.match(line)
        if not match:
            continue
        number, title = match.groups()
        title = title.strip(" .．\t")
        key = (number, title)
        if not title or key in seen:
            continue
        seen.add(key)
        headings.append({
            "number": number,
            "title": title,
            "style": style_for_number(number),
        })
    return headings


def build_profile():
    profiles = []
    ocr_required = []
    ocr_text = read_ocr_markdown()
    if ocr_text.strip():
        content = report_book_content(ocr_text)
        headings = extract_headings(content)
        if headings:
            profiles.append({
                "path": str(OCR_MD_DIR.relative_to(ROOT)),
                "source": "ocr_markdown",
                "chars": len(content),
                "headings": headings,
            })
    for path in STANDARDS_TEMPLATE_DIR.glob("*.pdf"):
        text = extract_pdf_text(path)
        if len(text.strip()) < OCR_THRESHOLD:
            ocr_required.append({
                "path": str(path.relative_to(ROOT)),
                "reason": "模板 PDF 可抽取文字过少，可能为扫描件，需要先 OCR 后才能提取章节结构。",
                "chars": len(text.strip()),
            })
            continue
        profiles.append({
            "path": str(path.relative_to(ROOT)),
            "source": "pdf_text",
            "chars": len(text),
            "headings": extract_headings(report_book_content(text)),
        })
    result = {
        "template_sources": profiles,
        "ocr_required_templates": ocr_required,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {OUTPUT}")
    if ocr_required:
        print("Template OCR required:")
        for item in ocr_required:
            print(f"- {item['path']}")


if __name__ == "__main__":
    build_profile()
