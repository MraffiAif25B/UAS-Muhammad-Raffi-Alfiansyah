"""
SISTEM MANAJEMEN PERPUSTAKAAN - Final Project UAS
Struktur Data : Linked List, Stack, Queue, Hash Map, BST
Database      : Flat File (.CSV)
Antarmuka     : Command-Line Interface (CLI)

Cara menjalankan:
    python perpustakaan_final.py
"""

import csv
import os
import sys
import uuid
from datetime import datetime, timedelta


# ============================================================
# BAGIAN 1 - STRUKTUR DATA
# ============================================================

# ------------------------------------------------------------
# 1A. LINKED LIST - menyimpan dan traversal daftar buku
# ------------------------------------------------------------
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data):
        node = Node(data)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self.size += 1

    def delete(self, isbn):
        cur, prev = self.head, None
        while cur:
            if cur.data["isbn"] == isbn:
                if prev:
                    prev.next = cur.next
                else:
                    self.head = cur.next
                self.size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def update(self, isbn, new_data):
        cur = self.head
        while cur:
            if cur.data["isbn"] == isbn:
                cur.data.update(new_data)
                return True
            cur = cur.next
        return False

    def find(self, isbn):
        cur = self.head
        while cur:
            if cur.data["isbn"] == isbn:
                return cur.data
            cur = cur.next
        return None

    def to_list(self):
        result = []
        cur = self.head
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result

    def search_by_title(self, keyword):
        result = []
        cur = self.head
        while cur:
            if keyword.lower() in cur.data.get("judul", "").lower():
                result.append(cur.data)
            cur = cur.next
        return result

    def search_by_author(self, keyword):
        result = []
        cur = self.head
        while cur:
            if keyword.lower() in cur.data.get("penulis", "").lower():
                result.append(cur.data)
            cur = cur.next
        return result


# ------------------------------------------------------------
# 1B. STACK - riwayat aksi (LIFO - Last In First Out)
# ------------------------------------------------------------
class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        return self._data.pop() if self._data else None

    def peek(self):
        return self._data[-1] if self._data else None

    def is_empty(self):
        return len(self._data) == 0

    def to_list(self):
        return list(reversed(self._data))


# ------------------------------------------------------------
# 1C. QUEUE - antrean peminjaman (FIFO - First In First Out)
# ------------------------------------------------------------
class QNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    def __init__(self):
        self.front = None
        self.rear  = None
        self.size  = 0

    def enqueue(self, data):
        node = QNode(data)
        if not self.rear:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def dequeue(self):
        if not self.front:
            return None
        data = self.front.data
        self.front = self.front.next
        if not self.front:
            self.rear = None
        self.size -= 1
        return data

    def is_empty(self):
        return self.front is None

    def to_list(self):
        result = []
        cur = self.front
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result


# ------------------------------------------------------------
# 1D. HASH MAP - pencarian cepat data anggota O(1)
# ------------------------------------------------------------
class HashMap:
    def __init__(self, capacity=64):
        self.capacity = capacity
        self.buckets  = [[] for _ in range(capacity)]
        self.count    = 0

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx][i] = (key, value)
                return
        self.buckets[idx].append((key, value))
        self.count += 1

    def get(self, key):
        for k, v in self.buckets[self._hash(key)]:
            if k == key:
                return v
        return None

    def delete(self, key):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx].pop(i)
                self.count -= 1
                return True
        return False

    def all_values(self):
        return [v for bucket in self.buckets for _, v in bucket]


# ------------------------------------------------------------
# 1E. BST (Binary Search Tree) - sorting buku A-Z
# ------------------------------------------------------------
class BSTNode:
    def __init__(self, key, data):
        self.key   = key
        self.data  = data
        self.left  = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key, data):
        self.root = self._insert(self.root, key, data)

    def _insert(self, node, key, data):
        if not node:
            return BSTNode(key, data)
        if key < node.key:
            node.left  = self._insert(node.left,  key, data)
        elif key > node.key:
            node.right = self._insert(node.right, key, data)
        else:
            node.data = data
        return node

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left,  result)
            result.append(node.data)
            self._inorder(node.right, result)

    def search(self, key):
        node = self._search(self.root, key)
        return node.data if node else None

    def _search(self, node, key):
        if not node or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)


# ============================================================
# BAGIAN 2 - DATABASE (Baca/Tulis CSV)
# ============================================================

DATA_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_perpustakaan")
BOOKS_FILE    = os.path.join(DATA_DIR, "buku.csv")
MEMBERS_FILE  = os.path.join(DATA_DIR, "anggota.csv")
LOANS_FILE    = os.path.join(DATA_DIR, "peminjaman.csv")
HISTORY_FILE  = os.path.join(DATA_DIR, "riwayat.csv")
WAITLIST_FILE = os.path.join(DATA_DIR, "antrian.csv")

BOOKS_FIELDS    = ["isbn", "judul", "penulis", "kategori", "tahun", "stok", "rak"]
MEMBERS_FIELDS  = ["id_anggota", "nama", "email", "telepon", "tgl_daftar", "status"]
LOANS_FIELDS    = ["id_pinjam", "id_anggota", "isbn", "tgl_pinjam", "tgl_kembali", "status"]
HISTORY_FIELDS  = ["timestamp", "aksi", "detail"]
WAITLIST_FIELDS = ["id_antrian", "id_anggota", "isbn", "tgl_daftar"]


def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def read_csv(filepath, fieldnames):
    ensure_dir()
    if not os.path.exists(filepath):
        return []
    with open(filepath, newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(filepath, fieldnames, rows):
    ensure_dir()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def db_load_books():
    return read_csv(BOOKS_FILE, BOOKS_FIELDS)

def db_save_books(rows):
    write_csv(BOOKS_FILE, BOOKS_FIELDS, rows)

def db_add_book(data):
    rows = db_load_books()
    rows.append(data)
    db_save_books(rows)

def db_update_book(isbn, new_data):
    rows = db_load_books()
    for r in rows:
        if r["isbn"] == isbn:
            r.update(new_data)
    db_save_books(rows)

def db_delete_book(isbn):
    db_save_books([r for r in db_load_books() if r["isbn"] != isbn])


def db_load_members():
    return read_csv(MEMBERS_FILE, MEMBERS_FIELDS)

def db_save_members(rows):
    write_csv(MEMBERS_FILE, MEMBERS_FIELDS, rows)

def db_add_member(data):
    rows = db_load_members()
    rows.append(data)
    db_save_members(rows)

def db_update_member(id_anggota, new_data):
    rows = db_load_members()
    for r in rows:
        if r["id_anggota"] == id_anggota:
            r.update(new_data)
    db_save_members(rows)

def db_delete_member(id_anggota):
    db_save_members([r for r in db_load_members() if r["id_anggota"] != id_anggota])


def db_load_loans():
    return read_csv(LOANS_FILE, LOANS_FIELDS)

def db_save_loans(rows):
    write_csv(LOANS_FILE, LOANS_FIELDS, rows)

def db_add_loan(data):
    rows = db_load_loans()
    rows.append(data)
    db_save_loans(rows)

def db_update_loan(id_pinjam, new_data):
    rows = db_load_loans()
    for r in rows:
        if r["id_pinjam"] == id_pinjam:
            r.update(new_data)
    db_save_loans(rows)

def db_active_loans_by_member(id_anggota):
    return [l for l in db_load_loans()
            if l["id_anggota"] == id_anggota and l["status"] == "dipinjam"]

def db_active_loans_by_isbn(isbn):
    return [l for l in db_load_loans()
            if l["isbn"] == isbn and l["status"] == "dipinjam"]


def db_load_history():
    return read_csv(HISTORY_FILE, HISTORY_FIELDS)

def db_append_history(aksi, detail):
    rows = db_load_history()
    rows.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "aksi"     : aksi,
        "detail"   : detail
    })
    write_csv(HISTORY_FILE, HISTORY_FIELDS, rows)


def db_load_waitlist():
    return read_csv(WAITLIST_FILE, WAITLIST_FIELDS)

def db_save_waitlist(rows):
    write_csv(WAITLIST_FILE, WAITLIST_FIELDS, rows)

def db_add_waitlist(data):
    rows = db_load_waitlist()
    rows.append(data)
    db_save_waitlist(rows)

def db_pop_waitlist(isbn):
    rows = db_load_waitlist()
    for i, r in enumerate(rows):
        if r["isbn"] == isbn:
            item = rows.pop(i)
            db_save_waitlist(rows)
            return item
    return None

def db_waitlist_by_isbn(isbn):
    return [r for r in db_load_waitlist() if r["isbn"] == isbn]


# ============================================================
# BAGIAN 3 - CONTROLLER (Business Logic)
# ============================================================

book_list     = LinkedList()
member_map    = HashMap()
history_stack = Stack()
wait_queue    = Queue()
book_bst      = BST()


def load_all():
    global book_list, member_map, history_stack, wait_queue, book_bst
    book_list     = LinkedList()
    member_map    = HashMap()
    history_stack = Stack()
    wait_queue    = Queue()
    book_bst      = BST()

    for b in db_load_books():
        book_list.append(b)
        book_bst.insert(b["judul"].lower(), b)

    for m in db_load_members():
        member_map.put(m["id_anggota"], m)

    for h in db_load_history():
        history_stack.push(h)

    for w in db_load_waitlist():
        wait_queue.enqueue(w)


def catat_log(aksi, detail):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "aksi"     : aksi,
        "detail"   : detail
    }
    history_stack.push(entry)
    db_append_history(aksi, detail)


# --- BUKU ---

def tambah_buku(judul, penulis, kategori, tahun, stok, rak, isbn=None):
    isbn = isbn or str(uuid.uuid4())[:8].upper()
    data = {
        "isbn"    : isbn,
        "judul"   : judul,
        "penulis" : penulis,
        "kategori": kategori,
        "tahun"   : str(tahun),
        "stok"    : str(stok),
        "rak"     : rak
    }
    book_list.append(data)
    book_bst.insert(judul.lower(), data)
    db_add_book(data)
    catat_log("TAMBAH_BUKU", "ISBN:" + isbn + " Judul:" + judul)
    return isbn


def lihat_semua_buku(urut_az=False):
    if urut_az:
        return book_bst.inorder()
    return book_list.to_list()


def cari_buku_judul(keyword):
    return book_list.search_by_title(keyword)


def cari_buku_penulis(keyword):
    return book_list.search_by_author(keyword)


def detail_buku(isbn):
    return book_list.find(isbn)


def update_buku(isbn, **kwargs):
    global book_bst
    book_list.update(isbn, kwargs)
    db_update_book(isbn, kwargs)
    book_bst = BST()
    for b in book_list.to_list():
        book_bst.insert(b["judul"].lower(), b)
    catat_log("UPDATE_BUKU", "ISBN:" + isbn)
    return True


def hapus_buku(isbn):
    if not book_list.find(isbn):
        return False, "Buku tidak ditemukan."
    if db_active_loans_by_isbn(isbn):
        return False, "Buku masih dipinjam, tidak bisa dihapus."
    book_list.delete(isbn)
    db_delete_book(isbn)
    catat_log("HAPUS_BUKU", "ISBN:" + isbn)
    return True, "Buku berhasil dihapus."


# --- ANGGOTA ---

def daftar_anggota(nama, email, telepon):
    id_a = "M" + str(uuid.uuid4())[:6].upper()
    data = {
        "id_anggota": id_a,
        "nama"      : nama,
        "email"     : email,
        "telepon"   : telepon,
        "tgl_daftar": datetime.now().strftime("%Y-%m-%d"),
        "status"    : "aktif"
    }
    member_map.put(id_a, data)
    db_add_member(data)
    catat_log("DAFTAR_ANGGOTA", "ID:" + id_a + " Nama:" + nama)
    return id_a


def lihat_semua_anggota():
    return member_map.all_values()


def detail_anggota(id_anggota):
    return member_map.get(id_anggota)


def update_anggota(id_anggota, **kwargs):
    m = member_map.get(id_anggota)
    if not m:
        return False, "Anggota tidak ditemukan."
    m.update(kwargs)
    member_map.put(id_anggota, m)
    db_update_member(id_anggota, kwargs)
    catat_log("UPDATE_ANGGOTA", "ID:" + id_anggota)
    return True, "Data anggota berhasil diperbarui."


def hapus_anggota(id_anggota):
    if not member_map.get(id_anggota):
        return False, "Anggota tidak ditemukan."
    if db_active_loans_by_member(id_anggota):
        return False, "Anggota masih memiliki pinjaman aktif."
    member_map.delete(id_anggota)
    db_delete_member(id_anggota)
    catat_log("HAPUS_ANGGOTA", "ID:" + id_anggota)
    return True, "Anggota berhasil dihapus."


# --- PEMINJAMAN ---

def pinjam_buku(id_anggota, isbn, hari=14):
    anggota = member_map.get(id_anggota)
    if not anggota:
        return False, "Anggota tidak ditemukan."
    if anggota.get("status") != "aktif":
        return False, "Status anggota tidak aktif."
    if len(db_active_loans_by_member(id_anggota)) >= 3:
        return False, "Batas pinjam 3 buku sudah tercapai."

    buku = book_list.find(isbn)
    if not buku:
        return False, "Buku tidak ditemukan."

    if int(buku.get("stok", 0)) <= 0:
        id_q = "Q" + str(uuid.uuid4())[:6].upper()
        item = {
            "id_antrian": id_q,
            "id_anggota": id_anggota,
            "isbn"      : isbn,
            "tgl_daftar": datetime.now().strftime("%Y-%m-%d")
        }
        wait_queue.enqueue(item)
        db_add_waitlist(item)
        catat_log("ANTRIAN", "Anggota:" + id_anggota + " ISBN:" + isbn)
        return False, "Stok habis. Anggota dimasukkan ke antrean (ID: " + id_q + ")."

    id_p    = "P" + str(uuid.uuid4())[:6].upper()
    tgl_p   = datetime.now().strftime("%Y-%m-%d")
    tgl_k   = (datetime.now() + timedelta(days=hari)).strftime("%Y-%m-%d")

    db_add_loan({
        "id_pinjam"  : id_p,
        "id_anggota" : id_anggota,
        "isbn"       : isbn,
        "tgl_pinjam" : tgl_p,
        "tgl_kembali": tgl_k,
        "status"     : "dipinjam"
    })

    stok_baru = str(int(buku["stok"]) - 1)
    book_list.update(isbn, {"stok": stok_baru})
    db_update_book(isbn, {"stok": stok_baru})

    catat_log("PINJAM", "ID:" + id_p + " Anggota:" + id_anggota + " ISBN:" + isbn)
    return True, "Berhasil dipinjam. ID Pinjam: " + id_p + " | Batas Kembali: " + tgl_k


def kembalikan_buku(id_pinjam):
    loan = next((l for l in db_load_loans() if l["id_pinjam"] == id_pinjam), None)
    if not loan:
        return False, "ID peminjaman tidak ditemukan."
    if loan["status"] != "dipinjam":
        return False, "Buku sudah dikembalikan sebelumnya."

    db_update_loan(id_pinjam, {"status": "dikembalikan"})

    isbn = loan["isbn"]
    buku = book_list.find(isbn)
    if buku:
        stok_baru = str(int(buku["stok"]) + 1)
        book_list.update(isbn, {"stok": stok_baru})
        db_update_book(isbn, {"stok": stok_baru})

    antrian = db_waitlist_by_isbn(isbn)
    pesan_antrian = ""
    if antrian:
        next_item = db_pop_waitlist(isbn)
        pesan_antrian = " | Antrean selanjutnya: Anggota " + next_item["id_anggota"] + " bisa meminjam."

    catat_log("KEMBALI", "ID:" + id_pinjam + " ISBN:" + isbn)
    return True, "Buku berhasil dikembalikan." + pesan_antrian


def lihat_pinjaman_aktif():
    return [l for l in db_load_loans() if l["status"] == "dipinjam"]


def lihat_pinjaman_terlambat():
    today  = datetime.now().date()
    result = []
    for l in db_load_loans():
        if l["status"] == "dipinjam":
            tgl = datetime.strptime(l["tgl_kembali"], "%Y-%m-%d").date()
            if tgl < today:
                l["terlambat"] = str((today - tgl).days) + " hari"
                result.append(l)
    return result


# --- LAPORAN ---

def lihat_riwayat(n=20):
    return history_stack.to_list()[:n]


def lihat_antrian(isbn=None):
    if isbn:
        return db_waitlist_by_isbn(isbn)
    return wait_queue.to_list()


def statistik():
    loans   = db_load_loans()
    counter = {}
    for l in loans:
        counter[l["isbn"]] = counter.get(l["isbn"], 0) + 1
    top_isbn = sorted(counter, key=counter.get, reverse=True)[:5]
    top_books = []
    for isbn in top_isbn:
        b = book_list.find(isbn)
        if b:
            top_books.append({"judul": b["judul"], "total": counter[isbn]})
    return {
        "total_judul"  : book_list.size,
        "total_anggota": member_map.count,
        "pinjam_aktif" : len([l for l in loans if l["status"] == "dipinjam"]),
        "terlambat"    : len(lihat_pinjaman_terlambat()),
        "total_antrian": wait_queue.size,
        "top_books"    : top_books,
    }


# ============================================================
# BAGIAN 4 - ANTARMUKA CLI
# ============================================================

def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def garis(panjang=65):
    print("-" * panjang)


def garis_tebal(panjang=65):
    print("=" * panjang)


def header(judul):
    bersihkan_layar()
    garis_tebal()
    print("  SISTEM PERPUSTAKAAN  |  " + judul)
    garis_tebal()
    print()


def jeda():
    input("\n  Tekan Enter untuk kembali...")


def pesan_ok(teks):
    print("  [OK] " + teks)


def pesan_error(teks):
    print("  [GAGAL] " + teks)


def pesan_info(teks):
    print("  [INFO] " + teks)


def tanya(label):
    return input("  > " + label + ": ").strip()


def cetak_buku(daftar):
    if not daftar:
        pesan_info("Tidak ada data buku.")
        return
    print()
    print("  {:<4} {:<12} {:<30} {:<22} {:<6} {:<6} {}".format(
        "No", "ISBN", "Judul", "Penulis", "Stok", "Rak", "Kategori"))
    garis()
    for i, b in enumerate(daftar, 1):
        print("  {:<4} {:<12} {:<30} {:<22} {:<6} {:<6} {}".format(
            i,
            b.get("isbn", ""),
            b.get("judul", "")[:29],
            b.get("penulis", "")[:21],
            b.get("stok", "0"),
            b.get("rak", ""),
            b.get("kategori", "")
        ))


def cetak_anggota(daftar):
    if not daftar:
        pesan_info("Tidak ada data anggota.")
        return
    print()
    print("  {:<14} {:<24} {:<26} {:<14} {:<12} {}".format(
        "ID", "Nama", "Email", "Telepon", "Tgl Daftar", "Status"))
    garis()
    for m in daftar:
        print("  {:<14} {:<24} {:<26} {:<14} {:<12} {}".format(
            m.get("id_anggota", ""),
            m.get("nama", "")[:23],
            m.get("email", "")[:25],
            m.get("telepon", ""),
            m.get("tgl_daftar", ""),
            m.get("status", "")
        ))


def cetak_pinjaman(daftar):
    if not daftar:
        pesan_info("Tidak ada data peminjaman.")
        return
    print()
    print("  {:<14} {:<14} {:<12} {:<12} {:<12} {}".format(
        "ID Pinjam", "ID Anggota", "ISBN", "Tgl Pinjam", "Tgl Kembali", "Status"))
    garis()
    for l in daftar:
        terlambat = l.get("terlambat", "")
        status = l.get("status", "")
        if terlambat:
            status = "TERLAMBAT " + terlambat
        print("  {:<14} {:<14} {:<12} {:<12} {:<12} {}".format(
            l.get("id_pinjam", ""),
            l.get("id_anggota", ""),
            l.get("isbn", ""),
            l.get("tgl_pinjam", ""),
            l.get("tgl_kembali", ""),
            status
        ))


# --- Menu Buku ---

def menu_buku():
    while True:
        header("Manajemen Buku")
        print("  [1] Lihat semua buku")
        print("  [2] Lihat buku urut A-Z (BST Inorder)")
        print("  [3] Tambah buku baru")
        print("  [4] Cari buku berdasarkan judul")
        print("  [5] Cari buku berdasarkan penulis")
        print("  [6] Update data buku")
        print("  [7] Hapus buku")
        print("  [8] Lihat detail buku")
        print("  [0] Kembali ke menu utama")
        print()
        pilihan = tanya("Pilih menu")

        if pilihan == "1":
            header("Daftar Semua Buku")
            cetak_buku(lihat_semua_buku())
            jeda()

        elif pilihan == "2":
            header("Daftar Buku Urut A-Z (BST Inorder Traversal)")
            cetak_buku(lihat_semua_buku(urut_az=True))
            jeda()

        elif pilihan == "3":
            header("Tambah Buku Baru")
            judul    = tanya("Judul buku")
            penulis  = tanya("Nama penulis")
            kategori = tanya("Kategori (Novel / Teknologi / dll)")
            tahun    = tanya("Tahun terbit")
            stok     = tanya("Jumlah stok")
            rak      = tanya("Nomor rak")
            isbn_in  = tanya("ISBN (kosongkan untuk auto-generate)")
            isbn = tambah_buku(judul, penulis, kategori, tahun, stok, rak,
                               isbn=isbn_in if isbn_in else None)
            pesan_ok("Buku berhasil ditambahkan. ISBN: " + isbn)
            jeda()

        elif pilihan == "4":
            header("Cari Buku Berdasarkan Judul")
            kata_kunci = tanya("Masukkan kata kunci judul")
            cetak_buku(cari_buku_judul(kata_kunci))
            jeda()

        elif pilihan == "5":
            header("Cari Buku Berdasarkan Penulis")
            kata_kunci = tanya("Masukkan kata kunci nama penulis")
            cetak_buku(cari_buku_penulis(kata_kunci))
            jeda()

        elif pilihan == "6":
            header("Update Data Buku")
            isbn = tanya("Masukkan ISBN buku yang akan diupdate")
            buku = detail_buku(isbn)
            if not buku:
                pesan_error("Buku tidak ditemukan.")
                jeda()
                continue
            print()
            print("  Data saat ini:")
            print("    Judul    : " + buku.get("judul", ""))
            print("    Penulis  : " + buku.get("penulis", ""))
            print("    Kategori : " + buku.get("kategori", ""))
            print("    Tahun    : " + buku.get("tahun", ""))
            print("    Stok     : " + buku.get("stok", ""))
            print("    Rak      : " + buku.get("rak", ""))
            print()
            print("  (Tekan Enter untuk melewati field yang tidak ingin diubah)")
            print()
            fields = {}
            for f in ["judul", "penulis", "kategori", "tahun", "stok", "rak"]:
                nilai = tanya(f)
                if nilai:
                    fields[f] = nilai
            if fields:
                update_buku(isbn, **fields)
                pesan_ok("Data buku berhasil diupdate.")
            else:
                pesan_info("Tidak ada perubahan.")
            jeda()

        elif pilihan == "7":
            header("Hapus Buku")
            isbn = tanya("Masukkan ISBN buku yang akan dihapus")
            buku = detail_buku(isbn)
            if buku:
                print()
                print("  Buku yang akan dihapus: " + buku.get("judul", "") + " (" + isbn + ")")
                konfirmasi = tanya("Yakin ingin menghapus? (y/n)")
                if konfirmasi.lower() == "y":
                    sukses, pesan = hapus_buku(isbn)
                    pesan_ok(pesan) if sukses else pesan_error(pesan)
                else:
                    pesan_info("Penghapusan dibatalkan.")
            else:
                pesan_error("Buku tidak ditemukan.")
            jeda()

        elif pilihan == "8":
            header("Detail Buku")
            isbn = tanya("Masukkan ISBN buku")
            b = detail_buku(isbn)
            if b:
                print()
                for k, v in b.items():
                    print("  {:<14}: {}".format(k, v))
                ant = lihat_antrian(isbn)
                print("  {:<14}: {} orang".format("Antrean", len(ant)))
                if ant:
                    print()
                    print("  Daftar antrean:")
                    for a in ant:
                        print("    - " + a["id_anggota"] + " (daftar: " + a["tgl_daftar"] + ")")
            else:
                pesan_error("Buku tidak ditemukan.")
            jeda()

        elif pilihan == "0":
            break
        else:
            pesan_error("Pilihan tidak valid.")
            jeda()


# --- Menu Anggota ---

def menu_anggota():
    while True:
        header("Manajemen Anggota")
        print("  [1] Lihat semua anggota")
        print("  [2] Daftarkan anggota baru")
        print("  [3] Lihat detail anggota")
        print("  [4] Update data anggota")
        print("  [5] Hapus anggota")
        print("  [0] Kembali ke menu utama")
        print()
        pilihan = tanya("Pilih menu")

        if pilihan == "1":
            header("Daftar Semua Anggota")
            cetak_anggota(lihat_semua_anggota())
            jeda()

        elif pilihan == "2":
            header("Daftarkan Anggota Baru")
            nama    = tanya("Nama lengkap")
            email   = tanya("Alamat email")
            telepon = tanya("Nomor telepon")
            id_a = daftar_anggota(nama, email, telepon)
            pesan_ok("Anggota berhasil didaftarkan. ID: " + id_a)
            jeda()

        elif pilihan == "3":
            header("Detail Anggota")
            id_a = tanya("Masukkan ID Anggota")
            m = detail_anggota(id_a)
            if m:
                print()
                for k, v in m.items():
                    print("  {:<16}: {}".format(k, v))
                aktif = [l for l in lihat_pinjaman_aktif() if l["id_anggota"] == id_a]
                print()
                print("  Pinjaman aktif: " + str(len(aktif)) + " buku")
                if aktif:
                    print()
                    cetak_pinjaman(aktif)
            else:
                pesan_error("Anggota tidak ditemukan.")
            jeda()

        elif pilihan == "4":
            header("Update Data Anggota")
            id_a = tanya("Masukkan ID Anggota")
            if not detail_anggota(id_a):
                pesan_error("Anggota tidak ditemukan.")
                jeda()
                continue
            print()
            print("  (Tekan Enter untuk melewati field yang tidak ingin diubah)")
            print()
            fields = {}
            for f in ["nama", "email", "telepon", "status"]:
                nilai = tanya(f)
                if nilai:
                    fields[f] = nilai
            if fields:
                sukses, pesan = update_anggota(id_a, **fields)
                pesan_ok(pesan) if sukses else pesan_error(pesan)
            else:
                pesan_info("Tidak ada perubahan.")
            jeda()

        elif pilihan == "5":
            header("Hapus Anggota")
            id_a = tanya("Masukkan ID Anggota")
            m = detail_anggota(id_a)
            if m:
                print()
                print("  Anggota yang akan dihapus: " + m.get("nama", "") + " (" + id_a + ")")
                konfirmasi = tanya("Yakin ingin menghapus? (y/n)")
                if konfirmasi.lower() == "y":
                    sukses, pesan = hapus_anggota(id_a)
                    pesan_ok(pesan) if sukses else pesan_error(pesan)
                else:
                    pesan_info("Penghapusan dibatalkan.")
            else:
                pesan_error("Anggota tidak ditemukan.")
            jeda()

        elif pilihan == "0":
            break
        else:
            pesan_error("Pilihan tidak valid.")
            jeda()


# --- Menu Peminjaman ---

def menu_peminjaman():
    while True:
        header("Peminjaman dan Pengembalian")
        print("  [1] Pinjam buku")
        print("  [2] Kembalikan buku")
        print("  [3] Lihat semua pinjaman aktif")
        print("  [4] Lihat buku yang terlambat dikembalikan")
        print("  [5] Lihat antrean peminjaman (Queue)")
        print("  [0] Kembali ke menu utama")
        print()
        pilihan = tanya("Pilih menu")

        if pilihan == "1":
            header("Pinjam Buku")
            id_a = tanya("ID Anggota")
            isbn = tanya("ISBN buku")
            hari = tanya("Durasi peminjaman dalam hari (kosong = 14 hari)")
            hari = int(hari) if hari.isdigit() else 14
            sukses, pesan = pinjam_buku(id_a, isbn, hari)
            pesan_ok(pesan) if sukses else pesan_error(pesan)
            jeda()

        elif pilihan == "2":
            header("Kembalikan Buku")
            id_pinjam = tanya("Masukkan ID Peminjaman (contoh: P1A2B3)")
            sukses, pesan = kembalikan_buku(id_pinjam)
            pesan_ok(pesan) if sukses else pesan_error(pesan)
            jeda()

        elif pilihan == "3":
            header("Semua Pinjaman Aktif")
            cetak_pinjaman(lihat_pinjaman_aktif())
            jeda()

        elif pilihan == "4":
            header("Buku Terlambat Dikembalikan")
            terlambat = lihat_pinjaman_terlambat()
            if not terlambat:
                pesan_ok("Tidak ada buku yang terlambat dikembalikan.")
            else:
                cetak_pinjaman(terlambat)
            jeda()

        elif pilihan == "5":
            header("Antrean Peminjaman (Queue - FIFO)")
            antrian = lihat_antrian()
            if not antrian:
                pesan_info("Tidak ada antrean saat ini.")
            else:
                print()
                print("  {:<14} {:<14} {:<12} {}".format(
                    "ID Antrian", "ID Anggota", "ISBN", "Tgl Daftar"))
                garis()
                for a in antrian:
                    print("  {:<14} {:<14} {:<12} {}".format(
                        a.get("id_antrian", ""),
                        a.get("id_anggota", ""),
                        a.get("isbn", ""),
                        a.get("tgl_daftar", "")
                    ))
            jeda()

        elif pilihan == "0":
            break
        else:
            pesan_error("Pilihan tidak valid.")
            jeda()


# --- Menu Laporan ---

def menu_laporan():
    while True:
        header("Laporan dan Statistik")
        print("  [1] Statistik perpustakaan")
        print("  [2] Riwayat aksi terbaru (Stack - LIFO)")
        print("  [0] Kembali ke menu utama")
        print()
        pilihan = tanya("Pilih menu")

        if pilihan == "1":
            header("Statistik Perpustakaan")
            s = statistik()
            print()
            print("  Total judul buku    : " + str(s["total_judul"]))
            print("  Total anggota       : " + str(s["total_anggota"]))
            print("  Sedang dipinjam     : " + str(s["pinjam_aktif"]))
            print("  Terlambat kembali   : " + str(s["terlambat"]))
            print("  Total antrean       : " + str(s["total_antrian"]))
            if s["top_books"]:
                print()
                print("  Top Buku Terpopuler:")
                for i, t in enumerate(s["top_books"], 1):
                    print("    " + str(i) + ". " + t["judul"] + " - " + str(t["total"]) + "x dipinjam")
            jeda()

        elif pilihan == "2":
            header("Riwayat Aksi (Stack - LIFO, 20 Terakhir)")
            riwayat = lihat_riwayat()
            if not riwayat:
                pesan_info("Belum ada riwayat aksi.")
            else:
                print()
                print("  {:<22} {:<22} {}".format("Timestamp", "Aksi", "Detail"))
                garis()
                for r in riwayat:
                    print("  {:<22} {:<22} {}".format(
                        r.get("timestamp", ""),
                        r.get("aksi", ""),
                        r.get("detail", "")
                    ))
            jeda()

        elif pilihan == "0":
            break
        else:
            pesan_error("Pilihan tidak valid.")
            jeda()


# --- Menu Utama ---

def main():
    load_all()

    while True:
        bersihkan_layar()
        garis_tebal()
        print("       SISTEM MANAJEMEN PERPUSTAKAAN")
        print("       Final Project UAS - Python CLI")
        garis_tebal()
        print()
        print("  [1] Manajemen Buku")
        print("  [2] Manajemen Anggota")
        print("  [3] Peminjaman dan Pengembalian")
        print("  [4] Laporan dan Statistik")
        print("  [0] Keluar")
        print()
        pilihan = tanya("Pilih menu")

        if   pilihan == "1":
            menu_buku()
        elif pilihan == "2":
            menu_anggota()
        elif pilihan == "3":
            menu_peminjaman()
        elif pilihan == "4":
            menu_laporan()
        elif pilihan == "0":
            print()
            print("  Terima kasih. Program selesai.")
            print()
            sys.exit(0)
        else:
            pesan_error("Pilihan tidak valid, coba lagi.")
            jeda()


# ============================================================
if __name__ == "__main__":
    main()
