from service_api.domain.exceptions.base_exceptions import CacheError


class CacheItemNotFoundError(CacheError):
    """Ошибка отсутствия кэша в брокере"""
