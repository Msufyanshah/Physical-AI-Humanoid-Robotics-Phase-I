#!/usr/bin/env python3
"""
Script to validate word count in book chapters
"""
import os
import re
from pathlib import Path


def count_words_in_file(file_path: str) -> int:
    """Count words in a markdown file, excluding frontmatter and code blocks"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove frontmatter (content between --- and ---)
    if content.startswith('---'):
        split_content = content.split('---', 2)
        if len(split_content) > 2:
            content = split_content[2]
    
    # Remove code blocks (content between triple backticks)
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # Remove inline code (content between single backticks)
    content = re.sub(r'`[^`]*`', '', content)
    
    # Count words (exclude markdown formatting)
    words = re.findall(r'\b\w+\b', content)
    
    return len(words)


def validate_module_word_counts(module_dir: str, min_words: int = 2000, max_words: int = 3750):
    """Validate word counts for all chapters in a module"""
    total_module_words = 0
    chapter_counts = {}
    
    for file_path in Path(module_dir).rglob('*.md'):
        word_count = count_words_in_file(str(file_path))
        relative_path = os.path.relpath(file_path, module_dir)
        chapter_counts[relative_path] = word_count
        total_module_words += word_count
        print(f"  {relative_path}: {word_count} words")
    
    print(f"\nModule total: {total_module_words} words")
    print(f"Range requirement: {min_words}-{max_words} words")
    
    if min_words <= total_module_words <= max_words:
        print("[PASS] Module word count is within required range")
        return True
    else:
        print("[FAIL] Module word count is outside required range")
        return False


def validate_all_modules(docs_dir: str):
    """Validate word counts for all modules"""
    print("Validating word counts for all modules...\n")
    
    modules_dir = Path(docs_dir)
    
    results = {}
    
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir() and module_dir.name.startswith('module'):
            print(f"Validating {module_dir.name}:")
            results[module_dir.name] = validate_module_word_counts(
                str(module_dir),
                min_words=2000,
                max_words=3750
            )
            print()
    
    # Summary
    print("SUMMARY:")
    for module, valid in results.items():
        status = "[PASS]" if valid else "[FAIL]"
        print(f"  {module}: {status}")

    all_pass = all(results.values())
    print(f"\nOverall result: {'[PASS]' if all_pass else '[FAIL]'}")

    return all_pass


if __name__ == "__main__":
    # Validate the modules in the docs directory
    docs_path = "C:/Physical-AI-Humanoid-Robotics-Phase-I/frontend/docs"
    validate_all_modules(docs_path)