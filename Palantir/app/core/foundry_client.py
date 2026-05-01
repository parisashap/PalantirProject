import foundry_sdk
from app.core.config import settings
from functools import lru_cache

@lru_cache()
def get_foundry_client():
    return foundry_sdk.FoundryClient(
        auth=foundry_sdk.UserTokenAuth(token=settings.FOUNDRY_TOKEN),
        hostname=settings.FOUNDRY_HOSTNAME,
    )
