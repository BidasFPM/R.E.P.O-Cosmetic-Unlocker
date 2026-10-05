"""
REPO - Unlock All Cosmetics
============================
Unlocks all cosmetics in the MetaSave.es3 save file of the game R.E.P.O.

File location (Windows):
    %AppData%\\..\\LocalLow\\semiwork\\Repo\\MetaSave.es3

Usage:
    python repo_unlock_cosmetics.py
    (the script finds the save automatically; or pass the path as an argument)

Requirements:
    pip install pycryptodome

The script always creates a backup (.bak) before modifying the file.
Format: AES-128-CBC + PBKDF2-SHA1 (Easy Save 3)
"""

import json
import os
import sys
import shutil
from datetime import datetime

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
from Crypto.Util.Padding import pad, unpad

# Fixed Easy Save password used by REPO (publicly known in the community)
ES3_PASSWORD = "Why would you want to cheat?... :o It's no fun. :') :'D"

# Total number of cosmetics in the game (id 0 to TOTAL_COSMETICS-1). If Semiwork adds
# more cosmetics in a future update, you only need to increase this number.
TOTAL_COSMETICS = 547


def default_save_path():
    local_low = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow")
    return os.path.join(local_low, "semiwork", "Repo", "MetaSave.es3")


def decrypt_es3(data: bytes, password: str) -> dict:
    salt = data[:16]
    key = PBKDF2(password.encode(), salt, dkLen=16, count=100, hmac_hash_module=SHA1)
    cipher = AES.new(key, AES.MODE_CBC, IV=salt)
    decrypted = unpad(cipher.decrypt(data[16:]), AES.block_size)
    return json.loads(decrypted), salt


def encrypt_es3(json_obj: dict, password: str, salt: bytes) -> bytes:
    raw = json.dumps(json_obj, indent=2).encode("utf-8")
    key = PBKDF2(password.encode(), salt, dkLen=16, count=100, hmac_hash_module=SHA1)
    cipher = AES.new(key, AES.MODE_CBC, IV=salt)
    return salt + cipher.encrypt(pad(raw, AES.block_size))


def unlock_all_cosmetics(path: str, total: int = TOTAL_COSMETICS):
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path, "rb") as f:
        raw_data = f.read()

    try:
        data, salt = decrypt_es3(raw_data, ES3_PASSWORD)
    except Exception as e:
        print("Failed to decrypt. The file may have an unexpected format "
              "or the password may have changed in a game update.")
        print(f"Details: {e}")
        sys.exit(1)

    # Backup before any modifications
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{path}.{timestamp}.bak"
    shutil.copy2(path, backup_path)
    print(f"Backup created at: {backup_path}")

    all_ids = list(range(total))

    before = len(data.get("cosmeticUnlocks", {}).get("value", []))

    for field in ("cosmeticUnlocks", "cosmeticHistory"):
        if field in data:
            data[field]["value"] = all_ids
        else:
            data[field] = {
                "__type": "System.Collections.Generic.List`1[[System.Int32, mscorlib, "
                          "Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]],mscorlib",
                "value": all_ids,
            }

    new_bytes = encrypt_es3(data, ES3_PASSWORD, salt)

    with open(path, "wb") as f:
        f.write(new_bytes)

    print(f"Cosmetics unlocked: {before} -> {total}")
    print("Save file successfully updated.")
    print("IMPORTANT: Disable Steam Cloud for REPO before opening the game, "
          "otherwise the synchronized save may overwrite this change.")


if __name__ == "__main__":
    save_path = sys.argv[1] if len(sys.argv) > 1 else default_save_path()
    print(f"Using save file: {save_path}")

    try:
        unlock_all_cosmetics(save_path)
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print()
    input("Press ENTER to close this window...")