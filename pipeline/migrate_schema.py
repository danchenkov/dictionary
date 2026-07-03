from dictionary.yaml_store import load_yaml, save_yaml
from dictionary.schema import migrate_dataset


def main() -> None:
    data = load_yaml()
    migrate_dataset(data)
    save_yaml(data)
    print("Migration complete.")


if __name__ == "__main__":
    main()