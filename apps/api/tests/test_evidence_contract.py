from uuid import uuid4

from app.contracts.cases import EvidenceItem, EvidenceSource


def test_evidence_contract_preserves_confidence() -> None:
    item = EvidenceItem(
        id=uuid4(),
        source=EvidenceSource.VISION,
        kind="delivery_photo",
        summary="Package visible at the delivery address",
        confidence=0.92,
    )
    assert item.confidence == 0.92
