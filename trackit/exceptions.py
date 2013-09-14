"""
Exceptions that trackit may raise.

These are generally for internal use.
"""

class TrackitException(Exception):
    """Indication of some data validation or generic exception
    in trackit that trackit should catch."""

class ArgumentParsingException(TrackitException):
    """Trackit uses this to signal that something went wrong argparsing.

    The default for argparse is to raise SystemExit, but that means we
    can not easily test our CLI.
    """
