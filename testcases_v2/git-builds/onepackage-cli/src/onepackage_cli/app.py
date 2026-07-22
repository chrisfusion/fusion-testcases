import argparse
import datetime
import os


def main() -> None:
    parser = argparse.ArgumentParser(prog="onepackage-cli")
    parser.add_argument("--name", default=os.environ.get("TARGET_NAME", "world"))
    args = parser.parse_args()

    print(f"[{datetime.datetime.now().isoformat()}] hello, {args.name} — installed as a real console command")


if __name__ == "__main__":
    main()
