import os
import ssl
from pathlib import Path

import httpx

DEFAULT_CA_BUNDLE_PATH = "/etc/ssl/certs/ca-certificates.crt"


def _create_ssl_context(cafile: str) -> ssl.SSLContext:
    context = ssl.create_default_context(cafile=cafile)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


def resolve_tls_verify() -> ssl.SSLContext | bool:
    env_ca_bundle = (
        os.getenv("SSL_CERT_FILE")
        or os.getenv("REQUESTS_CA_BUNDLE")
        or os.getenv("CURL_CA_BUNDLE")
    )
    if env_ca_bundle and Path(env_ca_bundle).exists():
        return _create_ssl_context(env_ca_bundle)

    if Path(DEFAULT_CA_BUNDLE_PATH).exists():
        return _create_ssl_context(DEFAULT_CA_BUNDLE_PATH)

    return True


def create_http_client(user_agent: str) -> httpx.Client:
    return httpx.Client(
        follow_redirects=True,
        timeout=10.0,
        verify=resolve_tls_verify(),
        headers={"User-Agent": user_agent},
    )
