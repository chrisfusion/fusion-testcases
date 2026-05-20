import os
import sys


def main() -> None:
    import streamlit.web.cli as stcli

    app_path = os.path.join(os.path.dirname(__file__), "internals", "app.py")
    sys.argv = ["streamlit", "run", app_path] + sys.argv[1:]
    stcli.main()


if __name__ == "__main__":
    main()
