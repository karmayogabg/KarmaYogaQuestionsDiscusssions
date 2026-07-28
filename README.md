# Legacy Font Decoder Guide (Bhagavad Gita PDF)

This directory contains resources for reading and decoding legacy font encodings used in the Bhagavad Gita PDF.

## Legacy Encodings Used

1. **Sanskrit Verses**: Encoded in **Kruti Dev 010** (a legacy Devanagari font).
   - Maps standard English ASCII characters to Devanagari glyphs.
   - For example, `T;k;lh` -> `ज्यायसी` (jyāyasī).
2. **Tamil Commentary & Transliteration**: Encoded in **Shreelipi** (a legacy Tamil font).
   - Maps standard English ASCII characters and some high-ASCII symbols to Tamil glyphs.
   - For example, `Az¯õ¯®` -> `அத்தியாயம்` (chapter).

## Decoding Pipeline

Decoding legacy font encodings requires:
1. **Pre-replacements**: Correcting single-glyph representations and symbol variations.
2. **Key-Value Dictionary Translations**: Translating the legacy character combinations to standard Unicode.

### 1. Tamil (Shreelipi) Pre-Replacements

| Legacy character | Replacement | Target Unicode | Rationale |
| :--- | :--- | :--- | :--- |
| `Ù` | `Óõ` | `றா` | Replaces the single-glyph representation of `ற` + `ா` |
| `à` | `Úõ` | `னா` | Replaces the single-glyph representation of `ன` + `ா` |
| `û` | `Ú` | `ன` | Standardizes the letter `ன` |
| `ù` | `ø` | `ை` | Standardizes the `ai` vowel sign (which differs for `ன`, `ல`, `ள`, `ண`) |
| `μ` (U+03BC) | `µ` (U+00B5) | `ர` | Corrects the Greek lowercase mu to the micro sign used in mapping keys |
| `†` | `é` | `ஸ` | Corrects the letter `ஸ` |

### 2. Preserving English Terminology

Since Shreelipi maps English keys directly to Tamil glyphs, any actual English words in the text (like *Introvert*, *Extrovert*, *serious*, etc.) will become garbled during translation.
- **Solution**: Identify known English words, substitute them with temporary digit-based placeholders (e.g. `999990999`), run the conversion, and then restore them.

## Decoders Scripts Location

The Python translation scripts are stored in the scratch folder:
- **Sanskrit Decoder**: `/home/sabrisatharamanathan/.gemini/antigravity-cli/brain/748cb54b-347f-48c3-8943-bb0594c95f85/scratch/krutidev2unicode.py`
- **Tamil Mapping Dictionary**: `/home/sabrisatharamanathan/.gemini/antigravity-cli/brain/748cb54b-347f-48c3-8943-bb0594c95f85/scratch/encode2utf8.py`
- **Tamil Decoder Module**: `/home/sabrisatharamanathan/.gemini/antigravity-cli/brain/748cb54b-347f-48c3-8943-bb0594c95f85/scratch/encode2unicode.py`
- **Extraction & Execution Script**: `/home/sabrisatharamanathan/.gemini/antigravity-cli/brain/748cb54b-347f-48c3-8943-bb0594c95f85/scratch/parse_gita_v2.py`
