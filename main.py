from dictionary import get_definition
from distractors import get_distractors
from quiz import build_question

WORDS = ["abandon", "concise", "obscure"]

for word in WORDS:
    definition = get_definition(word)

    if not definition:
        print(f"Skipping {word}, no definition found.")
        continue

    distractors = get_distractors(word, definition)
    question = build_question(word, definition, distractors)

    print(question)
    print("-" * 60)