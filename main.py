"""Pembuat gambar entri news-image-20261121 R2.

Skrip ini menghasilkan ``entry.png`` untuk kompetisi make.fun
"Sum up 21 November's world news in one image" (R2).

Cara kerja: menyalin berkas gambar sumber yang sudah disiapkan
(``source.jpg``, hasil riset berita 21 November hari penuh) menjadi
``entry.png`` di folder keluaran, lalu memeriksa hasilnya:
format JPEG dikenali dari magic bytes, ukuran tidak melebihi 1 MiB,
dan sidik SHA-256 salinan sama persis dengan sumber.

Folder keluaran dibaca dari variabel lingkungan
``MAKEFUN_OUTPUT_DIR`` (bawaan ``/output``) — repo tempat skrip ini
berada bersifat read-only saat dinilai, jadi hasil TIDAK boleh
ditulis ke folder repo. Penyalinan murni byte-ke-byte, jadi dua kali
jalan selalu memberi hasil yang identik. Hanya memakai pustaka
standar Python.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import sys

NAMA_SUMBER = "source.jpg"
NAMA_KELUARAN = "entry.png"
BATAS_BYTE = 1_048_576
SIDIK_SUMBER = (
    "ccb8a9abf7b224ef2e01bab7f325f305350caccf0b1886cdd415d1a91a8cbf7f"
)


def folder_repo() -> pathlib.Path:
    """Folder tempat skrip ini berada (folder repo entri)."""
    return pathlib.Path(__file__).resolve().parent


def folder_keluaran() -> pathlib.Path:
    """Folder tujuan dari lingkungan, atau /output.

    Repo bersifat read-only saat dinilai (grader memasang repo di
    /bot tanpa tulis), jadi hasil harus ke MAKEFUN_OUTPUT_DIR.
    """
    tujuan = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return pathlib.Path(tujuan) if tujuan else pathlib.Path("/output")


def temukan_sumber(folder: pathlib.Path) -> pathlib.Path:
    """Cari berkas gambar sumber; berhenti bila tidak ada."""
    berkas = folder / NAMA_SUMBER
    if not berkas.is_file():
        raise SystemExit(f"sumber tidak ditemukan: {berkas}")
    return berkas


def sidik_jari(berkas: pathlib.Path) -> str:
    """Hitung sidik SHA-256 dari isi berkas."""
    pencerna = hashlib.sha256()
    with berkas.open("rb") as tangan:
        while True:
            potongan = tangan.read(65536)
            if not potongan:
                break
            pencerna.update(potongan)
    return pencerna.hexdigest()


def periksa_jpeg(berkas: pathlib.Path) -> int:
    """Periksa magic bytes JPEG dan batas ukuran; kembalikan ukuran byte."""
    isi = berkas.read_bytes()
    if isi[:3] != b"\xff\xd8\xff":
        raise SystemExit(f"bukan berkas JPEG: {berkas}")
    if len(isi) > BATAS_BYTE:
        raise SystemExit(
            f"terlalu besar: {len(isi)} byte (batas {BATAS_BYTE})"
        )
    return len(isi)


def hasilkan_entri(sumber: pathlib.Path, tujuan: pathlib.Path) -> str:
    """Salin sumber ke tujuan dan pastikan salinannya sama persis."""
    if sumber.resolve() == tujuan.resolve():
        raise SystemExit("sumber dan tujuan tidak boleh berkas yang sama")
    tujuan.write_bytes(sumber.read_bytes())
    sidik = sidik_jari(tujuan)
    if sidik != SIDIK_SUMBER:
        raise SystemExit("sidik salinan tidak cocok dengan sumber")
    return sidik


def jalankan() -> int:
    """Titik masuk: buat entry.png lalu laporkan hasilnya."""
    folder = folder_repo()
    sumber = temukan_sumber(folder)
    if sidik_jari(sumber) != SIDIK_SUMBER:
        raise SystemExit("sidik sumber tidak cocok dengan yang tercatat")
    ukuran = periksa_jpeg(sumber)
    keluaran = folder_keluaran()
    keluaran.mkdir(parents=True, exist_ok=True)
    tujuan = keluaran / NAMA_KELUARAN
    sidik = hasilkan_entri(sumber, tujuan)
    print(f"dibuat: {tujuan}")
    print(f"ukuran: {ukuran} byte")
    print(f"sha256: {sidik}")
    return 0


if __name__ == "__main__":
    sys.exit(jalankan())
