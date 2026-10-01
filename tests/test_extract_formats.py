"""Extraction tests for PDF, EPUB, and plain text. Does not load a TTS model."""

import tempfile
import unittest
from pathlib import Path

from ebooklib import epub
from pypdf import PdfWriter

from PDF_to_Audiobook import SUPPORTED_INPUT_EXTENSIONS, AudiobookConverter, _html_to_text


class ExtractFormatTests(unittest.TestCase):
    def setUp(self):
        self.converter = AudiobookConverter(config_path="missing-pyproject.toml")

    def test_supported_extensions(self):
        self.assertEqual(
            SUPPORTED_INPUT_EXTENSIONS,
            {".pdf", ".epub", ".txt", ".text", ".md"},
        )

    def test_plain_text_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("chapter.txt", "notes.text", "draft.md"):
                path = root / name
                path.write_text("Hello from the source.\n\nSecond paragraph.", encoding="utf-8")
                self.converter.pdf_path = str(path)
                text = self.converter._extract_text()
                self.assertIn("Hello from the source.", text)
                self.assertIn("Second paragraph.", text)

    def test_utf16_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wide.txt"
            path.write_text("Plain text line.", encoding="utf-16")
            self.converter.pdf_path = str(path)
            self.assertIn("Plain text line.", self.converter._extract_text())

    def test_epub_skips_nav_and_keeps_chapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.epub"
            book = epub.EpubBook()
            book.set_identifier("test-book")
            book.set_title("Sample")
            book.set_language("en")
            chapter = epub.EpubHtml(title="One", file_name="chapter1.xhtml", lang="en")
            chapter.content = "<h1>Chapter One</h1><p>The quick brown fox.</p><script>ignore()</script>"
            nav = epub.EpubHtml(title="Nav", file_name="nav.xhtml", lang="en")
            nav.content = "<p>Table of contents should not be narrated.</p>"
            book.add_item(chapter)
            book.add_item(nav)
            book.spine = ["nav", chapter]
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            epub.write_epub(str(path), book)

            self.converter.pdf_path = str(path)
            text = self.converter._extract_text()
            self.assertIn("Chapter One", text)
            self.assertIn("The quick brown fox.", text)
            self.assertNotIn("should not be narrated", text)
            self.assertNotIn("ignore()", text)

    def test_html_helper(self):
        self.assertEqual(_html_to_text("<p>A &amp; B</p>"), "A & B")

    def test_rejects_unknown_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.docx"
            path.write_text("nope", encoding="utf-8")
            self.converter.pdf_path = str(path)
            with self.assertRaises(ValueError):
                self.converter._extract_text()

    def test_pdf_roundtrip_does_not_crash(self):
        # pypdf can write an empty page; extraction should return a string, not raise.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            with path.open("wb") as handle:
                writer.write(handle)
            self.converter.pdf_path = str(path)
            self.assertIsInstance(self.converter._extract_text(), str)

    def test_output_extension_guard(self):
        with self.assertRaises(ValueError):
            self.converter.output_path = "book.ogg"
            # Call only the suffix check by simulating the save branch.
            suffix = Path(self.converter.output_path).suffix.lower()
            from PDF_to_Audiobook import SUPPORTED_OUTPUT_EXTENSIONS
            if suffix not in SUPPORTED_OUTPUT_EXTENSIONS:
                raise ValueError(f"Unsupported output format '{suffix}'. Use .wav or .mp3.")


if __name__ == "__main__":
    unittest.main()
