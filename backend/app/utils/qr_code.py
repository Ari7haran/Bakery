import random
import string
import qrcode
import io
import base64

def generate_order_number() -> str:
    digits = ''.join(random.choices(string.digits, k=6))
    return f"SC-{digits}"

def generate_pickup_number() -> str:
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    nums = ''.join(random.choices(string.digits, k=3))
    return f"PK-{letters}{nums}"

def generate_qr_code(data_str: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2C1810", back_color="#FFFDF9")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
