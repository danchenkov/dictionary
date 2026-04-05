from config import QUIZ_MODE
from dictionary_api import get_definition
from distractors import get_distractor_definitions, get_related_words
from quiz import (
    build_word_to_definition_question,
    build_definition_to_word_question,
)
from word_loader import load_words_from_txt


words = load_words_from_txt()

for word in words:
    definition = get_definition(word)

    if not definition:
        print(f"Skipping '{word}' because no definition was found.")
        print("-" * 60)
        continue

    if QUIZ_MODE == "word_to_definition":
        distractors = get_distractor_definitions(word, definition)

        question = build_word_to_definition_question(
            word,
            definition,
            distractors
        )

    elif QUIZ_MODE == "definition_to_word":
        distractors = get_related_words(word, max_results=10)
        distractors = [item for item in distractors if item.lower() != word.lower()]
        distractors = distractors[:4]

        question = build_definition_to_word_question(
            word,
            definition,
            distractors
        )

    else:
        print(f"Unknown quiz mode: {QUIZ_MODE}")
        break

    print(question)
    print("-" * 60)