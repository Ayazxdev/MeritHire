import base64, hashlib
import orjson
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from app.config import settings

def _b64decode(s: str) -> bytes:
    return base64.b64decode(s.encode())

def _b64encode(b: bytes) -> str:
    return base64.b64encode(b).decode()

def get_private_key() -> Ed25519PrivateKey:
    raw = _b64decode(settings.SIGNING_PRIVATE_KEY_B64)
    return Ed25519PrivateKey.from_private_bytes(raw)

def get_public_key() -> Ed25519PublicKey:
    raw = _b64decode(settings.SIGNING_PUBLIC_KEY_B64)
    return Ed25519PublicKey.from_public_bytes(raw)

def canonical_json(data: dict) -> bytes:
    return orjson.dumps(data, option=orjson.OPT_SORT_KEYS)

def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def sign_credential(credential: dict) -> tuple[str, str]:
    payload = canonical_json(credential)
    h = sha256_hex(payload)
    sig = get_private_key().sign(payload)
    return h, _b64encode(sig)

def verify_credential(credential: dict, signature_b64: str) -> bool:
    payload = canonical_json(credential)
    sig = base64.b64decode(signature_b64)
    pk = get_public_key()
    try:
        pk.verify(sig, payload)
        return True
    except Exception:
        return False
