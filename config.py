"""
Fixed configuration for the Form 1008 (Plas"am) generator: issuer identity,
file paths, and the coordinate map calibrated against the actual scanned
template (assets/template.pdf, A4 / 595x842pt).

Coordinates were measured directly off the scan (pixel-traced at 300dpi and
converted to PDF points), not guessed - the printed form's issuer/receiver
sides are mirrored (issuer fields sit on the right half of the page, receiver
fields on the left), so don't "fix" these to look symmetric without re-checking
against assets/template.pdf.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PDF = os.path.join(BASE_DIR, "assets", "template.pdf")
FONT_REGULAR = os.path.join(BASE_DIR, "assets", "fonts", "NotoSansHebrew-Regular.ttf")
FONT_BOLD = os.path.join(BASE_DIR, "assets", "fonts", "NotoSansHebrew-Bold.ttf")
ROSTER_XLSX = os.path.join(BASE_DIR, "data", "roster.xlsx")
ROSTER_CSV = os.path.join(BASE_DIR, "data", "roster.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

PAGE_WIDTH = 595
PAGE_HEIGHT = 842

# Fixed issuer (מנפק) identity - Arik Brod, Battalion 429
ISSUER = {
    "first_name": "אריק",
    "last_name": "ברוד",
    "rank": "סרן",
    "personal_number": "8087810",
}

# Coordinates measured from the scanned template. Each entry is
# (x, y, max_width) in PDF points, anchored at the RIGHT edge of the
# field (text grows leftward from that point, matching how these blanks
# are naturally filled in on the original scanned form). max_width is
# the measured gap to the next label/field - the generator shrinks the
# font to fit rather than overlapping a neighbor, since roster names
# and ranks vary in length.
COORDS = {
    # Top "שם המנפק:" / "שם המקבל:" name line
    "issuer_top_name": (420, 686, 139),
    "receiver_top_name": (166, 678, 95),
    # Bottom identity block: מ.א. / דרגה / שם משפחה / שם פרטי
    "issuer_first_name": (334, 115, 60),
    "issuer_last_name": (397, 114, 55),
    "issuer_rank": (435, 114, 35),
    "issuer_personal_number": (483, 114, 45),
    "receiver_first_name": (82, 113, 65),
    "receiver_last_name": (156, 113, 65),
    "receiver_rank": (214, 112, 50),
    "receiver_personal_number": (286, 111, 65),
    # Bottom signature/date line
    "issuer_signature": (442, 152, 38),
    "issuer_date": (354, 152, 52),
    "receiver_signature": (195, 151, 46),
    "receiver_date": (98, 151, 54),
    # Checkmarks in the "נמצא" column, for the two daily-issue rows
    "helmet_check": (288, 366),
    "vest_check": (288, 334),
}
