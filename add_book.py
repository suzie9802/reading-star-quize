#!/usr/bin/env python3
"""
add_book.py — add a new book (with 5 AR-style questions) to books.json

Usage
  python3 add_book.py                    # interactive: type the answers in
  python3 add_book.py --file new.json    # import a prepared JSON file
  python3 add_book.py --list             # show books already in books.json
  python3 add_book.py --check            # validate books.json only

After it writes books.json, the site updates as soon as the change is pushed:

  git add -A && git commit -m "Add <book title>" && git push

A prepared JSON file looks exactly like one entry of books.json:

{
  "title": "Mercy Watson to the Rescue",
  "author": "Kate DiCamillo",
  "series": "Mercy Watson",
  "cover": "covers/mercy-watson.jpg",
  "ar": { "bl": 2.7, "points": 0.5, "quiz": 88160, "interest": "LG" },
  "sticker": { "emoji": "🐷", "name": "Porcine Pal", "bg": "linear-gradient(135deg,#F59E0B 0%,#F97316 100%)" },
  "questions": [
    { "q": "...?", "options": ["a", "b", "c", "d"], "answer": 0, "explain": "..." }
  ]
}
"""

import argparse
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS_PATH = os.path.join(HERE, "books.json")
QUESTIONS_PER_BOOK = 5
OPTION_COUNT = 4
LETTERS = "ABCD"


# ---------------------------------------------------------------- helpers
def die(msg):
    print("\n  ERROR: " + msg)
    sys.exit(1)


def ask(prompt, default=None, required=True):
    suffix = " [{}]".format(default) if default not in (None, "") else ""
    while True:
        raw = input("{}{}: ".format(prompt, suffix)).strip()
        if raw:
            return raw
        if default not in (None, ""):
            return str(default)
        if not required:
            return ""
        print("  (please type something)")


def ask_number(prompt, default=None, cast=float):
    while True:
        raw = ask(prompt, default)
        try:
            return cast(raw)
        except ValueError:
            print("  (numbers only, please)")


def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "book"


def load_books():
    if not os.path.exists(BOOKS_PATH):
        die("books.json not found next to this script.")
    with open(BOOKS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def save_books(data):
    data["updatedAt"] = date.today().isoformat()
    with open(BOOKS_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


# ---------------------------------------------------------------- validation
def validate_book(book, existing_ids=()):
    problems = []

    for key in ("title", "author", "cover", "ar", "sticker", "questions"):
        if key not in book:
            problems.append("missing field: " + key)
    if problems:
        return problems

    if not book.get("id"):
        book["id"] = slugify(book["title"])
    if book["id"] in existing_ids:
        problems.append('id "{}" already exists'.format(book["id"]))

    cover = book["cover"]
    if not os.path.exists(os.path.join(HERE, cover)):
        problems.append('cover file not found: {} (put the image in the covers/ folder)'.format(cover))

    ar = book["ar"]
    for key in ("bl", "points"):
        try:
            float(ar[key])
        except (KeyError, TypeError, ValueError):
            problems.append("ar.{} must be a number".format(key))
    if "quiz" in ar:
        try:
            int(ar["quiz"])
        except (TypeError, ValueError):
            problems.append("ar.quiz must be a number (AR quiz number)")

    sticker = book["sticker"]
    if not sticker.get("emoji") or not sticker.get("name"):
        problems.append("sticker needs an emoji and a name")
    sticker.setdefault("bg", "linear-gradient(135deg,#5B8DEF 0%,#8F6BFF 100%)")

    qs = book["questions"]
    if len(qs) != QUESTIONS_PER_BOOK:
        problems.append("need exactly {} questions (found {})".format(QUESTIONS_PER_BOOK, len(qs)))
    for i, q in enumerate(qs, start=1):
        label = "question {}".format(i)
        if not str(q.get("q", "")).strip():
            problems.append(label + ": empty question text")
        opts = q.get("options") or []
        if len(opts) != OPTION_COUNT:
            problems.append("{}: need exactly {} options (found {})".format(label, OPTION_COUNT, len(opts)))
        if any(not str(o).strip() for o in opts):
            problems.append(label + ": empty option text")
        if not isinstance(q.get("answer"), int) or not (0 <= q["answer"] < max(1, len(opts))):
            problems.append(label + ": answer must be 0-{} (0 = A)".format(OPTION_COUNT - 1))
        if not str(q.get("explain", "")).strip():
            problems.append(label + ": needs a short English explanation")

    return problems


# ---------------------------------------------------------------- interactive
def build_interactively(existing_ids):
    print("\n--- New book ---")
    title = ask("Book title (English, exactly as on the cover)")
    book = {
        "id": slugify(title),
        "title": title,
        "author": ask("Author"),
        "series": ask("Series (optional)", required=False),
        "cover": "",
        "ar": {},
        "sticker": {},
        "questions": [],
    }

    print("\n--- AR data (check arbookfind.com for the exact numbers) ---")
    book["ar"]["bl"] = ask_number("AR Book Level (BL), e.g. 3.9")
    book["ar"]["points"] = ask_number("AR Points, e.g. 1.0")
    book["ar"]["quiz"] = ask_number("AR quiz number (optional but nice)", cast=int) if ask(
        "Do you have the AR quiz number? (y/n)", "n").lower().startswith("y") else None

    print("\n--- Cover ---")
    print("  Copy the cover image into the covers/ folder first, then type its name.")
    book["cover"] = "covers/" + ask("Cover file name (e.g. stanley-in-space.jpg)")

    print("\n--- Sticker (given when the reader scores 4/5 or more) ---")
    book["sticker"]["emoji"] = ask("Sticker emoji (e.g. 🚀)")
    book["sticker"]["name"] = ask("Sticker name (e.g. Rocket Reader)")

    print("\n--- {} questions in English ---".format(QUESTIONS_PER_BOOK))
    for i in range(1, QUESTIONS_PER_BOOK + 1):
        print("\nQ{}".format(i))
        q = {"q": ask("Question"), "options": [], "answer": 0, "explain": ""}
        for j in range(OPTION_COUNT):
            q["options"].append(ask("  Option {} ({})".format(j + 1, LETTERS[j])))
        while True:
            letter = ask("  Correct answer (A/B/C/D)", "A").upper()
            if letter in LETTERS[:OPTION_COUNT]:
                q["answer"] = LETTERS.index(letter)
                break
            print("  (type A, B, C or D)")
        q["explain"] = ask("  Short English explanation (shown after answering)")
        book["questions"].append(q)

    if book["ar"].get("quiz") is None:
        book["ar"].pop("quiz", None)
    if not book.get("series"):
        book.pop("series", None)
    return book


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Add a book to books.json")
    ap.add_argument("--file", help="path to a JSON file holding one book object")
    ap.add_argument("--list", action="store_true", help="list books already in books.json")
    ap.add_argument("--check", action="store_true", help="validate books.json without changing it")
    args = ap.parse_args()

    data = load_books()
    existing_ids = [b.get("id") for b in data.get("books", [])]

    if args.list:
        for b in data.get("books", []):
            print("{:<24} {:<34} AR {} · {} pts".format(
                b.get("id", "?"), b.get("title", "?"), b["ar"]["bl"], b["ar"]["points"]))
        return

    if args.check:
        ok = True
        for b in data.get("books", []):
            problems = validate_book(dict(b), [i for i in existing_ids if i != b.get("id")])
            if problems:
                ok = False
                print("FAIL", b.get("title"))
                for p in problems:
                    print("   -", p)
        print("books.json looks good." if ok else "books.json has problems.")
        return

    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            book = json.load(fh)
        if "books" in book:  # allow a full file with a single book
            book = book["books"][0]
    else:
        book = build_interactively(existing_ids)

    problems = validate_book(book, existing_ids)
    if problems:
        print()
        for p in problems:
            print("  - " + p)
        die("this book was not added")

    data.setdefault("books", []).append(book)
    save_books(data)

    print("\nAdded: {} (AR BL {} · {} pts)".format(book["title"], book["ar"]["bl"], book["ar"]["points"]))
    print("books.json now holds {} books.".format(len(data["books"])))
    print("\nPublish it with:")
    print('  git add -A && git commit -m "Add {}" && git push'.format(book["title"]))


if __name__ == "__main__":
    main()
