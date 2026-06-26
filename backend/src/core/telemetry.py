"""OpenTelemetry distributed tracing (config-gated, optional).

Enabled only when OTEL_EXPORTER_ENDPOINT is set AND the OpenTelemetry packages are
installed. Kept import-guarded so it's a no-op otherwise — no hard dependency.
Install (when needed): ``uv add opentelemetry-distro opentelemetry-exporter-otlp \
opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-sqlalchemy``
"""

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger("telemetry")


def init_telemetry(app) -> None:
    if not settings.otel_exporter_endpoint:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning("otel_packages_not_installed")
        return

    provider = TracerProvider(resource=Resource.create({"service.name": "ucaas-backend"}))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint))
    )
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    logger.info("otel_initialized")
