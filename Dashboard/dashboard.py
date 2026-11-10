import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema seaborn
sns.set_theme(style='white')

# ==============================
# 1. HELPER FUNCTIONS
# ==============================
def create_revenue_category_df(df):
    """Menghitung total pendapatan per kategori produk."""
    revenue_df = df.groupby('product_category_name_english')['price'].sum().reset_index()
    revenue_df = revenue_df.sort_values(by='price', ascending=False)
    return revenue_df

def create_review_delivery_df(df):
    """Menghitung rata-rata skor ulasan berdasarkan kategori pengiriman."""
    # Pastikan tipe data categorical tertangani dengan baik
    review_df = df.groupby('delivery_category', observed=False)['review_score'].mean().reset_index()
    return review_df

def create_rfm_df(df):
    """Membuat dataframe untuk RFM analysis."""
    recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (recent_date - x.max()).days, # Recency
        'order_id': 'nunique', # Frequency
        'price': 'sum' # Monetary
    }).reset_index()
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    return rfm_df

# ==============================
# 2. LOAD DATA
# ==============================
# Menggunakan cache agar data tidak dimuat ulang setiap kali ada interaksi
@st.cache_data
def load_data():
    # Menangani kemungkinan perbedaan path saat di-deploy vs di-run lokal
    try:
        df = pd.read_csv("Dashboard/main_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("main_data.csv")
    
    # Konversi kolom tanggal menjadi datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

all_df = load_data()

# Mengurutkan data berdasarkan tanggal pesanan
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Mendapatkan batas minimum dan maksimum tanggal untuk filter
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

# ==============================
# 3. SIDEBAR & FILTER
# ==============================
with st.sidebar:
    # Menambahkan logo/gambar (opsional, menggunakan emoji atau URL jika ada)
    st.image("https://cdn-icons-png.flaticon.com/512/3141/3141113.png", width=150)
    st.header("Filter Data")
    
    # Mengambil input rentang tanggal dari user
    start_date, end_date = st.date_input(
        label='Rentang Waktu Pesanan',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter dataframe utama berdasarkan input tanggal
main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) & 
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

# Menyiapkan berbagai dataframe untuk visualisasi dari data yang telah difilter
revenue_category_df = create_revenue_category_df(main_df)
review_delivery_df = create_review_delivery_df(main_df)
rfm_df = create_rfm_df(main_df)


# ==============================
# 4. MAIN DASHBOARD UI
# ==============================
st.title("🛍️ E-Commerce Performance Dashboard")
st.markdown("Dashboard ini menyajikan metrik dan analisis kinerja penjualan E-Commerce di Brasil.")

# --- Metrik Utama (KPI) ---
st.subheader("Key Performance Indicators (KPI)")
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df['order_id'].nunique()
    st.metric("Total Pesanan", value=f"{total_orders:,}")

with col2:
    total_revenue = main_df['price'].sum()
    st.metric("Total Pendapatan (BRL)", value=f"${total_revenue:,.2f}")

with col3:
    avg_review = main_df['review_score'].mean()
    st.metric("Rata-rata Skor Ulasan", value=f"{avg_review:.2f} / 5.0")

st.divider()

# --- Tab Layout ---
tab1, tab2, tab3 = st.tabs(["📊 Performa Kategori Produk", "🚚 Evaluasi Logistik", "👥 RFM Analysis (Customers)"])

# TAB 1: Pertanyaan 1 (Kategori Produk)
with tab1:
    st.subheader("Top 10 Kategori Produk dengan Pendapatan Tertinggi")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    top_10 = revenue_category_df.head(10)
    
    # Highlight warna menggunakan palet
    sns.barplot(
        x='price', 
        y='product_category_name_english', 
        data=top_10, 
        hue='product_category_name_english',
        palette='viridis', 
        ax=ax,
        legend=False
    )
    ax.set_title("Total Pendapatan per Kategori (BRL)", fontsize=14)
    ax.set_xlabel("Pendapatan", fontsize=12)
    ax.set_ylabel("Kategori", fontsize=12)
    st.pyplot(fig)
    
    with st.expander("Lihat Insight"):
        st.write("Produk kategori `bed_bath_table` dan `health_beauty` mendominasi pendapatan. Anggaran pemasaran sebaiknya difokuskan pada kategori-kategori unggulan ini.")

# TAB 2: Pertanyaan 2 (Pengiriman vs Kepuasan)
with tab2:
    st.subheader("Dampak Kecepatan Pengiriman terhadap Kepuasan Pelanggan")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        x='delivery_category', 
        y='review_score', 
        data=review_delivery_df, 
        hue='delivery_category',
        palette='coolwarm', 
        ax=ax,
        legend=False
    )
    ax.set_title("Rata-rata Skor Ulasan berdasarkan Durasi Pengiriman", fontsize=14)
    ax.set_xlabel("Kategori Kecepatan Pengiriman", fontsize=12)
    ax.set_ylabel("Rata-rata Skor Ulasan", fontsize=12)
    ax.set_ylim(0, 5)
    st.pyplot(fig)
    
    with st.expander("Lihat Insight"):
        st.write("Terdapat korelasi langsung antara waktu pengiriman dan ulasan positif. Pengiriman lambat (lebih dari 30 hari) berakibat sangat fatal pada kepuasan pembeli.")

# TAB 3: Advanced Analysis (RFM)
with tab3:
    st.subheader("RFM Analysis (Recency, Frequency, Monetary) - Top Customers")
    st.markdown("Mengelompokkan pelanggan terbaik berdasarkan nilai belanjanya (Monetary).")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    top_5_customers = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    
    sns.barplot(
        x="customer_id", 
        y="monetary", 
        data=top_5_customers,
        hue="customer_id",
        palette="magma",
        ax=ax,
        legend=False
    )
    
    ax.set_title("Top 5 Pelanggan Berdasarkan Total Belanja (Monetary)", fontsize=14)
    ax.set_xlabel("Customer ID (Unique)", fontsize=12)
    ax.set_ylabel("Total Belanja (BRL)", fontsize=12)
    # Merotasi label X agar ID tidak saling bertumpuk
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)
    
    st.caption("Pelanggan di atas merupakan VIP yang dapat diberikan program loyalti khusus.")
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema seaborn
sns.set_theme(style='white')

# ==============================
# 1. HELPER FUNCTIONS
# ==============================
def create_revenue_category_df(df):
    """Menghitung total pendapatan per kategori produk."""
    revenue_df = df.groupby('product_category_name_english')['price'].sum().reset_index()
    revenue_df = revenue_df.sort_values(by='price', ascending=False)
    return revenue_df

def create_review_delivery_df(df):
    """Menghitung rata-rata skor ulasan berdasarkan kategori pengiriman."""
    # Pastikan tipe data categorical tertangani dengan baik
    review_df = df.groupby('delivery_category', observed=False)['review_score'].mean().reset_index()
    return review_df

def create_rfm_df(df):
    """Membuat dataframe untuk RFM analysis."""
    recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (recent_date - x.max()).days, # Recency
        'order_id': 'nunique', # Frequency
        'price': 'sum' # Monetary
    }).reset_index()
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    return rfm_df

# ==============================
# 2. LOAD DATA
# ==============================
# Menggunakan cache agar data tidak dimuat ulang setiap kali ada interaksi
@st.cache_data
def load_data():
    # Menangani kemungkinan perbedaan path saat di-deploy vs di-run lokal
    try:
        df = pd.read_csv("Dashboard/main_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("main_data.csv")
    
    # Konversi kolom tanggal menjadi datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

all_df = load_data()

# Mengurutkan data berdasarkan tanggal pesanan
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Mendapatkan batas minimum dan maksimum tanggal untuk filter
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

# ==============================
# 3. SIDEBAR & FILTER
# ==============================
with st.sidebar:
    # Menambahkan logo/gambar (opsional, menggunakan emoji atau URL jika ada)
    st.image("https://cdn-icons-png.flaticon.com/512/3141/3141113.png", width=150)
    st.header("Filter Data")
    
    # Mengambil input rentang tanggal dari user
    start_date, end_date = st.date_input(
        label='Rentang Waktu Pesanan',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
        key='date_filter'
    )

# Filter dataframe utama berdasarkan input tanggal
main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) & 
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

# Menyiapkan berbagai dataframe untuk visualisasi dari data yang telah difilter
revenue_category_df = create_revenue_category_df(main_df)
review_delivery_df = create_review_delivery_df(main_df)
rfm_df = create_rfm_df(main_df)


# ==============================
# 4. MAIN DASHBOARD UI
# ==============================
st.title("🛍️ E-Commerce Performance Dashboard")
st.markdown("Dashboard ini menyajikan metrik dan analisis kinerja penjualan E-Commerce di Brasil.")

# --- Metrik Utama (KPI) ---
st.subheader("Key Performance Indicators (KPI)")
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df['order_id'].nunique()
    st.metric("Total Pesanan", value=f"{total_orders:,}")

with col2:
    total_revenue = main_df['price'].sum()
    st.metric("Total Pendapatan (BRL)", value=f"${total_revenue:,.2f}")

with col3:
    avg_review = main_df['review_score'].mean()
    st.metric("Rata-rata Skor Ulasan", value=f"{avg_review:.2f} / 5.0")

st.divider()

# --- Tab Layout ---
tab1, tab2, tab3 = st.tabs(["📊 Performa Kategori Produk", "🚚 Evaluasi Logistik", "👥 RFM Analysis (Customers)"])

# TAB 1: Pertanyaan 1 (Kategori Produk)
with tab1:
    st.subheader("Top 10 Kategori Produk dengan Pendapatan Tertinggi")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    top_10 = revenue_category_df.head(10)
    
    # Highlight warna menggunakan palet
    sns.barplot(
        x='price', 
        y='product_category_name_english', 
        data=top_10, 
        hue='product_category_name_english',
        palette='viridis', 
        ax=ax,
        legend=False
    )
    ax.set_title("Total Pendapatan per Kategori (BRL)", fontsize=14)
    ax.set_xlabel("Pendapatan", fontsize=12)
    ax.set_ylabel("Kategori", fontsize=12)
    st.pyplot(fig)
    
    with st.expander("Lihat Insight"):
        st.write("Produk kategori `bed_bath_table` dan `health_beauty` mendominasi pendapatan. Anggaran pemasaran sebaiknya difokuskan pada kategori-kategori unggulan ini.")

# TAB 2: Pertanyaan 2 (Pengiriman vs Kepuasan)
with tab2:
    st.subheader("Dampak Kecepatan Pengiriman terhadap Kepuasan Pelanggan")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        x='delivery_category', 
        y='review_score', 
        data=review_delivery_df, 
        hue='delivery_category',
        palette='coolwarm', 
        ax=ax,
        legend=False
    )
    ax.set_title("Rata-rata Skor Ulasan berdasarkan Durasi Pengiriman", fontsize=14)
    ax.set_xlabel("Kategori Kecepatan Pengiriman", fontsize=12)
    ax.set_ylabel("Rata-rata Skor Ulasan", fontsize=12)
    ax.set_ylim(0, 5)
    st.pyplot(fig)
    
    with st.expander("Lihat Insight"):
        st.write("Terdapat korelasi langsung antara waktu pengiriman dan ulasan positif. Pengiriman lambat (lebih dari 30 hari) berakibat sangat fatal pada kepuasan pembeli.")

# TAB 3: Advanced Analysis (RFM)
with tab3:
    st.subheader("RFM Analysis (Recency, Frequency, Monetary) - Top Customers")
    st.markdown("Mengelompokkan pelanggan terbaik berdasarkan nilai belanjanya (Monetary).")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    top_5_customers = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    
    sns.barplot(
        x="customer_id", 
        y="monetary", 
        data=top_5_customers,
        hue="customer_id",
        palette="magma",
        ax=ax,
        legend=False
    )
    
    ax.set_title("Top 5 Pelanggan Berdasarkan Total Belanja (Monetary)", fontsize=14)
    ax.set_xlabel("Customer ID (Unique)", fontsize=12)
    ax.set_ylabel("Total Belanja (BRL)", fontsize=12)
    # Merotasi label X agar ID tidak saling bertumpuk
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)
    
    st.caption("Pelanggan di atas merupakan VIP yang dapat diberikan program loyalti khusus.")
