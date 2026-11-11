import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

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
# 2. LOAD DATA
# ==============================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Dashboard/main_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("main_data.csv")
    
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df.sort_values(by="order_purchase_timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

all_df = load_data()

min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

# ==============================
# 3. SIDEBAR & FILTER (TUNGGAL)
# ==============================
with st.sidebar:
    # Menampilkan gambar logo yang valid dan selalu termuat
    st.image(
        "https://cdn-icons-png.flaticon.com/512/3081/3081559.png",
        width=120
    )
    st.title("E-Commerce Dashboard")
    st.divider()
    st.subheader("Filter Data")
    
    # Mengambil input rentang tanggal dengan validasi tuple 2 tanggal
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
    st.metric("Total Pendapatan (BRL)", value=f"R$ {total_revenue:,.2f}")

with col3:
    avg_review = main_df['review_score'].mean() if not main_df.empty else 0.0
    st.metric("Rata-rata Skor Ulasan", value=f"{avg_review:.2f} / 5.0")

st.divider()

# --- Tab Layout ---
tab1, tab2, tab3 = st.tabs([
    "📊 Performa Kategori Produk", 
    "🚚 Evaluasi Logistik", 
    "👥 RFM Analysis (Customers)"
])

# TAB 1: Pertanyaan 1 (Kategori Produk)
with tab1:
    st.subheader("Performa Kategori Produk Berdasarkan Total Pendapatan")
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))
    top_5 = revenue_category_df.head(5)
    bottom_5 = revenue_category_df.sort_values(by='price', ascending=True).head(5)
    
    sns.barplot(
        x='price', 
        y='product_category_name_english', 
        data=top_5, 
        hue='product_category_name_english',
        palette='viridis', 
        ax=ax[0],
        legend=False
    )
    ax[0].set_title("Top 5 Kategori Pendapatan Tertinggi (BRL)", fontsize=13, fontweight='bold')
    ax[0].set_xlabel("Pendapatan (BRL)", fontsize=11)
    ax[0].set_ylabel("Kategori", fontsize=11)

    sns.barplot(
        x='price', 
        y='product_category_name_english', 
        data=bottom_5, 
        hue='product_category_name_english',
        palette='magma', 
        ax=ax[1],
        legend=False
    )
    ax[1].set_title("Bottom 5 Kategori Pendapatan Terendah (BRL)", fontsize=13, fontweight='bold')
    ax[1].set_xlabel("Pendapatan (BRL)", fontsize=11)
    ax[1].set_ylabel(None)

    plt.tight_layout()
    st.pyplot(fig)
    
    with st.expander("Lihat Insight"):
        st.write(
            "Produk kategori `health_beauty`, `watches_gifts`, dan `bed_bath_table` mendominasi total pendapatan. "
            "Sebaliknya, `security_and_services` dan `fashion_childrens_clothes` memiliki kontribusi terendah."
        )

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
    ax.set_title("Rata-rata Skor Ulasan Berdasarkan Durasi Pengiriman", fontsize=14, fontweight='bold')
    ax.set_xlabel("Kategori Kecepatan Pengiriman", fontsize=12)
    ax.set_ylabel("Rata-rata Skor Ulasan", fontsize=12)
    ax.set_ylim(0, 5)
    plt.tight_layout()
    st.pyplot(fig)
    
    with st.expander("Lihat Insight"):
        st.write(
            "Terdapat korelasi negatif yang kuat antara durasi pengiriman dan ulasan pelanggan. "
            "Pengiriman lambat (lebih dari 30 hari) menurunkan skor ulasan rata-rata secara drastis hingga ke kisaran 2,17."
        )

# TAB 3: Advanced Analysis (RFM)
with tab3:
    st.subheader("RFM Analysis (Recency, Frequency, Monetary) - Top Customers")
    st.markdown("Mengelompokkan pelanggan terbaik berdasarkan total nilai belanjanya (*Monetary*).")
    
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
    
    ax.set_title("Top 5 Pelanggan Berdasarkan Total Belanja (Monetary)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Customer ID (Unique)", fontsize=12)
    ax.set_ylabel("Total Belanja (BRL)", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.caption("Pelanggan di atas merupakan segmen prioritas yang dapat diberikan program retensi dan loyalti khusus.")