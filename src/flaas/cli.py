import argparse

def main() -> None:
    p = argparse.ArgumentParser(prog="flaas")
    p.add_argument("--version", action="store_true")
    args = p.parse_args()
    if args.version:
        print("0.0.1")
        return
    p.print_help()

if __name__ == "__main__":
    main()
