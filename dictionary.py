import requests

def get_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        # Take the first available definition
        meanings = data[0].get("meanings", [])

        for meaning in meanings:
            definitions = meaning.get("definitions", [])
            if definitions:
                return definitions[0].get("definition")

    except Exception as e:
        print(f"Error fetching definition for {word}: {e}")

    return None