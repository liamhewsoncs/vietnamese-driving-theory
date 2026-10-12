import csv
import html
import json
import re
import subprocess
from pathlib import Path

try:
    import genanki
except ImportError as exc:
    raise SystemExit(
        "The genanki package is required to build the .apkg deck. "
        "Install it with: python -m pip install genanki"
    ) from exc


ROOT = Path(__file__).resolve().parent
VOCAB_JS = ROOT / "driving-vocab.js"
QUESTIONS_JSON = ROOT / "questions.json"
APKG_OUT = ROOT / "Vietnamese_Driving_Test_Vocabulary.apkg"
TSV_OUT = ROOT / "Vietnamese_Driving_Test_Vocabulary.tsv"


def load_vocab():
    script = (
        "global.window={};"
        f"require({json.dumps(str(VOCAB_JS))});"
        "process.stdout.write(JSON.stringify(window.__DRIVING_VOCAB__ || []));"
    )
    result = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def load_questions():
    with QUESTIONS_JSON.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def text_matches(needle, haystack):
    return clean(needle).casefold() in clean(haystack).casefold()


def question_number(question):
    return question.get("number") or question.get("id")


def example_in_question(vietnamese, question):
    if text_matches(vietnamese, question.get("vietnamese")):
        return clean(question.get("vietnamese")), clean(question.get("english"))

    for option in question.get("options", []):
        if text_matches(vietnamese, option.get("vietnamese")):
            return clean(option.get("vietnamese")), clean(option.get("english"))

    return None


def find_example(term, questions):
    vietnamese = term["vietnamese"]
    source_id = term.get("sourceQuestionId")

    if source_id is not None:
        question = next((q for q in questions if question_number(q) == source_id), None)
        if question is None:
            raise ValueError(f"Vocabulary term {vietnamese!r} cites absent question {source_id}")
        example = example_in_question(vietnamese, question)
        if example is None:
            # A few terms name something shown only in a question's illustration.
            example = clean(question.get("vietnamese")), clean(question.get("english"))
        return *example, source_id

    for question in questions:
        example = example_in_question(vietnamese, question)
        if example is not None:
            return *example, question_number(question)

    return "", "", None


def join_values(values):
    return " / ".join(clean(value) for value in values or [] if clean(value))


def tagify(value):
    tag = re.sub(r"[^0-9A-Za-z]+", "_", clean(value)).strip("_")
    return tag or "Vocabulary"


def anki_field(value):
    return html.escape(clean(value), quote=False)


def build_model():
    return genanki.Model(
        2056728594,
        "Vietnamese Driving Test Vocabulary Model",
        fields=[
            {"name": "Vietnamese"},
            {"name": "English"},
            {"name": "Category"},
            {"name": "VietnameseAlternatives"},
            {"name": "EnglishAlternatives"},
            {"name": "ExampleVietnamese"},
            {"name": "ExampleEnglish"},
            {"name": "Source"},
        ],
        templates=[
            {
                "name": "Vietnamese to English",
                "qfmt": """
<div class="category">{{Category}}</div>
<div class="prompt-label">Translate to English</div>
<div class="term">{{Vietnamese}}</div>
""",
                "afmt": """
{{FrontSide}}
<hr id="answer">
<div class="answer">{{English}}</div>
{{#EnglishAlternatives}}<div class="detail"><b>Also:</b> {{EnglishAlternatives}}</div>{{/EnglishAlternatives}}
{{#VietnameseAlternatives}}<div class="detail"><b>Vietnamese variants:</b> {{VietnameseAlternatives}}</div>{{/VietnameseAlternatives}}
{{#ExampleVietnamese}}<div class="example"><b>Example:</b> {{ExampleVietnamese}}<br>{{ExampleEnglish}}</div>{{/ExampleVietnamese}}
<div class="source">{{Source}}</div>
""",
            },
            {
                "name": "English to Vietnamese",
                "qfmt": """
<div class="category">{{Category}}</div>
<div class="prompt-label">Translate to Vietnamese</div>
<div class="term">{{English}}</div>
{{#EnglishAlternatives}}<div class="hint">{{EnglishAlternatives}}</div>{{/EnglishAlternatives}}
""",
                "afmt": """
{{FrontSide}}
<hr id="answer">
<div class="answer">{{Vietnamese}}</div>
{{#VietnameseAlternatives}}<div class="detail"><b>Also:</b> {{VietnameseAlternatives}}</div>{{/VietnameseAlternatives}}
{{#ExampleVietnamese}}<div class="example"><b>Example:</b> {{ExampleVietnamese}}<br>{{ExampleEnglish}}</div>{{/ExampleVietnamese}}
<div class="source">{{Source}}</div>
""",
            },
        ],
        css="""
.card {
  background: #fffdf8;
  color: #1f2a2f;
  font-family: Arial, "Segoe UI", sans-serif;
  font-size: 20px;
  line-height: 1.45;
  text-align: center;
}
.category {
  color: #0d6c63;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: .04em;
  margin-bottom: 14px;
  text-transform: uppercase;
}
.prompt-label {
  color: #5f6c70;
  font-size: 15px;
  margin-bottom: 10px;
}
.term {
  font-size: 34px;
  font-weight: 700;
}
.answer {
  color: #b33c2f;
  font-size: 30px;
  font-weight: 700;
  margin: 16px 0;
}
.detail,
.hint,
.example,
.source {
  color: #39474c;
  font-size: 17px;
  margin-top: 12px;
}
.example {
  background: #f4efe3;
  border-radius: 8px;
  padding: 12px;
}
.source {
  color: #728085;
  font-size: 13px;
}
""",
    )


def main():
    vocab = load_vocab()
    questions = load_questions()
    model = build_model()
    deck = genanki.Deck(2056728593, "Vietnamese Driving Test Vocabulary")

    rows = []
    seen = set()

    for term in vocab:
        vietnamese = clean(term.get("vietnamese"))
        english = clean(term.get("english"))
        category = clean(term.get("category")) or "Vocabulary"
        if not vietnamese or not english:
            continue

        key = (vietnamese.casefold(), english.casefold(), category.casefold())
        if key in seen:
            continue
        seen.add(key)

        example_vi, example_en, source_id = find_example(term, questions)
        row = {
            "Vietnamese": vietnamese,
            "English": english,
            "Category": category,
            "VietnameseAlternatives": join_values(term.get("vietnameseAlternatives")),
            "EnglishAlternatives": join_values(term.get("englishAlternatives")),
            "ExampleVietnamese": example_vi,
            "ExampleEnglish": example_en,
            "Source": f"Question {source_id}" if source_id else "600-question study vocabulary",
        }
        rows.append(row)

        deck.add_note(
            genanki.Note(
                model=model,
                fields=[
                    anki_field(row["Vietnamese"]),
                    anki_field(row["English"]),
                    anki_field(row["Category"]),
                    anki_field(row["VietnameseAlternatives"]),
                    anki_field(row["EnglishAlternatives"]),
                    anki_field(row["ExampleVietnamese"]),
                    anki_field(row["ExampleEnglish"]),
                    anki_field(row["Source"]),
                ],
                tags=["VietnameseDriving", tagify(category)],
                guid=genanki.guid_for(row["Vietnamese"], row["English"], row["Category"]),
            )
        )

    genanki.Package(deck).write_to_file(APKG_OUT)

    with TSV_OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} notes and {len(rows) * 2} cards.")
    print(APKG_OUT)
    print(TSV_OUT)


if __name__ == "__main__":
    main()
