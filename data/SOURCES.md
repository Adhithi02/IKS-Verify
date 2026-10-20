# Corpus sources

Retrieval date: 2026-10-20

Sanskrit is copied from the cited sources without generation, repair, or paraphrase.

## Bhagavad Gita Sanskrit
- URL: https://github.com/cltk/sanskrit_text_gitasupersite
- License: Public Domain Mark 1.0
- Retrieved: 2026-10-20
- Notes: Public Domain Mark 1.0 — CLTK mirror of Gita Supersite Sanskrit files.

## Bhagavad Gita IAST + English (Purohit as packaged)
- URL: https://github.com/gita/gita
- License: Unlicense (repository packaging)
- Retrieved: 2026-10-20
- Notes: This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.
 English field uses Shri Purohit Swami as distributed in gita/gita. The 1935 translation may still be restricted in some jurisdictions; Sanskrit is public domain.

## Yoga Sutras Sanskrit
- URL: https://github.com/cltk/sanskrit_text_gitasupersite/tree/master/yogasutra
- License: Public Domain Mark 1.0
- Retrieved: 2026-10-20
- Notes: Public Domain Mark 1.0 — yogasutra/*/sutra.txt

## Yoga Sutras English (Charles Johnston, 1912)
- URL: https://www.gutenberg.org/cache/epub/2526/pg2526.txt
- License: Public domain (US): Project Gutenberg ebook 2526, published 1912
- Retrieved: 2026-10-20
- Notes: The Yoga Sutras of Patanjali: The Book of the Spiritual Man, Charles Johnston. Gutenberg license applies to the ebook packaging.

## Manual download required

Upanishads could not be fully downloaded automatically.
Last error: Missing Sanskrit files for: ['Isha', 'Kena', 'Katha', 'Mandukya']
Manual steps:
1. Obtain public-domain Devanagari for Isha (18), Kena (4 khandas: 8/5/12/9), Katha (6 vallis: 29/25/17/15/15/18), Mandukya (12) from a PD/CC source (e.g. sa.wikisource.org pages, or a Public Domain Mark dump).
2. Obtain PD English (Max Müller SBE 1/15, Hume 1921, or Paramananda 1919).
3. Save JSONL lines to data/processed/upanishads.jsonl with fields: text_id, chapter, verse, sanskrit_devanagari, transliteration_iast, english_translation, source, license. Do not generate Sanskrit.
4. Re-run: python scripts/download_sources.py

