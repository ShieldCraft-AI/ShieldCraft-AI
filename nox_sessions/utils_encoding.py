import os
import sys


def force_utf8():
    """Force UTF-8 encoding for all output, subprocesses, and environment."""
    # Set environment variables for subprocesses
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["LANG"] = "C.UTF-8"
    # Reconfigure stdio for UTF-8 (Python 3.7+)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        # Fallback for older Python or redirected output
        try:
            import io

            sys.stdout = io.TextIOWrapper(
                sys.stdout.detach(), encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.detach(), encoding="utf-8", errors="replace"
            )
        except (AttributeError, io.UnsupportedOperation, ValueError):
            pass
