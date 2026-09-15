"""Keep Airflow's forked processes stable on macOS."""

import sys
from types import ModuleType


if sys.platform == "darwin":
    setproctitle = ModuleType("setproctitle")
    setproctitle.getproctitle = lambda: "python"
    setproctitle.setproctitle = lambda _title: None
    sys.modules["setproctitle"] = setproctitle
