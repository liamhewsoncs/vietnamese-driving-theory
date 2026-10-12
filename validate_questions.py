"""Validate the complete illustrated 600-question CSGT data and browser bundle.

Run with --require-english when translation work is complete. Structural and
source-fidelity checks run independently of English text availability.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JS_PREFIX = "window.__QUESTIONS__ = "
CHAPTERS = (
    (1, 180, "CHƯƠNG I. QUY ĐỊNH CHUNG VÀ QUY TẮC GIAO THÔNG ĐƯỜNG BỘ", "CHAPTER I. GENERAL PROVISIONS AND ROAD TRAFFIC RULES"),
    (181, 205, "CHƯƠNG II. VĂN HÓA GIAO THÔNG, ĐẠO ĐỨC NGƯỜI LÁI XE, KỸ NĂNG PHÒNG CHÁY, CHỮA CHÁY VÀ CỨU HỘ, CỨU NẠN", "CHAPTER II. TRAFFIC CULTURE, DRIVER ETHICS, FIRE SAFETY AND RESCUE SKILLS"),
    (206, 263, "CHƯƠNG III. KỸ THUẬT LÁI XE", "CHAPTER III. DRIVING TECHNIQUES"),
    (264, 300, "CHƯƠNG IV. CẤU TẠO VÀ SỬA CHỮA", "CHAPTER IV. VEHICLE CONSTRUCTION AND REPAIR"),
    (301, 485, "CHƯƠNG V. BÁO HIỆU ĐƯỜNG BỘ", "CHAPTER V. ROAD SIGNS AND SIGNALS"),
    (486, 600, "CHƯƠNG VI. GIẢI THẾ SA HÌNH VÀ KỸ NĂNG XỬ LÝ TÌNH HUỐNG GIAO THÔNG", "CHAPTER VI. TRAFFIC DIAGRAMS AND SITUATION HANDLING SKILLS"),
)


def validate(require_english=False):
    errors = []
    english_errors = []
    questions = json.loads((ROOT / "questions.json").read_text(encoding="utf-8"))
    bundle = (ROOT / "questions-data.js").read_text(encoding="utf-8")
    if not bundle.startswith(JS_PREFIX) or not bundle.rstrip().endswith(";"):
        errors.append("questions-data.js has an invalid wrapper")
    else:
        browser_data = json.loads(bundle[len(JS_PREFIX):].strip()[:-1])
        if browser_data != questions:
            errors.append("questions-data.js differs from questions.json")

    numbers = [q.get("number") for q in questions]
    if numbers != list(range(1, 601)):
        errors.append(f"expected exactly 1–600 in order; missing={sorted(set(range(1,601))-set(numbers))}, duplicates={[n for n,c in Counter(numbers).items() if c>1]}")
    if len(questions) != 600:
        errors.append(f"expected 600 questions, found {len(questions)}")

    all_images = []
    image_question_count = 0
    for position, q in enumerate(questions, start=1):
        label = f"question {q.get('number', position)}"
        if q.get("id") != position or q.get("printed_number") != position:
            errors.append(f"{label}: id or printed number differs from logical number")
        expected = next(((vi, en) for lo, hi, vi, en in CHAPTERS if lo <= position <= hi), None)
        if expected and (q.get("category"), q.get("category_english")) != expected:
            errors.append(f"{label}: category mismatch at chapter boundary")
        if not q.get("vietnamese", "").strip():
            errors.append(f"{label}: missing Vietnamese question")
        if not isinstance(q.get("page"), int) or not 5 <= q["page"] <= 188:
            errors.append(f"{label}: invalid source page {q.get('page')}")
        options = q.get("options", [])
        indices = [o.get("index") for o in options]
        if indices != list(range(len(options))) or len(options) not in (2, 3, 4):
            errors.append(f"{label}: invalid option indices/count {indices}")
        if q.get("answer") not in indices:
            errors.append(f"{label}: answer {q.get('answer')} is outside options")
        for option in options:
            value = option.get("vietnamese", "")
            if not value.strip():
                errors.append(f"{label}: blank Vietnamese option")
            if re.search(r"(?:CHƯƠNG [IVX]+|\s\d{1,3})$", value):
                errors.append(f"{label}: leaked chapter/page marker in option: {value[-60:]}")
            if not option.get("english", "").strip():
                english_errors.append(f"{label}: missing English option {option.get('index')}")
        if not q.get("english", "").strip():
            english_errors.append(f"{label}: missing English question")
        if not q.get("category_english", "").strip():
            english_errors.append(f"{label}: missing English category")

        images = q.get("images")
        if not isinstance(images, list):
            errors.append(f"{label}: images must be an array")
            images = []
        if images:
            image_question_count += 1
        if q.get("image") != (images[0] if images else None):
            errors.append(f"{label}: image must equal the first images entry")
        for ordinal, name in enumerate(images, start=1):
            if not isinstance(name, str) or not re.fullmatch(rf"q{position:03d}_img{ordinal}\.(?:jpeg|jpg|png)", name):
                errors.append(f"{label}: invalid or colliding image name {name}")
                continue
            if not (ROOT / "images" / name).is_file():
                errors.append(f"{label}: missing image file {name}")
            all_images.append(name)

    counts = Counter(q.get("category") for q in questions)
    expected_counts = {vi: hi - lo + 1 for lo, hi, vi, _ in CHAPTERS}
    if counts != Counter(expected_counts):
        errors.append(f"chapter counts differ from source: {dict(counts)}")
    if (len(all_images), image_question_count) != (319, 318):
        errors.append(f"expected 319 image objects across 318 questions; got {len(all_images)} across {image_question_count}")
    if len(set(all_images)) != len(all_images):
        errors.append("image references collide")
    if len(questions) >= 362 and len(questions[361].get("images", [])) != 2:
        errors.append("question 362 should contain both sign images")
    if require_english:
        errors.extend(english_errors)
    return questions, errors, english_errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-english", action="store_true")
    args = parser.parse_args()
    questions, errors, missing_english = validate(args.require_english)
    if errors:
        for error in errors[:40]:
            print("ERROR:", error)
        raise SystemExit(f"Validation failed: {len(errors)} errors")
    print(f"Validated {len(questions)} questions, 6 chapter counts, 319 images, answers, and JS parity.")
    if missing_english:
        print(f"English translation entries still missing: {len(missing_english)} (use --require-english to enforce).")
