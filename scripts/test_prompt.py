import json
import sys

from falcons_qa import generate_answer


QUESTION = "What is the monthly membership fee for Falcons Club?"


def main():
    result = generate_answer(QUESTION)
    print(json.dumps(result, ensure_ascii=False))

    expected_keys = {"answer", "source"}
    if set(result.keys()) != expected_keys:
        raise SystemExit(f"Unexpected keys: {list(result.keys())}")
    if not result["answer"] or not result["source"]:
        raise SystemExit("Answer or source is empty.")

    print("JSON validation passed.")


if __name__ == "__main__":
    main()
