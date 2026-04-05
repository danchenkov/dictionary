import json
import random
import requests
import anthropic

from config import ANTHROPIC_API_KEY


client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def get_related_words(word, max_results=10):
    url = f"https://api.datamuse.com/words?ml={word}&max={max_results}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        return [item["word"] for item in data if "word" in item]

    except Exception as error:
        print(f"Could not fetch related words for '{word}': {error}")

    return []


def get_definition_for_related_word(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        meanings = data[0].get("meanings", [])

        for meaning in meanings:
            definitions = meaning.get("definitions", [])
            if definitions:
                return definitions[0].get("definition")

    except Exception:
        return None

    return None


def get_free_distractor_definitions(correct_word, correct_definition, count=4):
    related_words = get_related_words(correct_word)

    distractor_definitions = []

    for word in related_words:
        if word.lower() == correct_word.lower():
            continue

        definition = get_definition_for_related_word(word)

        if not definition:
            continue

        if definition.lower() == correct_definition.lower():
            continue

        distractor_definitions.append(definition)

        if len(distractor_definitions) >= count:
            break

    return distractor_definitions


def get_ai_distractor_definitions(correct_word, correct_definition, count=4):
    prompt = f"""
Word: {correct_word}
Correct definition: {correct_definition}

Generate {count} incorrect but believable dictionary-style definitions.
Requirements:
- They must not match the real meaning
- They should sound realistic
- They should be short
- Return only a JSON array of strings
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            temperature=0.8,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text = response.content[0].text.strip()
        return json.loads(text)

    except Exception as error:
        print(f"Could not generate AI distractors for '{correct_word}': {error}")
        return []


def get_distractor_definitions(correct_word, correct_definition, count=4):
    distractors = get_free_distractor_definitions(
        correct_word,
        correct_definition,
        count=count
    )

    if len(distractors) < count:
        ai_distractors = get_ai_distractor_definitions(
            correct_word,
            correct_definition,
            count=count - len(distractors)
        )

        distractors.extend(ai_distractors)

    random.shuffle(distractors)
    return distractors[:count]