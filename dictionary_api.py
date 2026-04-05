import requests


def get_definition(word):
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

    except Exception as error:
        print(f"Could not fetch definition for '{word}': {error}")

    return None