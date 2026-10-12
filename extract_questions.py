"""Extract all 600 questions, underlined answers, and illustrations from the CSGT PDF."""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "source" / "official-600-questions.pdf"
JSON = ROOT / "questions.json"
JS = ROOT / "questions-data.js"
IMAGE_DIR = ROOT / "images"
IMAGE_DIR.mkdir(exist_ok=True)
CHAPTERS = (
    (1, 180, "CHƯƠNG I. QUY ĐỊNH CHUNG VÀ QUY TẮC GIAO THÔNG ĐƯỜNG BỘ", "CHAPTER I. GENERAL PROVISIONS AND ROAD TRAFFIC RULES"),
    (181, 205, "CHƯƠNG II. VĂN HÓA GIAO THÔNG, ĐẠO ĐỨC NGƯỜI LÁI XE, KỸ NĂNG PHÒNG CHÁY, CHỮA CHÁY VÀ CỨU HỘ, CỨU NẠN", "CHAPTER II. TRAFFIC CULTURE, DRIVER ETHICS, FIRE SAFETY AND RESCUE SKILLS"),
    (206, 263, "CHƯƠNG III. KỸ THUẬT LÁI XE", "CHAPTER III. DRIVING TECHNIQUES"),
    (264, 300, "CHƯƠNG IV. CẤU TẠO VÀ SỬA CHỮA", "CHAPTER IV. VEHICLE CONSTRUCTION AND REPAIR"),
    (301, 485, "CHƯƠNG V. BÁO HIỆU ĐƯỜNG BỘ", "CHAPTER V. ROAD SIGNS AND SIGNALS"),
    (486, 600, "CHƯƠNG VI. GIẢI THẾ SA HÌNH VÀ KỸ NĂNG XỬ LÝ TÌNH HUỐNG GIAO THÔNG", "CHAPTER VI. TRAFFIC DIAGRAMS AND SITUATION HANDLING SKILLS"),
)
QUESTION = re.compile(r"^\s*Câu\s+(\d+)\s*[.:]\s*(.*)$", re.I)
OPTION = re.compile(r"^\s*([1-4])\.\s+(.*)$")
SECOND_COLUMN = re.compile(r"\s{4,}(?=[1-4]\.\s)")


def clean(value):
    return " ".join(value.split())


def plain(value):
    return "".join(c for c in unicodedata.normalize("NFD", value) if unicodedata.category(c) != "Mn").lower()


def translation_cache():
    cache_path = ROOT / "translations_en.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    if JSON.exists():
        for q in json.loads(JSON.read_text(encoding="utf-8")):
            for vi, en in ((q.get("vietnamese"), q.get("english")), (q.get("category"), q.get("category_english"))):
                if vi and en:
                    cache.setdefault(vi, en)
            for o in q.get("options", []):
                if o.get("vietnamese") and o.get("english"):
                    cache.setdefault(o["vietnamese"], o["english"])
    return cache


def split_line(line):
    chars = [c for span in line["spans"] for c in span["chars"]]
    text = "".join(c["c"] for c in chars)
    boundaries = [0] + [match.end() for match in SECOND_COLUMN.finditer(text)] + [len(text)]
    for start, end in zip(boundaries, boundaries[1:]):
        segment = text[start:end].strip()
        visible = [c for c in chars[start:end] if not c["c"].isspace()]
        if segment and visible:
            yield segment, (
                min(c["bbox"][0] for c in visible), min(c["bbox"][1] for c in visible),
                max(c["bbox"][2] for c in visible), max(c["bbox"][3] for c in visible),
            )


def make_question(number, page):
    vi, en = next((vi, en) for lo, hi, vi, en in CHAPTERS if lo <= number <= hi)
    return {"id": number, "number": number, "printed_number": number,
            "category": vi, "category_english": en, "vietnamese": "", "english": "",
            "options": [], "answer": None, "page": page, "image": None, "images": []}


def finish(questions, q):
    if q is not None:
        q["vietnamese"] = clean(q["vietnamese"])
        q["options"].sort(key=lambda o: o["index"])
        for o in q["options"]:
            o["vietnamese"] = clean(o["vietnamese"])
        q["image"] = q["images"][0] if q["images"] else None
        questions.append(q)


def match_underlines(page, questions):
    marks = [
        drawing["rect"]
        for drawing in page.get_drawings()
        if drawing.get("type") == "f"
        and drawing.get("fill") is not None
        # Most answer underlines are black; question 204 is rendered as a
        # dark gray Word underline in the source PDF.
        and max(drawing["fill"]) <= 0.15
        and drawing["rect"].height <= 1.6
        and drawing["rect"].width >= 3
    ]
    for q in questions:
        for option in q["options"]:
            for line_page, (x0, y0, x1, y1) in option["_lines"]:
                if line_page != page.number + 1:
                    continue
                for mark in marks:
                    overlap = max(0, min(x1, mark.x1) - max(x0, mark.x0))
                    if 0.7 <= y1 - mark.y0 <= 2.6 and overlap >= 3:
                        option["_score"] = option.get("_score", 0) + overlap


def extract():
    if not PDF.is_file():
        raise FileNotFoundError(f"Expected official 600-question source PDF at {PDF}")
    cache = translation_cache()
    questions = []
    current = None
    current_option = None
    with fitz.open(PDF) as doc:
        for page in doc:
            in_chapter_heading = False
            blocks = sorted(page.get_text("rawdict")["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            for block in blocks:
                if block["type"] == 1:
                    if current is not None:
                        ext = block.get("ext", "png").lower()
                        filename = f"q{current['number']:03d}_img{len(current['images']) + 1}.{ext}"
                        path = IMAGE_DIR / filename
                        image_bytes = block["image"]
                        if not path.exists() or path.read_bytes() != image_bytes:
                            path.write_bytes(image_bytes)
                        current["images"].append(filename)
                    continue
                for line in block.get("lines", []):
                    for text, bbox in split_line(line):
                        if text.isdigit() and 280 <= bbox[0] <= 340 and bbox[1] < 60:
                            continue
                        match = QUESTION.match(text)
                        if match:
                            in_chapter_heading = False
                            finish(questions, current)
                            current = make_question(int(match.group(1)), page.number + 1)
                            current["vietnamese"] = match.group(2)
                            current_option = None
                            continue
                        if plain(text).startswith("chuong "):
                            in_chapter_heading = True
                            continue
                        if current is None or in_chapter_heading:
                            continue
                        if re.fullmatch(r"[\d\s]+", text):
                            # Diagram labels (e.g. the two signs in question 362)
                            # are visible inside the picture, not question prose.
                            continue
                        match = OPTION.match(text)
                        if match:
                            current_option = {"index": int(match.group(1)) - 1,
                                              "vietnamese": match.group(2), "english": "",
                                              "_lines": [(page.number + 1, bbox)]}
                            current["options"].append(current_option)
                        elif current_option is not None:
                            current_option["vietnamese"] += " " + text
                            current_option["_lines"].append((page.number + 1, bbox))
                        else:
                            current["vietnamese"] += " " + text
            # Some options started on the prior page and continue on this one.
            match_underlines(page, questions + ([current] if current else []))
        finish(questions, current)

    ambiguous = []
    for q in questions:
        positive = [(o["index"], o.get("_score", 0)) for o in q["options"] if o.get("_score", 0) > 0]
        if len(positive) == 1:
            q["answer"] = positive[0][0]
        else:
            ambiguous.append((q["number"], positive))
        q["english"] = cache.get(q["vietnamese"], "")
        for o in q["options"]:
            o["english"] = cache.get(o["vietnamese"], "")
            o.pop("_lines", None)
            o.pop("_score", None)
    numbers = [q["number"] for q in questions]
    if numbers != list(range(1, 601)):
        raise ValueError(f"Numbering: {len(questions)} rows, missing {sorted(set(range(1, 601)) - set(numbers))}, duplicates {[n for n,c in Counter(numbers).items() if c > 1]}")
    if ambiguous:
        raise ValueError(f"Uncertain answer underlines in {len(ambiguous)} questions: {ambiguous}")
    image_count = sum(len(q["images"]) for q in questions)
    image_questions = sum(bool(q["images"]) for q in questions)
    if (image_count, image_questions) != (319, 318):
        raise ValueError(f"Expected 319 image objects across 318 questions; found {image_count} across {image_questions}")
    JSON.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
    JS.write_text("window.__QUESTIONS__ = " + json.dumps(questions, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"Extracted {len(questions)} questions; {image_count} images across {image_questions} questions")
    chapter_counts = dict(Counter(q["category"] for q in questions))
    print("Chapters:", json.dumps(chapter_counts, ensure_ascii=True))
    print("Missing English:", sum(not q["english"] for q in questions), "questions;", sum(not o["english"] for q in questions for o in q["options"]), "options")


if __name__ == "__main__":
    extract()
