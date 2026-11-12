import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Konfigurasi halaman dasar Streamlit
st.set_page_config(
    page_title="E-Commerce Performance Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# Mengatur tema seaborn
sns.set_theme(style='white')

# ==============================
# 1. HELPER FUNCTIONS
# ==============================
def create_revenue_category_df(df):
    """Menghitung total pendapatan per kategori produk."""
    revenue_df = df.groupby('product_category_name_english', as_index=False)['price'].sum()
    revenue_df = revenue_df.sort_values(by='price', ascending=False)
    return revenue_df

def create_review_delivery_df(df):
    """Menghitung rata-rata skor ulasan berdasarkan kategori pengiriman."""
    order_labels = [
        'Sangat Cepat (<=7 hari)', 
        'Cepat (8-15 hari)', 
        'Normal (16-30 hari)', 
        'Lambat (>30 hari)'
    ]
    review_df = df.groupby('delivery_category', observed=False)['review_score'].mean().reindex(order_labels).reset_index()
    return review_df

def create_rfm_df(df):
    """Membuat dataframe untuk RFM analysis."""
    if df.empty:
        return pd.DataFrame(columns=['customer_id', 'recency', 'frequency', 'monetary'])
    
    recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (recent_date - x.max()).days, # Recency
        'order_id': 'nunique', # Frequency
        'price': 'sum' # Monetary
    }).reset_index()
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    return rfm_df

# ==============================
# 2. LOAD DATA (DENGAN PATH DINAMIS)
# ==============================
# Mendapatkan direktori absolut dari file dashboard.py saat ini
current_dir = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_main_data():
    # Mencari main_data.csv relatif terhadap posisi dashboard.py
    # Karena main_data.csv biasanya satu folder dengan dashboard.py
    file_path = os.path.join(current_dir, "main_data.csv")
    
    # Jika tidak ada, coba cek apakah dijalankan dari luar (folder Submission)
    if not os.path.exists(file_path):
        file_path = os.path.join(current_dir, "Dashboard", "main_data.csv")
        
    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df.sort_values(by="order_purchase_timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

@st.cache_data
def load_geo_data():
    # Mencari geolocation_dataset.csv (biasanya ada di folder 'data' yang sejajar dengan folder 'Dashboard')
    # Mundur satu folder dari current_dir (keluar dari folder Dashboard), lalu masuk ke folder 'data'
    parent_dir = os.path.dirname(current_dir)
    file_path = os.path.join(parent_dir, "data", "geolocation_dataset.csv")
    
    # Jika folder 'data' ada di dalam folder Dashboard (atau sejajar jika script ini ada di root)
    if not os.path.exists(file_path):
        file_path = os.path.join(current_dir, "data", "geolocation_dataset.csv")
        
    # Jika file csv-nya langsung sejajar dengan file dashboard.py
    if not os.path.exists(file_path):
        file_path = os.path.join(current_dir, "geolocation_dataset.csv")

    try:
        geo_df = pd.read_csv(file_path)
        # Menghapus duplikat kode pos sesuai analisis di notebook
        geo_df = geo_df.drop_duplicates(subset=['geolocation_zip_code_prefix'])
        return geo_df
    except FileNotFoundError:
         raise FileNotFoundError(f"File geolocation_dataset.csv tidak ditemukan. Terakhir mencoba mencari di path: {file_path}. Tolong periksa lokasi file CSV Anda.")

all_df = load_main_data()
geo_df = load_geo_data()

min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

# ==============================
# 3. SIDEBAR & FILTER
# ==============================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=120)
    st.title("E-Commerce Dashboard")
    st.divider()
    st.subheader("Filter Data")
    
    date_range = st.date_input(
        label='Rentang Waktu Pesanan',
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        key='order_date_filter'
    )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = date_range[0] if isinstance(date_range, tuple) else date_range
        end_date = start_date

# Filter dataframe utama
main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) & 
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

revenue_category_df = create_revenue_category_df(main_df)
review_delivery_df = create_review_delivery_df(main_df)
rfm_df = create_rfm_df(main_df)

# ==============================
# 4. MAIN DASHBOARD UI
# ==============================
st.title("🛍️ E-Commerce Performance Dashboard")
st.markdown("Dashboard ini menyajikan metrik dan analisis kinerja penjualan E-Commerce di Brasil.")

st.subheader("Key Performance Indicators (KPI)")
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df['order_id'].nunique()
    st.metric("Total Pesanan", value=f"{total_orders:,}")

with col2:
    total_revenue = main_df['price'].sum()
    st.metric("Total Pendapatan (BRL)", value=f"R$ {total_revenue:,.2f}")

with col3:
    avg_review = main_df['review_score'].mean() if not main_df.empty else 0.0
    st.metric("Rata-rata Skor Ulasan", value=f"{avg_review:.2f} / 5.0")

st.divider()

tab1, tab2, tab3 = st.tabs([
    "📊 Performa Kategori Produk", 
    "🚚 Evaluasi Logistik", 
    "👥 RFM & Geospatial Analysis"
])

# TAB 1
with tab1:
    st.subheader("Performa Kategori Produk Berdasarkan Total Pendapatan")
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))
    top_5 = revenue_category_df.head(5)
    bottom_5 = revenue_category_df.sort_values(by='price', ascending=True).head(5)
    
    sns.barplot(x='price', y='product_category_name_english', data=top_5, hue='product_category_name_english', palette='viridis', ax=ax[0], legend=False)
    ax[0].set_title("Top 5 Kategori Pendapatan Tertinggi (BRL)", fontsize=13, fontweight='bold')
    ax[0].set_xlabel("Pendapatan (BRL)", fontsize=11)
    ax[0].set_ylabel("Kategori", fontsize=11)

    sns.barplot(x='price', y='product_category_name_english', data=bottom_5, hue='product_category_name_english', palette='magma', ax=ax[1], legend=False)
    ax[1].set_title("Bottom 5 Kategori Pendapatan Terendah (BRL)", fontsize=13, fontweight='bold')
    ax[1].set_xlabel("Pendapatan (BRL)", fontsize=11)
    ax[1].set_ylabel(None)

    plt.tight_layout()
    st.pyplot(fig)

# TAB 2
with tab2:
    st.subheader("Dampak Kecepatan Pengiriman terhadap Kepuasan Pelanggan")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='delivery_category', y='review_score', data=review_delivery_df, hue='delivery_category', palette='coolwarm', ax=ax, legend=False)
    ax.set_title("Rata-rata Skor Ulasan Berdasarkan Durasi Pengiriman", fontsize=14, fontweight='bold')
    ax.set_xlabel("Kategori Kecepatan Pengiriman", fontsize=12)
    ax.set_ylabel("Rata-rata Skor Ulasan", fontsize=12)
    ax.set_ylim(0, 5)
    
    for index, row in review_delivery_df.iterrows():
        ax.text(index, row.review_score + 0.1, f"{row.review_score:.2f}", color='black', ha="center", fontweight='bold')
        
    plt.tight_layout()
    st.pyplot(fig)

# TAB 3
with tab3:
    # 1. RFM Chart
    st.subheader("RFM Analysis (Recency, Frequency, Monetary) - Top Customers")
    
    fig_rfm, ax_rfm = plt.subplots(figsize=(10, 5))
    top_5_customers = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    
    sns.barplot(x="customer_id", y="monetary", data=top_5_customers, hue="customer_id", palette="magma", ax=ax_rfm, legend=False)
    ax_rfm.set_title("Top 5 Pelanggan Berdasarkan Total Belanja (Monetary)", fontsize=14, fontweight='bold')
    ax_rfm.set_xlabel("Customer ID (Unique)", fontsize=12)
    ax_rfm.set_ylabel("Total Belanja (BRL)", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    
    plt.tight_layout()
    st.pyplot(fig_rfm)
    
    st.divider()
    
    # 2. Geospatial Map
    st.subheader("Geospatial Analysis: Persebaran Lokasi Pelanggan")
    
    customers_geo_df = main_df.merge(
        geo_df, 
        left_on='customer_zip_code_prefix', 
        right_on='geolocation_zip_code_prefix', 
        how='inner'
    )
    
    fig_geo, ax_geo = plt.subplots(figsize=(10, 7))
    ax_geo.scatter(
        customers_geo_df['geolocation_lng'], 
        customers_geo_df['geolocation_lat'], 
        alpha=0.3, s=3, c='royalblue'
    )
    ax_geo.set_title('Peta Persebaran Lokasi Pelanggan E-Commerce (Brasil)', fontsize=14, fontweight='bold')
    ax_geo.set_xlabel('Longitude')
    ax_geo.set_ylabel('Latitude')
    ax_geo.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    st.pyplot(fig_geo)