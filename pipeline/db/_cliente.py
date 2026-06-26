import os

from supabase import Client, create_client

_cliente: Client | None = None


def obter_cliente() -> Client:
    global _cliente
    if _cliente is None:
        _cliente = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    return _cliente
