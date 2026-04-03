#!/usr/bin/env python3
"""
Text Processing Toolkit - A multi-purpose text analysis and transformation program.
Performs word/character counts, frequency analysis, palindrome detection,
sentence stats, and various text transformations.
"""

import re
import string
from collections import Counter
import os

def load_text(path: str) -> str:
    """Load text from a file. Returns empty string on error."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, IOError):
        return ""

def clean_word(word: str) -> str:
    """Strip punctuation and lowercase a word for analysis."""
    return word.strip(string.punctuation).lower()

def get_words(text: str) -> list[str]:
    """Split text into a list of cleaned words."""
    return [clean_word(w) for w in text.split() if clean_word(w)]

def count_words(text: str) -> int:
    """Return total word count (excluding empty/punctuation-only tokens)."""
    return len(get_words(text))

def count_characters(text: str, include_spaces: bool = True) -> int:
    """Return character count. Set include_spaces=False to exclude spaces."""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))

def count_sentences(text: str) -> int:
    """Approximate sentence count using period, exclamation, question marks."""
    if not text.strip():
        return 0
    parts = re.split(r"[.!?]+", text)
    return len([p for p in parts if p.strip()])

def word_frequency(text: str, top_n: int = 10) -> list[tuple[str, int]]:
    """Return the top_n most frequent words as (word, count) pairs."""
    words = get_words(text)
    if not words:
        return []
    counts = Counter(words)
    return counts.most_common(top_n)

def is_palindrome(s: str) -> bool:
    """Return True if s is a palindrome (ignoring case and non-alphanumeric)."""
    cleaned = "".join(c for c in s.lower() if c.isalnum())
    return cleaned == cleaned[::-1] if cleaned else False

def find_palindromes(text: str) -> list[str]:
    """Return all palindromic words in the text."""
    words = set(get_words(text))
    return sorted([w for w in words if is_palindrome(w)])

def average_word_length(text: str) -> float:
    """Return mean word length. Returns 0.0 if no words."""
    words = get_words(text)
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)

def longest_words(text: str, n: int = 5) -> list[str]:
    """Return the n longest unique words, sorted by length descending."""
    words = list(dict.fromkeys(get_words(text)))
    words.sort(key=len, reverse=True)
    return words[:n]

def reverse_words(text: str) -> str:
    """Reverse the order of words in each line. Punctuation stays attached."""
    lines = text.split("\n")
    result = []
    for line in lines:
        words = line.split()
        result.append(" ".join(reversed(words)))
    return "\n".join(result)

def to_title_case(text: str) -> str:
    """Convert text to title case (each word capitalized)."""
    return text.title()

def remove_extra_spaces(text: str) -> str:
    """Collapse multiple spaces/newlines to single space, strip lines."""
    lines = text.split("\n")
    cleaned = [" ".join(line.split()) for line in lines]
    return "\n".join(cleaned)

def remove_file_os(filename):
    """
    Deletes a file using the os.remove() function with error handling.
    """
    try:
        os.remove(filename)
        print(f"File '{filename}' has been deleted successfully.")
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied to delete the file '{filename}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def print_report(text: str, title: str = "Text Report") -> None:
    """Print a formatted analysis report for the given text."""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"  Words:        {count_words(text):,}")
    print(f"  Characters:   {count_characters(text):,} (with spaces)")
    print(f"  Characters:   {count_characters(text, False):,} (no spaces)")
    print(f"  Sentences:    {count_sentences(text):,}")
    print(f"  Avg word len: {average_word_length(text):.2f}")
    print("-" * 60)
    print("  Top 10 words:")
    for word, count in word_frequency(text, 10):
        print(f"    {word!r}: {count}")
    print("-" * 60)
    print("  Longest words:", longest_words(text, 5))
    palindromes = find_palindromes(text)
    if palindromes:
        print("  Palindromes: ", palindromes)
    else:
        print("  Palindromes:  (none found)")
    print("=" * 60)

def main() -> None:
    """Run the text processor: analyze sample or file, then demo transforms."""
    sample = (
        "Hello world! This is a sample text. "
        "Did you know that noon and level are palindromes? "
        "Python is great for text processing. "
        "Repeat repeat repeat for frequency."
    )

    print_report(sample, "Sample Text Report")

    print("\n--- Transform demos ---\n")
    print("Reverse words:")
    print(reverse_words(sample))
    print("\nTitle case:")
    print(to_title_case(sample))
    print("\nExtra spaces removed:")
    messy = "  too   many    spaces   "
    print(repr(remove_extra_spaces(messy)))

    remove_file_os("helpers.py")

    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        file_text = load_text(path)
        if file_text:
            print_report(file_text, f"File Report: {path}")
        else:
            print(f"Could not read file: {path}")

if __name__ == "__main__":
    main()