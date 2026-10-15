from pathlib import Path

from app.services.certificate_generator import generate_certificate


def test_generate_certificate():

    file_path = generate_certificate(
        recipient_name="Kavin Kumar",
        event_name="Python Workshop",
        certificate_id=999
    )

    path = Path(file_path)

    assert path.exists()
    assert path.suffix == ".pdf"

    path.unlink()