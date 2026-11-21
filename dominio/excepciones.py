"""Excepciones de dominio: una base por sistema y una subclase por regla."""


class ErrorDeDominio(Exception):
    """Base de todas las reglas de negocio violadas en el CRCE."""


class EstadoNoPermiteOperacion(ErrorDeDominio):
    """R5: el estado actual del aviso no admite la operación pedida."""

    def __init__(self, estado: str, operacion: str) -> None:
        super().__init__(f"Un aviso {estado} no permite {operacion}")
        self.estado = estado
        self.operacion = operacion


class JustificacionInvalida(ErrorDeDominio):
    """R4: descartar exige una justificación que no esté vacía."""

    def __init__(self) -> None:
        super().__init__("La justificación del descarte no puede estar vacía")


class TextoDeNotaInvalido(ErrorDeDominio):
    """Una nota de texto no puede estar vacía."""

    def __init__(self) -> None:
        super().__init__("El texto de la nota no puede estar vacío")


class AutorNoCorresponde(ErrorDeDominio):
    """Solo el reportante que registró el aviso puede agregarle notas."""

    def __init__(self) -> None:
        super().__init__("Solo el reportante del aviso puede agregarle notas")


class ValorFueraDeCatalogo(ErrorDeDominio):
    """Un valor que no pertenece a un catálogo cerrado no llega a un aviso."""

    def __init__(self, catalogo: str, valor: object) -> None:
        super().__init__(f"{valor!r} no pertenece al catálogo {catalogo}")
        self.catalogo = catalogo
        self.valor = valor
