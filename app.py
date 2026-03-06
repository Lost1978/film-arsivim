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
    
    /* Film Kartı Tasarımı */
    .film-card {
        background-color: #1a1c23;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    
    /* Checkbox'ı küçültme ve hizalama */
    [data-testid="stCheckbox"] {
        margin-bottom: -15px;
        margin-top: -5px;
    }
    [data-testid="stCheckbox"] p {
        font-size: 0.9rem !important; /* Yazıyı küçülttük */
        color: #888 !important;
    }
    
    /* Hassas İçerik Etiketi */
    .warning-badge {
        background-color: #e63946;
        color: white;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 5px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #000000; }
    
    /* İnce Divider */
    hr { margin: 10px 0px; border-color: #333; }
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

    if st.button("🎲 BANA BİR FİLM ÖNER"):
        izlenmemisler = filtered_df[filtered_df["İzlendi"] == "Hayır"]
        if not izlenmemisler.empty:
            oneri = izlenmemisler.sample(n=1).iloc[0]
            st.markdown(f"<div style='background-color:#000; border:1px dashed #fff; padding:15px; border-radius:10px; text-align:center;'><h3>✨ {oneri['İsim']} ({oneri['Yıl']})</h3></div>", unsafe_allow_html=True)
        else: st.info("Kriterlere uygun izlenmemiş film yok.")

    st.write(f"**{len(filtered_df)} Film**")

    # --- LİSTELEME ---
    for i, row in filtered_df.iterrows():
        st.markdown(f'<div class="film-card">', unsafe_allow_html=True)
        
        # Kartın üst kısmı: Başlık ve 18+ Etiketi
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            st.markdown(f"**🎬 {row['İsim']} ({row['Yıl']})**")
        with c2:
            if row['Hassas_Icerik'] == "Evet":
                st.markdown('<span class="warning-badge">18+</span>', unsafe_allow_html=True)
        
        st.markdown(f"<small style='color:#888;'>{row['Tür']} | {row['Bilgi']}</small>", unsafe_allow_html=True)
        
        # İzlenme Checkbox'ı (Küçültülmüş)
        is_checked = (row["İzlendi"] == "Evet")
        check = st.checkbox("İzlendi", value=is_checked, key=f"c_{i}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if check != is_checked:
            df.at[i, "İzlendi"] = "Evet" if check else "Hayır"
            save_data(df)
            st.rerun()

# --- 3. HIZLI SORGU ---
elif menu == "🔍 Hızlı Sorgu":
    st.subheader("İsimle Hızlı Arama")
    ara = st.text_input("Film adı...").strip().title()
    if ara:
        res = df[df["İsim"].str.contains(ara, na=False, case=False)]
        st.dataframe(res[["İsim", "Yıl", "Tür", "İzlendi"]], use_container_width=True)
