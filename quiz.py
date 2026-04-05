import random


def build_word_to_definition_question(word, correct_definition, distractors):
    choices = distractors + [correct_definition]
    random.shuffle(choices)

    lines = []
    lines.append(f"Word: {word}")
    lines.append("Choose the correct definition:")
    lines.append("")

    for index, choice in enumerate(choices, start=1):
        lines.append(f"{index}. {choice}")

    answer_index = choices.index(correct_definition) + 1

    lines.append("")
    lines.append(f"Correct answer: {answer_index}")

    return "\n".join(lines)


def build_definition_to_word_question(correct_word, definition, distractor_words):
    choices = distractor_words + [correct_word]
    random.shuffle(choices)

    lines = []
    lines.append(f"Definition: {definition}")
    lines.append("Choose the correct word:")
    lines.append("")

    for index, choice in enumerate(choices, start=1):
        lines.append(f"{index}. {choice}")

    answer_index = choices.index(correct_word) + 1

    lines.append("")
    lines.append(f"Correct answer: {answer_index}")

    return "\n".join(lines)