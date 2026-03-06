import streamlit as st
import pandas as pd
import os
import random

# Sayfa Ayarları
st.set_page_config(page_title="Emre'nin Film Arşivi", page_icon="🎬", layout="centered")

# --- PREMIUM MOBIL TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Genel Arka Plan */
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Film Kartı */
    .film-card {
        background: #111111;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* Film Başlığı */
    .film-title { font-size: 1.1rem; font-weight: bold; color: #ffffff; margin-bottom: 2px; }
    
    /* Film Detayları */
    .film-meta { font-size: 0.85rem; color: #888; margin-bottom: 8px; }
    
    /* 18+ Etiketi */
    .age-badge {
        background: #ff0000;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
        float: right;
    }

    /* Checkbox'ı Küçültme ve Kartın İçine Hizalama */
    .stCheckbox {
        background: #1a1a1a;
        padding: 5px 10px;
        border-radius: 8px;
        border: 1px solid #333;
    }
    .stCheckbox p { font-size: 0.8rem !important; margin-bottom: 0px !important; }
    
    /* Menü ve Butonlar */
    [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #222; }
    .stButton>button { background: #ffffff; color: #000; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ YÖNETİMİ ---
def load_data():
    if os.path.exists("filmler.csv"):
        return pd.read_csv("filmler.csv")
    return pd.DataFrame(columns=["İsim", "Yıl", "Tür", "Bilgi", "İzlendi", "Hassas_Icerik"])

def save_data(df):
    df.to_csv("filmler.csv", index=False)

df = load_data()

# --- ÜST BAŞLIK ---
st.markdown("<h2 style='text-align: center;'>🎬 ARŞİVİM</h2>", unsafe_allow_html=True)

# --- YAN MENÜ ---
menu = st.sidebar.radio("BÖLÜMLER", ["🎥 Film Kaydet", "📋 Koleksiyon & Öneri", "🔍 Hızlı Sorgu"])

# --- 1. FİLM KAYDETME ---
if menu == "🎥 Film Kaydet":
    st.subheader("Yeni Ekle")
    with st.form("kayit"):
        isim = st.text_input("Film Adı").strip().title()
        c1, c2 = st.columns(2)
        yil = c1.number_input("Yıl", 1950, 2030, 2024)
        tur = c2.selectbox("Tür", ["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Suç", "Belgesel"])
        bilgi = st.text_area("Not")
        hassas = st.checkbox("18+ İçerik")
        if st.form_submit_button("Listeye Yaz"):
            if isim:
                yeni = pd.DataFrame([[isim, yil, tur, bilgi, "Hayır", "Evet" if hassas else "Hayır"]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                save_data(df)
                st.success("Kaydedildi!")
                st.rerun()

# --- 2. KOLEKSİYON & ÖNERİ ---
elif menu == "📋 Koleksiyon & Öneri":
    # Filtreler (Daha derli toplu)
    with st.expander("⚙️ Filtrele"):
        secilen_tur = st.multiselect("Tür", options=df["Tür"].unique())
        secilen_izlendi = st.radio("İzlenme", ["Hepsi", "İzlenmeyenler", "İzlenenler"], horizontal=True)
        secilen_hassas = st.radio("İçerik", ["Hepsi", "Temiz", "18+"], horizontal=True)

    filtered_df = df.copy()
    if secilen_tur: filtered_df = filtered_df[filtered_df["Tür"].isin(secilen_tur)]
    if secilen_izlendi == "İzlenmeyenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Hayır"]
    elif secilen_izlendi == "İzlenenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Evet"]
    if secilen_hassas == "Temiz": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Hayır"]
    elif secilen_hassas == "18+": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Evet"]

    # Öneri Butonu
    if st.button("🎲 RASTGELE ÖNER"):
        izlenmemis = filtered_df[filtered_df["İzlendi"] == "Hayır"]
        if not izlenmemis.empty:
            f = izlenmemis.sample(n=1).iloc[0]
            st.info(f"Önerim: {f['İsim']} ({f['Yıl']})")
        else: st.warning("Film bulunamadı.")

    st.markdown("---")

    # LİSTE (KART TASARIMI)
    for i, row in filtered_df.iterrows():
        # Her filmi bir kart (container) içine alıyoruz
        with st.container():
            # Kartın üst başlığı ve 18+ etiketi (HTML)
            badge_html = f'<span class="age-badge">18+</span>' if row['Hassas_Icerik'] == "Evet" else ""
            st.markdown(f"""
                <div class="film-card">
                    {badge_html}
                    <div class="film-title">🎬 {row['İsim']} ({row['Yıl']})</div>
                    <div class="film-meta">{row['Tür']} | {row['Bilgi']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # İzlenme kutusu - Kartın hemen altında ama bitişik
            is_checked = (row["İzlendi"] == "Evet")
            check = st.checkbox(f"İzlendi", value=is_checked, key=f"c_{i}")
            
            if check != is_checked:
                df.at[i, "İzlendi"] = "Evet" if check else "Hayır"
                save_data(df)
                st.rerun()

# --- 3. HIZLI SORGU ---
elif menu == "🔍 Hızlı Sorgu":
    ara = st.text_input("Film ara...").strip().title()
    if ara:
        res = df[df["İsim"].str.contains(ara, na=False, case=False)]
        st.write(res[["İsim", "Yıl", "Tür", "İzlendi"]])
