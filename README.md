# Lái Lab — Vietnamese Driving Theory Quiz

Lái Lab is an offline-friendly, bilingual study quiz based on the 2025
Vietnamese 600-question driving theory bank. It runs entirely in a web browser:
no account, installation, server, or internet connection is required.

## Use the quiz

Everything needed to study is already included. You do **not** need Python,
Node.js, the official PDF, or any of the developer scripts.

### Play online

Use the GitHub Pages website shown in this repository's **About** section. Your
answers and preferences are stored locally in your browser.

### Download for offline use

1. Open this repository's **Releases** page.
2. Download `Lai-Lab-v1.0.0.zip` from the latest release.
3. Extract the entire ZIP file.
4. Open `index.html` in a modern web browser.

Keep all extracted files and folders together. Moving `index.html` away from
`questions-data.js`, `driving-vocab.js`, `assets/`, or `images/` will prevent
parts of the quiz from loading.

## Features

- All 600 questions from the 2025 question bank, organized into six chapters.
- 319 source illustrations across 318 illustrated questions.
- Vietnamese, English, and bilingual display modes.
- Single-question, themed, random, and vocabulary study modes.
- Answer checking, scoring, and missed-question review.
- A curated deck of 162 driving-related vocabulary terms in eight categories.
- Eight visual themes with automatic or manual selection.
- Local-only progress and preference storage.
- Fully offline operation after download.

The quiz identifies the correct choice using the source answer key. It does not
provide explanations of the underlying traffic rules or analyses of the other
choices.

## Privacy

Lái Lab has no user account, analytics, advertising, or cloud database. Quiz
progress and preferences are saved using the browser's local storage. Clearing
browser data, using private browsing, or switching browsers or devices may
reset that progress.

## Accuracy and official source

Lái Lab is an independent study aid, **not an official licensing application**.
The Vietnamese content is based on the 2025 question bank published by the
Cục Cảnh sát giao thông (CSGT).

Many English strings began as machine translations and have not received expert
legal or technical review. Always compare the wording, answers, and current
exam rules with the official Vietnamese material. See
[Official source data](docs/SOURCE_DATA.md) for links to the source bank and
the publisher's guidance.

The official source PDF is intentionally not included in this repository or in
the offline ZIP. Normal users do not need it; it is only required when a
developer wants to regenerate the bundled data.

## Repository contents

| Path | Purpose |
| --- | --- |
| `index.html` | Main quiz application |
| `questions-data.js` | Browser-ready bundled question data |
| `driving-vocab.js` | Bundled vocabulary deck |
| `assets/` | Interface theme artwork |
| `images/` | Question illustrations |
| `questions.json` | Canonical generated question data |
| `translations_en.json` | English translation cache and reviewed corrections |
| `OFFLINE_README.txt` | Instructions and cautions included with the ZIP |
| `extract_questions.py` | Rebuilds question data and illustrations from the source PDF |
| `validate_questions.py` | Checks numbering, answers, images, translations, and bundle parity |
| `validate_vocab.py` | Checks the vocabulary deck |
| `export_anki_vocab.py` | Produces optional Anki and TSV vocabulary exports |

## Optional: rebuild the question data

This section is for developers and maintainers only. It is **not required to
use the quiz**. The repository and release ZIP already contain all questions,
illustrations, translations, vocabulary content, and interface files.

### Requirements

- Python 3
- The official 600-question PDF described in
  [docs/SOURCE_DATA.md](docs/SOURCE_DATA.md)

Save the PDF as:

```text
source/official-600-questions.pdf
```

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Rebuild and validate the question data:

```powershell
python extract_questions.py
python validate_questions.py --require-english
python validate_vocab.py
```

`extract_questions.py` regenerates `questions.json`, `questions-data.js`, and
the question illustrations. It stops instead of publishing when the source
does not produce exactly 600 sequential questions, unique detected answers,
and the expected illustration counts.

To update missing translations, run:

```powershell
python translate_questions.py
python validate_questions.py --require-english
```

Translation output should be reviewed against the Vietnamese source before it
is published. To rebuild the optional vocabulary downloads, run:

```powershell
python export_anki_vocab.py
```

## Validation

The current release passes the included validators with:

- 600 sequential questions across six chapters.
- 319 illustration objects across 318 questions.
- Matching JSON and browser JavaScript data.
- Complete English fields required by the validator.
- 162 vocabulary terms across eight categories.

Validation checks data structure and completeness; it does not replace expert
review of legal wording or translations.

## Publishing

Instructions for pushing the project to GitHub, enabling GitHub Pages, and
attaching the offline ZIP to a release are available in
[GitHub upload instructions](docs/GITHUB_UPLOAD.md).

Because this is a static browser application, it does not need an installer.
