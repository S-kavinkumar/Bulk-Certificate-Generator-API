from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


OUTPUT_DIRECTORY = Path("generated_certificates")


def generate_certificate(
    recipient_name: str,
    event_name: str,
    certificate_id: int
) -> str:

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_name = "".join(
        character
        for character in recipient_name
        if character.isalnum() or character in (" ", "_", "-")
    ).strip()

    safe_name = safe_name.replace(" ", "_")

    filename = f"{safe_name}_{certificate_id}.pdf"

    file_path = OUTPUT_DIRECTORY / filename

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=A4
    )

    width, height = A4

    # Border
    pdf.rect(
        40,
        40,
        width - 80,
        height - 80
    )

    # Title
    pdf.setFont(
        "Helvetica-Bold",
        30
    )

    pdf.drawCentredString(
        width / 2,
        height - 150,
        "CERTIFICATE OF PARTICIPATION"
    )

    # Main text
    pdf.setFont(
        "Helvetica",
        16
    )

    pdf.drawCentredString(
        width / 2,
        height - 230,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFont(
        "Helvetica-Bold",
        26
    )

    pdf.drawCentredString(
        width / 2,
        height - 290,
        recipient_name
    )

    # Event
    pdf.setFont(
        "Helvetica",
        16
    )

    pdf.drawCentredString(
        width / 2,
        height - 350,
        f"for participating in {event_name}"
    )

    # Certificate ID
    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        60,
        60,
        f"Certificate ID: {certificate_id}"
    )

    pdf.save()

    return str(file_path)