"""
REPO - Unlock All Cosmetics
============================
Unlocks all cosmetics in the MetaSave.es3 save file of the game R.E.P.O.

File location (Windows):
    %AppData%\\..\\LocalLow\\semiwork\\Repo\\MetaSave.es3

Usage:
    python repo_unlocker.py
    (the script finds the save automatically; or pass the path as an argument)

Requirements:
    pip install pycryptodome

The script always creates a backup (.bak) before modifying the file.
Format: AES-128-CBC + PBKDF2-SHA1 (Easy Save 3)

Works both with a console and as a windowed build (PyInstaller --noconsole):
without a console, messages are shown in popup windows instead.
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
TOTAL_COSMETICS = 557


def show(msg: str):
    """Print if a console exists, otherwise show a popup window."""
    if sys.stdout is not None:
        try:
            print(msg)
            return
        except Exception:
            pass
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("REPO Unlocker", msg)
        root.destroy()
    except Exception:
        pass


def default_save_path():
    local_low = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow")
    return os.path.join(local_low, "semiwork", "Repo", "MetaSave.es3")


def decrypt_es3(data: bytes, password: str):
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


def unlock_all_cosmetics(path: str, total: int = TOTAL_COSMETICS) -> bool:
    if not os.path.isfile(path):
        show(f"File not found: {path}")
        return False

    with open(path, "rb") as f:
        raw_data = f.read()

    try:
        data, salt = decrypt_es3(raw_data, ES3_PASSWORD)
    except Exception as e:
        show("Failed to decrypt. The file may have an unexpected format "
             "or the password may have changed in a game update.\n"
             f"Details: {e}")
        return False

    # Backup before any modifications
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{path}.{timestamp}.bak"
    shutil.copy2(path, backup_path)

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

    show(f"Backup created at: {backup_path}\n"
         f"Cosmetics unlocked: {before} -> {total}\n"
         "Save file successfully updated.\n\n"
         "IMPORTANT: Disable Steam Cloud for REPO before opening the game, "
         "otherwise the synchronized save may overwrite this change.")
    return True


if __name__ == "__main__":
    save_path = sys.argv[1] if len(sys.argv) > 1 else default_save_path()
    show(f"Using save file: {save_path}")

    try:
        unlock_all_cosmetics(save_path)
    except Exception as e:
        show(f"Unexpected error: {e}")

    # Only wait for ENTER if a real console exists
    if sys.stdin is not None:
        try:
            input("\nPress ENTER to close this window...")
        except (RuntimeError, EOFError):
            pass
