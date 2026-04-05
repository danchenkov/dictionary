import random

def build_question(correct_word, definition, distractors):
    choices = distractors + [correct_word]
    random.shuffle(choices)

    lines = []
    lines.append(f"Definition: {definition}")
    lines.append("Which word matches this definition?")
    lines.append("")

    for index, choice in enumerate(choices, start=1):
        lines.append(f"{index}. {choice}")

    answer_index = choices.index(correct_word) + 1
    lines.append("")
    lines.append(f"(Correct answer: {answer_index})")

    return "\n".join(lines)