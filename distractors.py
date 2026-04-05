import requests
import random

def get_related_words(word):
    url = f"https://api.datamuse.com/words?ml={word}&max=20"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        return [item["word"] for item in data]

    except Exception as e:
        print(f"Error fetching related words for {word}: {e}")

    return []

def get_distractors(correct_word, definition, count=4):
    related_words = get_related_words(correct_word)

    # Remove the correct answer itself
    filtered = [w for w in related_words if w.lower() != correct_word.lower()]

    random.shuffle(filtered)

    return filtered[:count]