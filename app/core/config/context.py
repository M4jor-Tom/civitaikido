from contextvars import ContextVar

session_id_var: ContextVar[str] = ContextVar("session_id")
session_id_var.set("global")
