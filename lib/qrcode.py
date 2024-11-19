import io
from io import FileIO, BytesIO

import segno
from segno import QRCode

def generate_qr_code(number: str, category: str):
    data: list = [number, category, "StudentEngagement"]
    tag: str = "_".join(data)

    img: QRCode = segno.make(tag, micro=False)

    file = BytesIO()
    img.save(file, kind="PNG", scale=10)

    return file, tag

