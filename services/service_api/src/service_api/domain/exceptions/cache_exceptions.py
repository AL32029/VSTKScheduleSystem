from service_api.domain.exceptions.base_exceptions import CacheError


class CacheItemNotFound(CacheError):
    """Ошибка отсутствия кэша в брокере"""
