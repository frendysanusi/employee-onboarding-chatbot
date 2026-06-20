from __future__ import annotations


def log_usage(service: str, model: str, **metrics: float) -> None:
    parts = ", ".join(f"{name}={int(value):,}" for name, value in metrics.items() if value)
    if parts:
        print(f"[usage] {service} {model}: {parts}")
