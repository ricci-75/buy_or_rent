"""Buy or rent: compare renting and buying a home with a Streamlit app."""

import sys
from pathlib import Path


def main() -> None:
    """Launch the Streamlit application."""
    from streamlit.web import cli

    sys.argv = ["streamlit", "run", str(Path(__file__).with_name("app.py"))]
    sys.exit(cli.main())
