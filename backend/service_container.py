from functools import lru_cache
from services_v2 import ChurnServiceV2


@lru_cache(maxsize=1)
def get_churn_service() -> ChurnServiceV2:
    return ChurnServiceV2()
