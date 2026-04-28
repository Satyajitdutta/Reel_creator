"""
audioop_shim.py

Python 3.11  → audioop is built-in, nothing to do.
Python 3.13+ → audioop was removed; install audioop-lts and shim it in.

Import this module BEFORE importing pydub or any audio library.
"""
import sys

if sys.version_info >= (3, 13):
    try:
        import audioop  # noqa: F401 — already available (shouldn't happen on 3.13+)
    except ImportError:
        try:
            import audioop_lts as audioop  # type: ignore
            sys.modules["audioop"] = audioop
        except ImportError:
            pass  # pydub will raise its own clear error if it truly needs audioop
