import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. KONFIGURASI HALAMAN & LOAD DATA
# ==========================================
st.set_page_config(page_title="Dashboard Analytics GoPay", layout="wide")

st.title("📱 GoPay User Analytics Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis hasil kuesioner dan data ulasan aplikasi GoPay.")

@st.cache_data
def load_data():
    # Load dataset hasil cleaning kelompokmu
    survey_df = pd.read_csv("survey_gopay_clean.csv")
    review_df = pd.read_csv("review_gopay_clean (1).csv")
    
    # Bersihkan header kolom survey dari spasi/quote berlebih jika ada
    survey_df.columns = [col.strip().strip('"') for col in survey_df.columns]
    
    # Kolom Likert (asumsi dari kolom ke-5 ke atas) diubah jadi numerik
    for col in survey_df.columns[5:]:
        survey_df[col] = pd.to_numeric(survey_df[col], errors='coerce')
        
    return survey_df, review_df

try:
    df_survey, df_review = load_data()
except Exception as e:
    st.error(f"Gagal memuat file CSV. Pastikan file berada di folder yang sama. Error: {e}")
    st.stop()

# ==========================================
# 2. SIDEBAR FILTER (Widget Interaktif - Langkah 8)
# ==========================================
st.sidebar.header("🔍 Filter Data Responden")

# Filter Jenis Kelamin
gender_options = ["Semua"] + list(df_survey["Jenis Kelamin"].unique())
selected_gender = st.sidebar.selectbox("Pilih Jenis Kelamin:", gender_options)

# Filter Usia
age_options = ["Semua"] + list(df_survey["Usia"].unique())
selected_age = st.sidebar.selectbox("Pilih Kategori Usia:", age_options)

# Menerapkan Filter ke DataFrame Survey
df_filtered = df_survey.copy()
if selected_gender != "Semua":
    df_filtered = df_filtered[df_filtered["Jenis Kelamin"] == selected_gender]
if selected_age != "Semua":
    df_filtered = df_filtered[df_filtered["Usia"] == selected_age]

# ==========================================
# 3. LAYOUT UTAMA & GRAFIK (Langkah 7 & 8)
# ==========================================

# Ringkasan KPI singkat
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Total Responden Terfilter", value=len(df_filtered))
kpi2.metric(label="Total Responden Asli", value=len(df_survey))
kpi3.metric(label="Total Ulasan Di-Scrape", value=len(df_review))

st.markdown("---")

# --- BAGIAN 1: PROFIL RESPONDEN (Pie Chart) ---
st.subheader("📊 Profil Demografi Responden")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Distribusi Jenis Kelamin**")
    if not df_filtered.empty and df_filtered["Jenis Kelamin"].nunique() > 0:
        fig, ax = plt.subplots(figsize=(6, 4))
        gender_data = df_filtered["Jenis Kelamin"].value_counts()
        ax.pie(gender_data, labels=gender_data.index, autopct='%1.1f%%', startangle=90, 
               colors=sns.color_palette("pastel"))
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.warning("Data tidak tersedia untuk kombinasi filter ini.")

with col2:
    st.markdown("**Distribusi Usia**")
    if not df_filtered.empty and df_filtered["Usia"].nunique() > 0:
        fig, ax = plt.subplots(figsize=(6, 4))
        age_data = df_filtered["Usia"].value_counts()
        ax.pie(age_data, labels=age_data.index, autopct='%1.1f%%', startangle=90, 
               colors=sns.color_palette("Set2"))
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.warning("Data tidak tersedia untuk kombinasi filter ini.")

st.markdown("---")

# --- BAGIAN 2: HASIL KUESIONER LIKERT (Bar Plot) ---
st.subheader("📈 Analisis Hasil Kuesioner Skala Likert")

# Mengambil kolom pertanyaan kuesioner (kolom ke-5 sampai akhir)
pertanyaan_cols = df_survey.columns[5:]

if len(pertanyaan_cols) > 0:
    # Dropdown untuk memilih pertanyaan kuesioner yang ingin dilihat grafiknya
    selected_q = st.selectbox("Pilih Pertanyaan Kuesioner untuk Divisualisasikan:", pertanyaan_cols)
    
    if not df_filtered.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        # Hitung frekuensi nilai skala 1-5
        likert_counts = df_filtered[selected_q].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        
        sns.barplot(x=likert_counts.index, y=likert_counts.values, ax=ax, palette="viridis")
        ax.set_title(f"Distribusi Jawaban:\n{selected_q}", fontsize=12)
        ax.set_xlabel("Skala Likert (1-5)")
        ax.set_ylabel("Jumlah Responden")
        
        # Beri label angka di atas bar
        for p in ax.patches:
            ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points')
            
        st.pyplot(fig)
    else:
        st.warning("Tidak ada data responden yang memenuhi filter untuk menampilkan grafik Likert.")
else:
    st.info("Kolom kuesioner Likert tidak terdeteksi secara otomatis. Pastikan urutan kolom sesuai.")

st.markdown("---")

# --- BAGIAN 3: PREVIEW DATA REVIEW (Langkah 3 & 4) ---
st.subheader("💬 Sampel Data Ulasan Play Store / App Store")
st.dataframe(df_review.head(100), use_container_width=True)