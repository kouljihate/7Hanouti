import io
import random
import string
from barcode import Code128
from barcode.writer import ImageWriter


def generate_barcode_image(code: str) -> bytes:
    rv = io.BytesIO()
    Code128(code, writer=ImageWriter()).write(rv, {"module_width": 0.25, "module_height": 8, "font_size": 8, "text_distance": 2, "quiet_zone": 2})
    rv.seek(0)
    return rv.getvalue()


def generate_unique_code(existing_codes: set) -> str:
    while True:
        code = "ED" + "".join(random.choices(string.digits, k=8))
        if code not in existing_codes:
            return code
