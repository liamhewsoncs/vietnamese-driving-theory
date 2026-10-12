import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_JSON = BASE_DIR / "questions.json"
TRANSLATION_CACHE = BASE_DIR / "translations_en.json"
EXTRACT_SCRIPT = BASE_DIR / "extract_questions.py"
MAX_WORKERS = 4
SAVE_EVERY = 25


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_cache(cache):
    TRANSLATION_CACHE.write_text(
        json.dumps(dict(sorted(cache.items())), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def ensure_questions_exist():
    if QUESTIONS_JSON.exists():
        return
    subprocess.run([sys.executable, str(EXTRACT_SCRIPT)], cwd=BASE_DIR, check=True)


def collect_texts(questions):
    seen = set()
    ordered = []
    for question in questions:
        for text in (
            question.get("category", ""),
            question.get("vietnamese", ""),
            *(option.get("vietnamese", "") for option in question.get("options", [])),
        ):
            text = str(text).strip()
            if text and text not in seen:
                seen.add(text)
                ordered.append(text)
    return ordered


def translate_one(text, retries=3):
    for attempt in range(retries):
        try:
            query = urllib.parse.urlencode(
                {"client": "gtx", "sl": "vi", "tl": "en", "dt": "t", "q": text}
            )
            request = urllib.request.Request(
                f"https://translate.googleapis.com/translate_a/single?{query}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(
                str(segment[0]) for segment in payload[0] if segment and segment[0]
            ).strip()
            if not translated:
                raise ValueError("translation service returned an empty result")
            return translated
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))


def main():
    ensure_questions_exist()

    questions = load_json(QUESTIONS_JSON, [])
    if not questions:
        raise SystemExit("No questions found in questions.json")

    cache = load_json(TRANSLATION_CACHE, {})
    if not isinstance(cache, dict):
        cache = {}
    cache = {str(key): str(value) for key, value in cache.items() if str(value).strip()}

    for question in questions:
        if question.get("english"):
            cache.setdefault(question["vietnamese"], question["english"])
        if question.get("category_english"):
            cache.setdefault(question["category"], question["category_english"])
        for option in question.get("options", []):
            if option.get("english"):
                cache.setdefault(option["vietnamese"], option["english"])

    texts = collect_texts(questions)
    missing = [text for text in texts if not cache.get(text, "").strip()]

    print(f"loaded {len(questions)} questions")
    print(f"cached translations: {len(cache)}")
    print(f"missing translations: {len(missing)}")

    translated_count = 0
    failed = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(translate_one, text): text for text in missing}
        for future in as_completed(futures):
            text = futures[future]
            try:
                translation = future.result()
                cache[text] = str(translation).strip()
                translated_count += 1
                if translated_count % SAVE_EVERY == 0:
                    save_cache(cache)
                    print(f"saved progress: {translated_count}/{len(missing)}")
            except Exception as exc:
                failed.append((text, str(exc)))
                print(f"failed: {text[:80]}")

    save_cache(cache)
    print(f"translated this run: {translated_count}")
    print(f"failed translations: {len(failed)}")

    if failed:
        failed_path = BASE_DIR / "translation_failures.json"
        failed_path.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"saved failures: {failed_path}")

    subprocess.run([sys.executable, str(EXTRACT_SCRIPT)], cwd=BASE_DIR, check=True)


if __name__ == "__main__":
    main()
