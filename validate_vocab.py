"""Check the curated vocabulary deck against the 600-question source."""

import json
import re
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MINIMUM_BY_CATEGORY = {
    "Vehicle Systems & Maintenance": 30,
    "Signs & Signals": 35,
    "Fire Safety & Rescue": 10,
    "Traffic Scenarios": 8,
}


def load_vocab():
    script = (
        "global.window={};"
        f"require({json.dumps(str(ROOT / 'driving-vocab.js'))});"
        "process.stdout.write(JSON.stringify(window.__DRIVING_VOCAB__ || []));"
    )
    result = subprocess.run(
        ["node", "-e", script], check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return json.loads(result.stdout)


def normalized(value):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or ""))).strip().casefold()


def main():
    vocab = load_vocab()
    questions = json.loads((ROOT / "questions.json").read_text(encoding="utf-8"))
    full_bank = len(questions) == 600
    by_number = {q.get("number", q.get("id")): q for q in questions}
    categories = Counter()
    seen = set()
    errors = []

    if len(vocab) < 150:
        errors.append(f"Only {len(vocab)} vocabulary entries; expected at least 150")

    for index, term in enumerate(vocab, 1):
        label = f"entry {index}"
        for field in ("category", "vietnamese", "english"):
            if not isinstance(term.get(field), str) or not term[field].strip():
                errors.append(f"{label}: missing {field}")
        if any(field not in term for field in ("category", "vietnamese", "english")):
            continue
        categories[term["category"]] += 1
        vietnamese_key = normalized(term["vietnamese"])
        if vietnamese_key in seen:
            errors.append(f"{label}: duplicate Vietnamese term {term['vietnamese']!r}")
        seen.add(vietnamese_key)
        if len(vietnamese_key) < 3:
            errors.append(f"{label}: term too short to be useful")
        for field in ("vietnameseAlternatives", "englishAlternatives"):
            if field in term and (
                not isinstance(term[field], list)
                or any(not isinstance(item, str) or not item.strip() for item in term[field])
            ):
                errors.append(f"{label}: {field} must contain nonempty strings")

        source_id = term.get("sourceQuestionId")
        if source_id is None:
            continue
        if type(source_id) is not int or not 1 <= source_id <= 600:
            errors.append(f"{label}: invalid sourceQuestionId {source_id!r}")
            continue
        if not full_bank:
            continue
        question = by_number.get(source_id)
        if question is None:
            errors.append(f"{label}: question {source_id} is absent")
            continue
        source_text = " ".join(
            [question.get("vietnamese", "")]
            + [option.get("vietnamese", "") for option in question.get("options", [])]
        )
        if vietnamese_key not in normalized(source_text):
            errors.append(
                f"{label}: {term['vietnamese']!r} not found in cited question {source_id}"
            )

    for category, minimum in MINIMUM_BY_CATEGORY.items():
        if categories[category] < minimum:
            errors.append(f"{category}: {categories[category]} entries; expected at least {minimum}")

    if errors:
        raise SystemExit("Vocabulary validation failed:\n" + "\n".join(errors))
    print(f"Validated {len(vocab)} terms in {len(categories)} categories.")
    print("Category counts:", ", ".join(f"{name} {count}" for name, count in sorted(categories.items())))
    if not full_bank:
        print(f"Source term matching deferred: questions.json currently has {len(questions)} questions.")


if __name__ == "__main__":
    main()
