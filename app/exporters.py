from datetime import datetime
from pathlib import Path
import re

from fpdf import FPDF


def _t(value):
    """Convert text to PDF-safe characters."""
    if value is None:
        return ""

    text = str(value)

    replacements = {
        "–": "-",
        "—": "-",
        "−": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
        "→": "->",
        "←": "<-",
        "™": "(TM)",
        "®": "(R)",
        "©": "(C)",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove characters that standard Helvetica cannot reliably render.
    text = text.encode("latin-1", "replace").decode("latin-1")

    # Prevent extremely long unbroken strings from breaking FPDF.
    text = re.sub(r"(\S{45})", r"\1 ", text)

    return text.strip()


class ComicPDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 15)
        self.cell(0, 10, "ComicCraft", align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(
            0,
            10,
            f"Page {self.page_no()}",
            align="C",
        )


def save_pdf(layout, exports_dir: Path):
    exports_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"comiccraft_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.pdf"
    )

    output_path = exports_dir / filename

    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    for panel in layout:

        pdf.add_page()

        # Panel title
        pdf.set_font("Helvetica", "B", 15)

        title = (
            f"Panel {panel.get('panel_number', '')}: "
            f"{_t(panel.get('title', ''))}"
        )

        pdf.multi_cell(
            170,
            9,
            title,
            align="L",
        )

        pdf.ln(3)

        # Panel image
        image_path = exports_dir.parent / panel["image_path"].lstrip("/")

        if image_path.exists():
            pdf.image(
                str(image_path),
                x=25,
                w=160,
            )
            pdf.ln(8)

        # Scene description
        scene = _t(panel.get("scene_description", ""))

        if scene:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(
                170,
                6,
                scene,
                align="L",
            )
            pdf.ln(3)

        # Optional text fields
        pdf.set_font("Helvetica", "B", 10)

        for label, key in [
            ("Caption", "caption"),
            ("Narration", "narration"),
            ("Dialogue", "dialogue"),
        ]:

            value = _t(panel.get(key, ""))

            if value:
                pdf.multi_cell(
                    170,
                    6,
                    f"{label}: {value}",
                    align="L",
                )
                pdf.ln(1)

    pdf.output(str(output_path))

    return f"/static/exports/{output_path.name}"