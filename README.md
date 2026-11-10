# 📊 E-Commerce Public Dataset - Data Analysis Project

Proyek ini merupakan tugas akhir dari kelas **Belajar Analisis Data dengan Python** di Dicoding. Proyek ini bertujuan untuk menganalisis **E-Commerce Public Dataset** guna menjawab pertanyaan bisnis terkait performa kategori produk dan efisiensi logistik. Selain itu, dilakukan analisis lanjutan menggunakan teknik **RFM Analysis (Recency, Frequency, Monetary)** untuk mengelompokkan pelanggan berdasarkan pola transaksi mereka.

## 👤 Identitas

- **Nama:** Briliant Priscilla
- **ID ASAH:** DS297B6X0355

## 📁 Struktur Direktori

Berikut merupakan struktur direktori proyek:

```text
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/
│   └── *.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

Keterangan:

- **`dashboard/`**: Berisi kode utama aplikasi dashboard berbasis Streamlit (`dashboard.py`) serta dataset hasil pemrosesan (`main_data.csv`).
- **`data/`**: Berisi kumpulan dataset mentah dalam format CSV yang digunakan selama proses analisis.
- **`notebook.ipynb`**: Jupyter Notebook yang memuat seluruh tahapan analisis data, mulai dari *Data Gathering, Assessing, Cleaning, Exploratory Data Analysis (EDA), Data Visualization*, hingga *Advanced Analysis* dan *Conclusion*.
- **`README.md`**: Dokumentasi proyek yang berisi informasi dan panduan penggunaan aplikasi.
- **`requirements.txt`**: Daftar library Python yang diperlukan untuk menjalankan proyek.
- **`url.txt`**: Berisi tautan dashboard yang telah di-deploy menggunakan Streamlit Community Cloud.

## 🚀 Cara Menjalankan Dashboard Secara Lokal

Ikuti langkah-langkah berikut untuk menjalankan dashboard di komputer lokal.

### 1. Clone atau Ekstrak Proyek

Pastikan seluruh berkas proyek sudah tersedia di komputer. Buka Terminal atau Command Prompt (CMD), kemudian arahkan direktori kerja ke folder utama proyek.

### 2. Membuat Virtual Environment

Disarankan untuk menggunakan *virtual environment* agar dependensi proyek tidak bercampur dengan proyek Python lainnya.

**Windows:**

```bash
python -m venv env
env\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Menginstal Dependencies

Setelah virtual environment berhasil diaktifkan, instal seluruh library yang dibutuhkan dengan menjalankan perintah:

```bash
pip install -r requirements.txt
```

### 4. Menjalankan Dashboard

Pastikan terminal berada di direktori utama proyek, kemudian jalankan perintah berikut:

```bash
streamlit run dashboard/dashboard.py
```

Setelah berhasil dijalankan, dashboard akan terbuka secara otomatis melalui browser default. Jika tidak terbuka secara otomatis, akses dashboard melalui alamat berikut:

**http://localhost:8501**

## 🌐 Deployment (Streamlit Community Cloud)

Dashboard proyek ini telah di-deploy menggunakan **Streamlit Community Cloud** sehingga dapat diakses secara publik.

Untuk mengakses dashboard, silakan buka tautan yang tercantum dalam berkas `url.txt` pada direktori utama proyek.

---

**Terima kasih telah mengunjungi proyek Data Analysis ini!**