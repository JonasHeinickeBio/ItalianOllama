#!/usr/bin/env python3
"""
Extract Italian vocabulary from all telc PDFs using table detection.
Extracts vocabulary from all 6 PDFs: A1.1, A1.2, A2.1, A2.2, B1.1, B1.2
"""

import json
import re
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Please install pdfplumber: pip install pdfplumber")
    exit(1)


def determine_italian_article(word: str) -> str:
    """Determine Italian article based on word ending."""
    if not word:
        return ""
    
    word_lower = word.lower().strip()
    
    # Check for articles already present in the word
    if word_lower.startswith(("il ", "la ", "l'", "lo ", "i ", "le ", "gli ")):
        article_match = re.match(r'^(il |la |l\'|lo |i |le |gli )(.+)', word_lower)
        if article_match:
            return article_match.group(1).strip()
    
    vowels = "aeiou"
    
    # Check for vowels
    if word_lower[0] in vowels:
        return "l'"
    
    # Guess gender based on ending
    gender = ""
    if word_lower.endswith("one") or word_lower.endswith("atore") or word_lower.endswith("otto"):
        gender = "m"
    elif word_lower.endswith("onna") or word_lower.endswith("atrice") or word_lower.endswith("ità"):
        gender = "f"
    elif word_lower.endswith("a"):
        gender = "f"
    elif word_lower.endswith("o"):
        gender = "m"
    elif word_lower.endswith("i"):
        gender = "m"
    elif word_lower.endswith("e"):
        gender = "n"
    
    # Determine article based on gender and first letter
    if gender == "m":
        if word_lower[0] in "sz":
            return "lo"
        elif word_lower[0] in "gh":
            return "il"
        elif word_lower[0] in "bcdfjlmnpqrstvwxyz":
            return "lo"
        else:
            return "il"
    else:
        return "la"


def extract_vocabulary_from_pdf(pdf_path):
    """Extract vocabulary entries from a telc PDF using table detection."""
    print(f"Processing: {pdf_path}")
    
    # Find CEFR level from filename (handle various formats with underscores)
    level_match = re.search(r'Auf_jeden_Fall_+([A12B.]+)', pdf_path)
    cefr_level = level_match.group(1) if level_match else 'unknown'
    
    # Extract section title from filename
    section_match = re.search(r'Wortschatzliste', pdf_path)
    section_name = 'general' if section_match else 'unknown'
    
    vocabulary = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Try to extract tables
            tables = page.extract_tables()
            
            for table in tables:
                # Process table rows
                for row in table[1:]:  # Skip header
                    if len(row) >= 4:
                        # Columns: Article, German, Plural, Italian/Translation, Example
                        german = row[1].strip() if row[1] else ''
                        italian = row[3].strip() if row[3] else ''
                        
                        # Only add if both have content
                        if german and italian and len(german) > 1 and len(italian) > 1:
                            # Skip if looks like header or example content
                            skip_patterns = ['wortschatz', 'beispielsatz', 'artikel', 'plural', 
                                           'traduzione', 'übersetzung', 'beispielsatz']
                            if any(skip in german.lower() for skip in skip_patterns):
                                continue
                            if any(skip in italian.lower() for skip in skip_patterns):
                                continue
                            
                            # Extract article from Italian word directly
                            article = determine_italian_article(italian)
                            
                            # Determine part of speech
                            pos = 'noun'
                            if any(italian.lower().endswith(x) for x in ['are', 'ere', 'ire', 're']):
                                pos = 'verb'
                            elif any(italian.lower().endswith(x) for x in ['oso', 'osa', 'ico', 'ica', 'e']):
                                pos = 'adjective'
                            
                            vocabulary.append({
                                'italian_word': italian,
                                'german_word': german,
                                'cefr_level': cefr_level,
                                'topic': section_name,
                                'part_of_speech': pos,
                                'article': article
                            })
                            print(f"  Found: {german} -> {italian} [{article}] ({pos})")
    
    return vocabulary


def main():
    """Main function to extract vocabulary from all PDFs."""
    data_dir = Path('/home/jhe24/ItalianOllama/data')
    pdf_files = sorted(data_dir.glob('*.pdf'))
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    all_vocabulary = []
    
    for pdf_path in pdf_files:
        try:
            vocab = extract_vocabulary_from_pdf(str(pdf_path))
            all_vocabulary.extend(vocab)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            import traceback
            traceback.print_exc()
    
    # Remove exact duplicates (same Italian word + CEFR level)
    seen = set()
    unique_vocabulary = []
    for item in all_vocabulary:
        key = (item['italian_word'].lower(), item['cefr_level'])
        if key not in seen:
            seen.add(key)
            unique_vocabulary.append(item)
    
    # Save to JSON
    output_file = data_dir / 'vocabulary_extracted.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_vocabulary, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Extracted {len(unique_vocabulary)} unique vocabulary items")
    print(f"Saved to: {output_file}")
    print(f"{'='*60}")
    
    # Print summary by CEFR level
    levels = {}
    for item in unique_vocabulary:
        level = item['cefr_level']
        levels[level] = levels.get(level, 0) + 1
    
    print("\nSummary by CEFR level:")
    for level in sorted(levels.keys()):
        print(f"  {level}: {levels[level]} words")
    
    print(f"\nTotal: {sum(levels.values())} words extracted")


if __name__ == '__main__':
    main()
