import streamlit as st
import pandas as pd
import os
import random

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Emre'nin Film Arşivi", page_icon="🎬", layout="centered")

# --- GELİŞMİŞ ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Film Kartı Tasarımı */
    .film-card {
        background-color: #1a1c23;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 15px;
        position: relative;
    }
    
    /* İzlenme Durumu Yazısı ve Checkbox Düzeni */
    .stCheckbox {
        margin-top: -20px;
        padding-bottom: 10px;
    }

    /* Hassas İçerik Etiketi */
    .warning-badge {
        background-color: #e63946;
        color: white;
        padding: 2px 10px;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Öneri Kutusu */
    .suggest-box {
        background-color: #000000;
        border: 2px dashed #ffffff;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #000000; }
    
    /* Butonlar */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #ffffff; color: #000000; }
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

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center;'>🦅 EMRE'NİN FİLM ARŞİVİ</h1>", unsafe_allow_html=True)

# --- MENÜ ---
menu = st.sidebar.radio("MENÜ", ["🎥 Film Kaydet", "📋 Koleksiyon & Öneri"])

# --- 1. FİLM KAYDETME ---
if menu == "🎥 Film Kaydet":
    st.subheader("Yeni Film Ekle")
    with st.form("yeni_film"):
        isim = st.text_input("Film Adı").strip().title()
        col1, col2 = st.columns(2)
        yil = col1.number_input("Yıl", 1950, 2030, 2024)
        tur = col2.selectbox("Tür", ["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Suç", "Belgesel", "Animasyon"])
        bilgi = st.text_area("Film Özeti / Notlar")
        hassas = st.checkbox("Hassas/Cinsel İçerik Barındırıyor")
        
        if st.form_submit_button("Arşive Gönder"):
            if isim:
                yeni = pd.DataFrame([[isim, yil, tur, bilgi, "Hayır", "Evet" if hassas else "Hayır"]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                save_data(df)
                st.success("Film başarıyla eklendi!")
                st.rerun()

# --- 2. KOLEKSİYON & ÖNERİ ---
elif menu == "📋 Koleksiyon & Öneri":
    # --- FİLTRELEME ---
    with st.expander("🔍 Filtreleme Seçenekleri", expanded=False):
        f_col1, f_col2 = st.columns(2)
        secilen_tur = f_col1.multiselect("Tür Seç", options=df["Tür"].unique())
        secilen_yil = f_col2.slider("Yıl Aralığı", 1950, 2026, (1950, 2026))
        secilen_hassas = st.radio("Hassas İçerik", ["Hepsi", "Temiz", "18+"], horizontal=True)
        secilen_izlendi = st.radio("Durum", ["Hepsi", "İzlenmeyenler", "İzlenenler"], horizontal=True)

    # Filtreleme Mantığı
    filtered_df = df.copy()
    if secilen_tur:
        filtered_df = filtered_df[filtered_df["Tür"].isin(secilen_tur)]
    filtered_df = filtered_df[(filtered_df["Yıl"] >= secilen_yil[0]) & (filtered_df["Yıl"] <= secilen_yil[1])]
    
    if secilen_hassas == "Temiz": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Hayır"]
    elif secilen_hassas == "18+": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Evet"]
        
    if secilen_izlendi == "İzlenmeyenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Hayır"]
    elif secilen_izlendi == "İzlenenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Evet"]

    # --- FİLM ÖNER BUTONU ---
    if st.button("🎲 BANA BİR FİLM ÖNER"):
        izlenmemisler = filtered_df[filtered_df["İzlendi"] == "Hayır"]
        if not izlenmemisler.empty:
            oneri = izlenmemisler.sample(n=1).iloc[0]
            st.markdown(f"""
            <div class="suggest-box">
                <h2 style='color: white; margin:0;'>✨ Önerilen ✨</h2>
                <h1 style='color: #FFFFFF;'>{oneri['İsim']} ({oneri['Yıl']})</h1>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Kriterlere uygun izlenmemiş film yok.")

    st.write(f"**{len(filtered_df)} Film Bulundu**")
    
    # --- LİSTELEME ---
    for i, row in filtered_df.iterrows():
        # Her film için bir 'container' açıyoruz ki checkbox kartın içinde kalsın
        with st.container():
            # Kartın üst kısmını (HTML) çiziyoruz
            st.markdown(f"""
            <div class="film-card">
                {f'<div class="warning-badge">⚠️ 18+</div>' if row['Hassas_Icerik'] == "Evet" else ""}
                <div style="font-size: 1.2rem; font-weight: bold; color: white;">🎬 {row['İsim']} ({row['Yıl']})</div>
                <div style="color: #888; font-size: 0.9rem; margin-bottom: 10px;">{row['Tür']} | {row['Bilgi']}</div>
            """, unsafe_allow_html=True)
            
            # Kartın içindeki Checkbox
            is_checked = (row["İzlendi"] == "Evet")
            check = st.checkbox("İzlendi", value=is_checked, key=f"c_{i}")
            
            # Kartın HTML kapanışını yapıyoruz
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Veri Güncelleme
            yeni_durum = "Evet" if check else "Hayır"
            if yeni_durum != row["İzlendi"]:
                df.at[i, "İzlendi"] = yeni_durum
                save_data(df)
                st.rerun()
