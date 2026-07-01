"""LI057 (Slice 1) — engine-regressieborging: de transitie-attributen zijn geen lifecycle-driver.

`migratiepad`/`complexiteit`/`prioriteit` verhuisden van de applicatie-subtabel naar het basis-
component. De scoring-engine mag deze NOOIT lezen — de enige lifecycle-driver blijft de checklist-
score (+ open blokkades). Dit is de OFFLINE helft van de dubbele borging (import-/broncode-afwezigheid);
de LIVE helft (geen-mutatie van ComponentProfiel/lifecycle) wordt gedekt door test_lifecycle*.py.
"""
import inspect

from services import lifecycle_service


def test_engine_leest_transitie_attributen_niet():
    """De lifecycle-service-broncode refereert nergens aan de drie verhuisde velden."""
    src = inspect.getsource(lifecycle_service)
    for veld in ("migratiepad", "complexiteit", "prioriteit"):
        assert veld not in src, (
            f"lifecycle_service refereert aan '{veld}' — de transitie-attributen mogen GEEN "
            f"lifecycle-driver zijn (score blijft de enige driver)."
        )


def test_engine_beslisregel_hangt_alleen_van_score_en_blokkades():
    """`bepaal_lifecycle` (de pure driver) neemt uitsluitend score-telling + open blokkades —
    geen migratiepad/complexiteit/prioriteit-parameters."""
    params = set(inspect.signature(lifecycle_service.bepaal_lifecycle).parameters)
    assert not (params & {"migratiepad", "complexiteit", "prioriteit"})
