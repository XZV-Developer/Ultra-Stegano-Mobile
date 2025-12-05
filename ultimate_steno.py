import os, re, base64, binascii
from PIL import Image
import numpy as np

# -----------------------------------------------------------
#  Utility
# -----------------------------------------------------------
def ensure(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure("HASIL")

# -----------------------------------------------------------
#  Extract Base64
# -----------------------------------------------------------
def scan_base64(text):
    print("[*] Checking Base64...")
    outdir = "HASIL/base64"
    ensure(outdir)

    matches = re.findall(rb"[A-Za-z0-9+/=]{40,}", text)
    if not matches:
        print("  - No Base64 found.")
        return

    for i, m in enumerate(matches):
        try:
            data = base64.b64decode(m)
            open(f"{outdir}/decoded_{i}.bin", "wb").write(data)
        except:
            pass

    print(f"  ✔ Done! ({len(matches)} found)")


# -----------------------------------------------------------
#  Extract HEX
# -----------------------------------------------------------
def scan_hex(text):
    print("[*] Checking HEX sequences...")
    outdir = "HASIL/hex"
    ensure(outdir)

    matches = re.findall(rb"(?:[0-9A-Fa-f]{2}){20,}", text)
    if not matches:
        print("  - No HEX found.")
        return

    for i, m in enumerate(matches):
        try:
            data = binascii.unhexlify(m)
            open(f"{outdir}/hex_{i}.bin", "wb").write(data)
        except:
            pass

    print(f"  ✔ Done! ({len(matches)} found)")


# -----------------------------------------------------------
#  SUPER FAST LSB
# -----------------------------------------------------------
def lsb_fast(image_path):
    print("[*] Extracting LSB (super fast)...")

    outdir = "HASIL/lsb"
    ensure(outdir)

    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    # ambil bit paling rendah, dikali 255 biar terlihat hitam/putih
    lsb_r = (arr[:, :, 0] & 1) * 255
    lsb_g = (arr[:, :, 1] & 1) * 255
    lsb_b = (arr[:, :, 2] & 1) * 255

    Image.fromarray(lsb_r.astype("uint8")).save(f"{outdir}/lsb_r.png")
    Image.fromarray(lsb_g.astype("uint8")).save(f"{outdir}/lsb_g.png")
    Image.fromarray(lsb_b.astype("uint8")).save(f"{outdir}/lsb_b.png")

    print("  ✔ LSB extraction finished!")


# -----------------------------------------------------------
#  Bitplane Slicing (optimized)
# -----------------------------------------------------------
def bitplanes(image_path):
    print("[*] Extracting bitplanes...")

    outdir = "HASIL/bitplanes"
    ensure(outdir)

    img = Image.open(image_path).convert("L")
    arr = np.array(img)

    for bit in range(8):
        plane = ((arr >> bit) & 1) * 255
        Image.fromarray(plane.astype("uint8")).save(f"{outdir}/bit_{bit}.png")

    print("  ✔ Bitplanes finished!")


# -----------------------------------------------------------
#  Meta + strings
# -----------------------------------------------------------
def scan_strings(text):
    print("[*] Extracting strings...")

    outdir = "HASIL/strings"
    ensure(outdir)

    try:
        extracted = re.findall(rb"[ -~]{6,}", text)
        with open(f"{outdir}/strings.txt", "wb") as f:
            for s in extracted:
                f.write(s + b"\n")
        print(f"  ✔ Saved {len(extracted)} strings!")
    except:
        print("  - string extraction failed")


# -----------------------------------------------------------
#  MAIN
# -----------------------------------------------------------
def scan(file):
    print(f"[+] Scanning: {file}")

    with open(file, "rb") as f:
        raw = f.read()

    # text-based stego
    scan_base64(raw)
    scan_hex(raw)
    scan_strings(raw)

    # image-based stego
    try:
        lsb_fast(file)
        bitplanes(file)
    except:
        print("[!] Image processing skipped (not an image?)")

    print("\n✔ Selesai! Semua output ada di folder: HASIL/")


# -----------------------------------------------------------
#  Run
# -----------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:\n   python ultimate_stego_mobile.py <file>")
        exit()

    scan(sys.argv[1])