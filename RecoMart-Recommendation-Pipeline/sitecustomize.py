import os
import pathlib
import signal

if os.name == "nt":
    if not hasattr(signal, "SIGALRM"):
        signal.SIGALRM = 0
    if not hasattr(signal, "ITIMER_REAL"):
        signal.ITIMER_REAL = 0

    _orig_signal = getattr(signal, "signal", None)
    if _orig_signal is not None:
        def _compat_signal(signum, handler):
            if signum == getattr(signal, "SIGALRM", None):
                return None
            return _orig_signal(signum, handler)

        signal.signal = _compat_signal

    if not hasattr(signal, "setitimer"):
        def _compat_setitimer(*args, **kwargs):
            return None

        signal.setitimer = _compat_setitimer

repo = pathlib.Path(__file__).resolve().parent
airflow_home = repo / "airflow"
os.environ.setdefault("AIRFLOW_HOME", str(airflow_home))
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
conn = "sqlite:///" + str((airflow_home / "airflow.db").resolve()).replace("\\", "/")
os.environ.setdefault("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN", conn)

try:
    import airflow.settings as settings
except Exception:
    settings = None
else:
    settings.SQL_ALCHEMY_CONN = conn
    settings.SQL_ALCHEMY_CONN_ASYNC = conn
