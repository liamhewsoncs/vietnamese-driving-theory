# Lái Lab — Vietnamese Driving Theory Quiz

An offline, bilingual study quiz based on the 2025 Vietnamese 600-question driving theory bank. The app runs entirely in your browser. No account, server, installation, or build step is required.

## Start the quiz

Download `Lai-Lab-v1.0.0.zip` from this repository's Releases page, extract **the whole ZIP**, and open `index.html` in a browser. Keep `questions-data.js`, `driving-vocab.js`, `assets/`, and `images/` beside it. Alternatively, use the GitHub Pages link in the repository's About section when the maintainer has enabled Pages.

For developers, clone this repository and open `index.html` directly. The bundled `questions-data.js` supports browsers that block local JSON fetches. Internet access is not needed for normal quiz use. Your progress and preferences are kept in this browser's local storage, so changing browsers or clearing site data may reset them.

## What is included

- All 600 questions, grouped into six chapters, with source illustrations where needed.
- Vietnamese, English, and bilingual display; answer checking, scoring, and missed-question review.
- Question practice modes, a curated 162-term vocabulary deck, and eight visual themes.
- A self-contained static site suitable for direct opening or GitHub Pages.

`index.html`, `questions-data.js`, `driving-vocab.js`, `assets/`, and `images/` are the files needed to run the quiz. `OFFLINE_README.txt` provides release notes and source cautions for downloaded copies. `questions.json`, `translations_en.json`, and the Python scripts support data maintenance and validation.

## Accuracy and source

This is an independent study aid, **not an official licensing app**. The Vietnamese question bank originates from the Cục Cảnh sát giao thông (CSGT) document linked in [SOURCE_DATA.md](docs/SOURCE_DATA.md). The official PDF is intentionally not included in this repository or the download ZIP. Many English strings began as machine translation and have not received expert legal or technical review. Check the current official Vietnamese source for authoritative wording, answers, and exam rules.

The quiz checks answers against the source answer key but does not provide rule explanations. The source data has 319 illustration objects across 318 questions. Question 362 uses two separate images.

## Rebuild and check the data

Install Python and Node.js. Download the official PDF as described in [SOURCE_DATA.md](docs/SOURCE_DATA.md), then run from this folder:

```powershell
python -m pip install -r requirements.txt
python extract_questions.py
python validate_questions.py --require-english
python validate_vocab.py
```

`extract_questions.py` writes `questions.json`, `questions-data.js`, and extracted images. The supplied English translation cache is used during extraction. If translations need work, run `python translate_questions.py` and validate again; this optional step uses an online translation service. Review its output before publication. `python export_anki_vocab.py` creates optional Anki/TSV exports after the dependencies are installed.

For repository upload, GitHub Pages, and downloadable ZIP instructions, see [GITHUB_UPLOAD.md](docs/GITHUB_UPLOAD.md). No installer is needed for this browser app.
