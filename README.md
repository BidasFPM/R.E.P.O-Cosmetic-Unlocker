# REPO - Unlock All Cosmetics

A simple Python script to automatically unlock all cosmetics in the game **R.E.P.O.** by modifying the `MetaSave.es3` save file.

---

## Prerequisites

Make sure you have **Python** installed on your system. You will also need the `pycryptodome` library for decryption and encryption (AES-128-CBC + PBKDF2-SHA1 via Easy Save 3).

Open your terminal or command prompt and run:
```bash
pip install pycryptodome
```

---

## How to Use

1. **Close the game** before running the script.
2. (Optional) **Disable Steam Cloud** for R.E.P.O. to prevent your synchronized save from overwriting the modifications.
3. Run the script:
   ```bash
   python repo_unlock_cosmetics.py
   ```
   *(If your save file is located in a custom directory, you can also pass the path as an argument: `python repo_unlock_cosmetics.py "C:\path\to\MetaSave.es3"`)*

---

## Features

* **Auto-Detection:** Automatically locates your `MetaSave.es3` file inside `%AppData%\..\LocalLow\semiwork\Repo\`.
* **Automatic Backups:** Always creates a timestamped backup (`.bak`) in the same folder before making any changes.
* **Safe Handling:** Fully decrypts, updates the cosmetic unlock lists (`cosmeticUnlocks` and `cosmeticHistory`), and re-encrypts the save file securely.