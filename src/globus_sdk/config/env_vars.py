"""
Definition and loading of standard environment variables, plus a wrappers for loading
and parsing values.

This does not include service URL env vars (see environments.py for loading of those)
"""
import logging
import os
from distutils.util import strtobool
from typing import Any, Optional, cast

log = logging.getLogger(__name__)


ENVNAME_VAR = "GLOBUS_SDK_ENVIRONMENT"
HTTP_TIMEOUT_VAR = "GLOBUS_SDK_HTTP_TIMEOUT"
SSL_VERIFY_VAR = "GLOBUS_SDK_VERIFY_SSL"


def _load_var(varname: str, default, explicit_value=None, cast=None):
    # use the explicit value if given and non-None, otherwise, do an env lookup
    value = (
        explicit_value if explicit_value is not None else os.getenv(varname, default)
    )
    if cast:
        value = cast(value, default)
    # only info log on non-default *values*
    # meaning that if we define the default as 'foo' and someone explicitly sets 'foo',
    # no info log gets emitted
    if value != default:
        log.info(f"on lookup, non-default setting: {varname}={value}")
    else:
        log.debug(f"on lookup, default setting: {varname}={value}")
    return value


def _bool_cast(value: Any, default) -> bool:
    if isinstance(value, bool):
        return value
    return strtobool(value.lower())


def _optfloat_cast(value: Any, default) -> Optional[float]:
    try:
        return float(value)
    except ValueError:
        pass
    if value == "":
        return cast(float, default)
    log.error(f'Value "{value}" can\'t cast to optfloat')
    raise ValueError(f"Invalid config float: {value}")


def get_environment_name(inputenv: Optional[str] = None) -> str:
    return cast(str, _load_var(ENVNAME_VAR, "production", explicit_value=inputenv))


def get_ssl_verify(value: Optional[bool] = None) -> bool:
    return cast(
        bool, _load_var(SSL_VERIFY_VAR, True, explicit_value=value, cast=_bool_cast)
    )


def get_http_timeout(value: Optional[float] = None) -> Optional[float]:
    ret = cast(
        Optional[float],
        _load_var(HTTP_TIMEOUT_VAR, 60.0, explicit_value=value, cast=_optfloat_cast),
    )
    if ret == -1.0:
        return None
    return ret