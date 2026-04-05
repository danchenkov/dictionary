import yaml


def load_words_from_txt(filename="words.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def load_words_from_yaml(filename="words.yaml"):
    with open(filename, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)