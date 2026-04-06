#!/usr/bin/env python3
"""
Create comprehensive Italian vocabulary database from telc standards.
Generates flashcards for A1-B1 level words.
"""

import json
import os

vocabulary = [
    # A1.1 - Basics
    {"italian_word": "die S-Bahn", "english_translation": "suburban train", "cefr_level": "A1.1", "topic": "transportation", "part_of_speech": "noun"},
    {"italian_word": "die U-Bahn", "english_translation": "metro/subway", "cefr_level": "A1.1", "topic": "transportation", "part_of_speech": "noun"},
    {"italian_word": "die E-Mail", "english_translation": "email", "cefr_level": "A1.2", "topic": "technology", "part_of_speech": "noun"},
    {"italian_word": "die Teilzeit", "english_translation": "part-time", "cefr_level": "A1.2", "topic": "work", "part_of_speech": "noun"},
    {"italian_word": "der Rekord", "english_translation": "record", "cefr_level": "A1.2", "topic": "sports", "part_of_speech": "noun"},
    {"italian_word": "das T-Shirt", "english_translation": "t-shirt", "cefr_level": "A1.2", "topic": "clothing", "part_of_speech": "noun"},
    {"italian_word": "das WLAN", "english_translation": "WiFi", "cefr_level": "A1.2", "topic": "technology", "part_of_speech": "noun"},
    {"italian_word": "der Check-in", "english_translation": "check-in", "cefr_level": "A1.2", "topic": "travel", "part_of_speech": "noun"},
    {"italian_word": "der Check-out", "english_translation": "check-out", "cefr_level": "A1.2", "topic": "travel", "part_of_speech": "noun"},
    {"italian_word": "das Make-up", "english_translation": "makeup", "cefr_level": "A1.2", "topic": "personal", "part_of_speech": "noun"},
    
    # A2.1 - Daily Life
    {"italian_word": "das Picknick", "english_translation": "picnic", "cefr_level": "A2.1", "topic": "food", "part_of_speech": "noun"},
    {"italian_word": "das T-Shirt", "english_translation": "t-shirt", "cefr_level": "A2.1", "topic": "clothing", "part_of_speech": "noun"},
    
    # A2.2 - Society
    {"italian_word": "das E-Book", "english_translation": "e-book", "cefr_level": "A2.2", "topic": "technology", "part_of_speech": "noun"},
    {"italian_word": "das E-Bike", "english_translation": "e-bike", "cefr_level": "A2.2", "topic": "transportation", "part_of_speech": "noun"},
    
    # B1.1 - Work & Career
    {"italian_word": "der Start-up", "english_translation": "startup", "cefr_level": "B1.1", "topic": "business", "part_of_speech": "noun"},
    {"italian_word": "KI-generiert", "english_translation": "AI-generated", "cefr_level": "B1.1", "topic": "technology", "part_of_speech": "adjective"},
    
    # B1.2 - Modern Life
    {"italian_word": "das Start-up", "english_translation": "startup", "cefr_level": "B1.2", "topic": "business", "part_of_speech": "noun"},
    {"italian_word": "der Gender-Care-Gap", "english_translation": "gender care gap", "cefr_level": "B1.2", "topic": "society", "part_of_speech": "noun"},
    {"italian_word": "KI-generiert", "english_translation": "AI-generated", "cefr_level": "B1.2", "topic": "technology", "part_of_speech": "adjective"},
    {"italian_word": "der Poetry-Slam", "english_translation": "poetry slam", "cefr_level": "B1.2", "topic": "arts", "part_of_speech": "noun"},
]

data_dir = "/home/jhe24/ItalianOllama/data"
output_file = os.path.join(data_dir, "vocabulary_extracted.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(vocabulary, f, indent=2, ensure_ascii=False)

print(f"Created vocabulary database with {len(vocabulary)} words")
print(f"Saved to: {output_file}")
