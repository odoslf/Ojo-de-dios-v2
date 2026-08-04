"""Base exceptions for Ojo de Dios."""


class OjoDeDiosError(RuntimeError):
    """Base exception for Ojo de Dios."""


class ConfigurationError(OjoDeDiosError):
    """Raised when runtime configuration is invalid."""


class ContractError(OjoDeDiosError):
    """Raised when an internal contract is broken."""
