import sys


def main():
    try:
        from src.main import main as main_entry

        main_entry()
        print("Main service healthcheck: OK")
        sys.exit(0)
    except Exception as e:
        print(f"Main service healthcheck failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
