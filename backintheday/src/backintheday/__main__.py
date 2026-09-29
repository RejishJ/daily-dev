"""Entry point for ``python -m backintheday``."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
