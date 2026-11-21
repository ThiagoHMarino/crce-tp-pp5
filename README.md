# CRCE – TP Integrador 2026 (Paradigmas de Programación V)

Centro Regional de Coordinación de Emergencias. **Avance 1: avisos y notas**
(registrar aviso, agregar notas, descartar; aceptar queda fuera de este avance).

## Requisitos
- Python ≥ 3.11 y [uv](https://docs.astral.sh/uv/)
- El dominio usa solo la biblioteca estándar; `pytest` es dependencia de desarrollo.

## Ejecutar las pruebas
```bash
uv run pytest
```

## Estructura
```
pyproject.toml
dominio/        # excepciones, catálogos, estados, nota, aviso, usuarios
tests/          # test_avisos.py (un test por regla R1–R6, prefijo test_rN_)
docs/           # documento del avance (PDF) y diagramas de clases y estados
```

## Entrega
Tag `avance-1` sobre este repositorio público.
