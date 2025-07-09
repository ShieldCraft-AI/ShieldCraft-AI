def color_log(session, msg, style=None):
    """
    Print a message to the session log with optional ANSI font style.
    style: one of 'bold', 'underline', 'red', 'yellow', 'green', 'cyan', 'magenta', or None.
    """
    styles = {
        "bold": "\033[1m",
        "underline": "\033[4m",
        "red": "\033[31m",
        "yellow": "\033[33m",
        "green": "\033[32m",
        "cyan": "\033[36m",
        "magenta": "\033[35m",
        None: "",
    }
    reset = "\033[0m"
    prefix = styles.get(style, "")
    session.log(f"{prefix}{msg}{reset}")


def matrix_log(session, msg, color="green"):
    """
    color: 'green', 'yellow', 'red', or 'bold'.
    """
    colors = {
        "green": "\033[1;32m",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "black_bg": "\033[40m",
        "yellow": "\033[1;33m",
        "red": "\033[1;31m",
    }
    c = colors.get(color, colors["green"])
    session.log(f"{colors['black_bg']}{c}{msg}{colors['reset']}")


def color_error(session, msg, style="red"):
    styles = {
        "bold": "\033[1m",
        "underline": "\033[4m",
        "red": "\033[31m",
        "yellow": "\033[33m",
        "green": "\033[32m",
        "cyan": "\033[36m",
        "magenta": "\033[35m",
        None: "",
    }
    reset = "\033[0m"
    prefix = styles.get(style, "")
    session.error(f"{prefix}{msg}{reset}")
