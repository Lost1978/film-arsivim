import streamlit as st
import pandas as pd
import os
import random

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Emre'nin Film Arşivi", page_icon="🎬", layout="centered")

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Film Kartı Benzeri Bölüm */
    .stColumn {
        background-color: #1a1c23;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    
    /* Hassas İçerik Etiketi */
    .warning-badge {
        background-color: #e63946;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-bottom: 5px;
        display: inline-block;
    }

    /* Öneri Kutusu */
    .suggest-box {
        background-color: #000000;
        border: 2px dashed #ffffff;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #000000; }
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

# --- MENÜ (3 SEKME DE BURADA) ---
menu = st.sidebar.radio("MENÜ", ["🎥 Film Kaydet", "📋 Koleksiyon & Öneri", "🔍 Hızlı Sorgu"])

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
    with st.expander("🔍 Filtreleme Seçenekleri"):
        f_col1, f_col2 = st.columns(2)
        secilen_tur = f_col1.multiselect("Tür Seç", options=df["Tür"].unique())
        secilen_yil = f_col2.slider("Yıl Aralığı", 1950, 2026, (1950, 2026))
        secilen_hassas = st.radio("Hassas İçerik", ["Hepsi", "Temiz", "18+"], horizontal=True)
        secilen_izlendi = st.radio("Durum", ["Hepsi", "İzlenmeyenler", "İzlenenler"], horizontal=True)

    filtered_df = df.copy()
    if secilen_tur: filtered_df = filtered_df[filtered_df["Tür"].isin(secilen_tur)]
    filtered_df = filtered_df[(filtered_df["Yıl"] >= secilen_yil[0]) & (filtered_df["Yıl"] <= secilen_yil[1])]
    if secilen_hassas == "Temiz": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Hayır"]
    elif secilen_hassas == "18+": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Evet"]
    if secilen_izlendi == "İzlenmeyenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Hayır"]
    elif secilen_izlendi == "İzlenenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Evet"]

    # --- ÖNERİ BUTONU ---
    if st.button("🎲 BANA BİR FİLM ÖNER"):
        izlenmemisler = filtered_df[filtered_df["İzlendi"] == "Hayır"]
        if not izlenmemisler.empty:
            oneri = izlenmemisler.sample(n=1).iloc[0]
            st.markdown(f"<div class='suggest-box'><h2>✨ Önerilen ✨</h2><h3>{oneri['İsim']} ({oneri['Yıl']})</h3></div>", unsafe_allow_html=True)
        else: st.info("Kriterlere uygun izlenmemiş film yok.")

    st.divider()

    # --- LİSTELEME (GÜNCELLENEN KUTU TASARIMI) ---
    for i, row in filtered_df.iterrows():
        # st.expander veya st.container kullanarak her filmi bir kutu içine alıyoruz
        with st.expander(f"🎬 {row['İsim']} ({row['Yıl']})", expanded=True):
            col_info, col_check = st.columns([0.8, 0.2])
            
            with col_info:
                if row['Hassas_Icerik'] == "Evet":
                    st.markdown('<span class="warning-badge">⚠️ 18+</span>', unsafe_allow_html=True)
                st.write(f"**Tür:** {row['Tür']}")
                st.write(f"**Bilgi:** {row['Bilgi']}")
            
            with col_check:
                is_checked = (row["İzlendi"] == "Evet")
                check = st.checkbox("İzlendi", value=is_checked, key=f"c_{i}")
                
                if check != is_checked:
                    df.at[i, "İzlendi"] = "Evet" if check else "Hayır"
                    save_data(df)
                    st.rerun()

# --- 3. HIZLI SORGU (GERİ GELDİ) ---
elif menu == "🔍 Hızlı Sorgu":
    st.subheader("İsimle Hızlı Arama")
    ara = st.text_input("Film adı girin...").strip().title()
    if ara:
        res = df[df["İsim"].str.contains(ara, na=False, case=False)]
        if not res.empty:
            st.table(res[["İsim", "Yıl", "Tür", "İzlendi"]])
        else:
            st.warning("Sonuç bulunamadı.")
