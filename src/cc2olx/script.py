import os
import sys

import django


def initialize_django() -> None:
    """
    Initialize the Django package.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cc2olx.settings")
    django.setup()


def run_script() -> None:
    initialize_django()

    from cc2olx.main import main

    sys.exit(main())


if __name__ == "__main__":
    run_script()
