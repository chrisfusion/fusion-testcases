import os
import sys


def main() -> None:
    import internals
    import streamlit.web.cli as stcli

    app_path = os.path.join(os.path.dirname(internals.__file__), "app.py")
    sys.argv = ["streamlit", "run", app_path] + sys.argv[1:]
    stcli.main()


if __name__ == "__main__":
    main()
