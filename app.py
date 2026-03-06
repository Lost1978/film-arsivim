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
    
    /* İzlenme Durumu Kutucuğu Style */
    .status-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
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
    
    /* Sidebar Düzenleme */
    [data-testid="stSidebar"] { background-color: #000000; }
    
    /* Butonlar */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ YÖNETİMİ ---
def load_data():
    if os.path.exists("filmler.csv"):
        df = pd.read_csv("filmler.csv")
        # Eski verilerde Hassas_Icerik sütunu yoksa ekle
        if "Hassas_Icerik" not in df.columns:
            df["Hassas_Icerik"] = "Hayır"
        return df
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
            else:
                st.error("Film adı girmelisin!")

# --- 2. KOLEKSİYON & ÖNERİ (YENİLENEN KISIM) ---
elif menu == "📋 Koleksiyon & Öneri":
    st.subheader("Koleksiyon Yönetimi ve Öneriler")
    
    # --- FİLTRELEME ALANI ---
    with st.expander("🔍 Filtreleme Seçenekleri", expanded=False):
        f_col1, f_col2 = st.columns(2)
        secilen_tur = f_col1.multiselect("Tür Seç", options=df["Tür"].unique())
        secilen_yil = f_col2.slider("Yıl Aralığı", int(df["Yıl"].min() if not df.empty else 1950), 2026, (1950, 2026))
        secilen_hassas = st.radio("Hassas İçerik Filtresi", ["Hepsi", "Sadece Temizler", "Sadece Hassaslar"], horizontal=True)
        secilen_izlendi = st.radio("İzlenme Durumu", ["Hepsi", "Sadece İzlenmeyenler", "Sadece İzlenenler"], horizontal=True)

    # Filtre Uygulama
    filtered_df = df.copy()
    if secilen_tur:
        filtered_df = filtered_df[filtered_df["Tür"].isin(secilen_tur)]
    filtered_df = filtered_df[(filtered_df["Yıl"] >= secilen_yil[0]) & (filtered_df["Yıl"] <= secilen_yil[1])]
    
    if secilen_hassas == "Sadece Temizler":
        filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Hayır"]
    elif secilen_hassas == "Sadece Hassaslar":
        filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Evet"]
        
    if secilen_izlendi == "Sadece İzlenmeyenler":
        filtered_df = filtered_df[filtered_df["İzlendi"] == "Hayır"]
    elif secilen_izlendi == "Sadece İzlenenler":
        filtered_df = filtered_df[filtered_df["İzlendi"] == "Evet"]

    # --- FİLM ÖNER BUTONU ---
    st.markdown("---")
    if st.button("🎲 BANA BİR FİLM ÖNER"):
        izlenmemisler = filtered_df[filtered_df["İzlendi"] == "Hayır"]
        if not izlenmemisler.empty:
            oneri = izlenmemisler.sample(n=1).iloc[0]
            st.markdown(f"""
            <div class="suggest-box">
                <h2 style='color: white; margin:0;'>✨ Önerilen Film ✨</h2>
                <h1 style='color: #FFFFFF;'>{oneri['İsim']} ({oneri['Yıl']})</h1>
                <p>Tür: {oneri['Tür']} | {oneri['Bilgi']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Filtrelere uygun izlenmemiş film bulamadım Emre.")

    # --- KOLEKSİYON LİSTESİ (TABLO YERİNE KART SİSTEMİ) ---
    st.write(f"**Toplam {len(filtered_df)} film listeleniyor.**")
    
    for i, row in filtered_df.iterrows():
        with st.container():
            # Kart Görünümü
            is_checked = True if row["İzlendi"] == "Evet" else False
            
            st.markdown(f"""
            <div class="film-card">
                <span style="font-size: 1.2rem; font-weight: bold;">🎬 {row['İsim']} ({row['Yıl']})</span>
                <p style="color: #bbb; margin-bottom: 5px;">{row['Tür']} | {row['Bilgi']}</p>
                {f'<div class="warning-badge">⚠️ 18+ CONTENT</div>' if row['Hassas_Icerik'] == "Evet" else ""}
            </div>
            """, unsafe_allow_html=True)
            
            # İzlenme Durumu Düzenleme (Kutucuklu)
            check = st.checkbox(f"İzlendi İşaretle", value=is_checked, key=f"check_{i}")
            
            # Değişiklik varsa kaydet
            current_status = "Evet" if check else "Hayır"
            if current_status != row["İzlendi"]:
                df.at[i, "İzlendi"] = current_status
                save_data(df)
                st.rerun()

# --- 3. HIZLI SORGU ---
elif menu == "🔍 Hızlı Sorgu":
    st.subheader("İsimle Hızlı Arama")
    ara = st.text_input("Film adı girin...").strip().title()
    if ara:
        res = df[df["İsim"].str.contains(ara, na=False)]
        st.write(res)
