from abc import ABC, abstractmethod


class MetricsCollector(ABC):
    @abstractmethod
    def inc_counter(self, name: str, value: float = 1, **labels):
        """Увеличение счетчика"""
        raise NotImplementedError

    @abstractmethod
    def inc_gauge(self, name: str, value: float = 1, **labels):
        """Увеличение Gauge"""
        raise NotImplementedError

    @abstractmethod
    def dec_gauge(self, name: str, value: float = 1, **labels):
        """Уменьшение Gauge"""
        raise NotImplementedError

    @abstractmethod
    def observe_histogram(self, name: str, value: float, **labels):
        """Запись значения в гистограмму"""
        raise NotImplementedError
