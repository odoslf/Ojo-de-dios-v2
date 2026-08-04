"""Manual implementation marker exception for Ojo de Dios contracts."""


class ManualImplementationRequired(RuntimeError):
    """Raised when a technique requires private user implementation."""

    marker = "IMPLEMENTACION_USUARIO_REQUERIDA"

    def __init__(self, message: str | None = None):
        super().__init__(
            message
            or "IMPLEMENTACION_USUARIO_REQUERIDA: conecta aquí tu lógica privada."
        )
