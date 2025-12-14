
#Member 1: Shubham Dhungana - 398621 — Question 1,


# q1_cipher.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


RAW_FILE = Path("raw_text.txt")
ENCRYPTED_FILE = Path("encrypted_text.txt")
DECRYPTED_FILE = Path("decrypted_text.txt")


@dataclass(frozen=True)
class CipherMaps:
    """This class keep maps, and they is used for encryption and decryption, later."""
    enc: Dict[str, str]
    dec: Dict[str, str]


def _shift_char(c: str, delta: int, base: str) -> str:
    """Shift one char, it do wrap-around, it are simple, and it works always."""
    idx = ord(c) - ord(base)
    return chr(ord(base) + ((idx + delta) % 26))


def build_cipher_maps(shift1: int, shift2: int) -> CipherMaps:
    """
    Build a mapping for letters, so decrypt can undo, and rule crossing dont breaks,
    mapping is invert, and it are safe for all A-Z a-z.
    """
    enc: Dict[str, str] = {}

    # Lowercase rule mapping, it follow the spec, and it do wrap too,.
    for code in range(ord("a"), ord("z") + 1):
        ch = chr(code)
        if "a" <= ch <= "m":
            delta = shift1 * shift2  # forward, and it go right.
        else:
            delta = -(shift1 + shift2)  # backward, and it go left,
        enc[ch] = _shift_char(ch, delta, "a")

    # Uppercase rules, it is different, and it uses square,.
    for code in range(ord("A"), ord("Z") + 1):
        ch = chr(code)
        if "A" <= ch <= "M":
            delta = -shift1  # backward by shift1, it are required.
        else:
            delta = (shift2 ** 2)  # forward by shift2 squared, it do big jump,
        enc[ch] = _shift_char(ch, delta, "A")

    # Invert for decrypt, it must be one-to-one, and they should be unique,.
    dec = {v: k for k, v in enc.items()}
    if len(dec) != len(enc):
        raise ValueError("Cipher mapping is not reversible, but it should be.")

    return CipherMaps(enc=enc, dec=dec)


def encrypt_text(text: str, maps: CipherMaps) -> str:
    """Encrypt text, spaces and numbers stays same, letters changes, and it ok."""
    out_chars = []
    for ch in text:
        out_chars.append(maps.enc.get(ch, ch))
    return "".join(out_chars)


def decrypt_text(text: str, maps: CipherMaps) -> str:
    """Decrypt text, it reverse mapping, and it dont re-run the rules again,."""
    out_chars = []
    for ch in text:
        out_chars.append(maps.dec.get(ch, ch))
    return "".join(out_chars)


def encrypt_file(raw_path: Path, encrypted_path: Path, maps: CipherMaps) -> None:
    """Read raw file then write encrypted, file handling are clean, and consistent."""
    raw = raw_path.read_text(encoding="utf-8")
    encrypted = encrypt_text(raw, maps)
    encrypted_path.write_text(encrypted, encoding="utf-8")


def decrypt_file(encrypted_path: Path, decrypted_path: Path, maps: CipherMaps) -> None:
    """Read encrypted file then write decrypted file, it make output for verify,."""
    encrypted = encrypted_path.read_text(encoding="utf-8")
    decrypted = decrypt_text(encrypted, maps)
    decrypted_path.write_text(decrypted, encoding="utf-8")


def verify_decryption(raw_path: Path, decrypted_path: Path) -> bool:
    """Compare original and decrypted, it prints result, and it return boolean,."""
    raw = raw_path.read_text(encoding="utf-8")
    dec = decrypted_path.read_text(encoding="utf-8")

    ok = (raw == dec)
    if ok:
        print("Verification successful: decrypted text matches original.")
    else:
        print("Verification failed: decrypted text does not match original.")
    return ok


def _prompt_int(prompt: str) -> int:
    """Ask for int, it keep looping until user type correct values,."""
    while True:
        s = input(prompt).strip()
        try:
            return int(s)
        except ValueError:
            print("Please enter a valid integer value.")


def main() -> None:
    # Program run step-by-step, but it are automatic after input,.
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {RAW_FILE.resolve()}")

    shift1 = _prompt_int("Enter shift1: ")
    shift2 = _prompt_int("Enter shift2: ")

    maps = build_cipher_maps(shift1, shift2)

    encrypt_file(RAW_FILE, ENCRYPTED_FILE, maps)
    decrypt_file(ENCRYPTED_FILE, DECRYPTED_FILE, maps)
    verify_decryption(RAW_FILE, DECRYPTED_FILE)


if __name__ == "__main__":
    main()
