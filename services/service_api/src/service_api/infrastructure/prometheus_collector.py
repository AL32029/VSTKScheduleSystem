from prometheus_client import REGISTRY, Counter, Gauge, Histogram

from service_api.application.ports.metrics_collector import MetricsCollector


class PrometheusMetricsCollector(MetricsCollector):
    def __init__(self, registry=None):
        self._registry = registry or REGISTRY
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}

    def inc_counter(self, name: str, value: float = 1, **labels):
        counter = self._get_counter(name, **labels)

        if counter._labelnames:
            counter.labels(**labels).inc(value)
        else:
            counter.inc(value)

    def inc_gauge(self, name: str, value: float = 1, **labels):
        gauge = self._get_gauge(name, **labels)

        if gauge._labelnames:
            gauge.labels(**labels).inc(value)
        else:
            gauge.inc(value)

    def dec_gauge(self, name: str, value: float = 1, **labels):
        gauge = self._get_gauge(name, **labels)

        if gauge._labelnames:
            gauge.labels(**labels).dec(value)
        else:
            gauge.dec(value)

    def observe_histogram(self, name: str, value: float, **labels):
        histogram = self._get_histogram(name, **labels)

        if histogram._labelnames:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)

    def _get_counter(self, name: str, doc: str = "Counter", **labels) -> Counter:
        if name not in self._counters:
            self._counters[name] = Counter(
                name, doc, list(labels.keys()), registry=self._registry
            )

        return self._counters[name]

    def _get_gauge(self, name: str, doc: str = "Gauge", **labels) -> Gauge:
        if name not in self._gauges:
            self._gauges[name] = Gauge(
                name, doc, list(labels.keys()), registry=self._registry
            )

        return self._gauges[name]

    def _get_histogram(self, name: str, doc: str = "Histogram", **labels) -> Histogram:
        if name not in self._histograms:
            self._histograms[name] = Histogram(
                name, doc, list(labels.keys()), registry=self._registry
            )

        return self._histograms[name]
