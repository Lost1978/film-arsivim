import streamlit as st
import pandas as pd
import os
import random

# Sayfa Ayarları
st.set_page_config(page_title="Emre'nin Film Arşivi", page_icon="🎬", layout="centered")

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .film-card {
        background: #111111;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 5px;
    }
    .film-title { font-size: 1.1rem; font-weight: bold; color: #ffffff; }
    .age-badge {
        background: #ff0000; color: white; padding: 2px 6px;
        border-radius: 4px; font-size: 0.7rem; float: right;
    }
    .stCheckbox { background: #1a1a1a; padding: 5px; border-radius: 5px; border: 1px solid #333; }
    [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #222; }
    .stButton>button { background: #ffffff; color: #000; font-weight: bold; width: 100%; }
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

# --- YAN MENÜ ---
st.sidebar.title("🦅 KARTAL PANEL")
menu = st.sidebar.radio("MENÜ", ["🎥 Film Kaydet", "📋 Koleksiyon & Öneri", "✍️ Kayıtları Düzenle", "🔍 Hızlı Sorgu"])

# --- 1. FİLM KAYDETME ---
if menu == "🎥 Film Kaydet":
    st.subheader("Yeni Film")
    with st.form("kayit"):
        isim = st.text_input("Film Adı").strip().title()
        yil = st.number_input("Yıl", 1950, 2030, 2024)
        tur = st.selectbox("Tür", ["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Suç", "Belgesel", "Animasyon"])
        bilgi = st.text_area("Not")
        hassas = st.checkbox("18+ İçerik")
        if st.form_submit_button("Arşive Ekle"):
            if isim:
                yeni = pd.DataFrame([[isim, yil, tur, bilgi, "Hayır", "Evet" if hassas else "Hayır"]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                save_data(df)
                st.success("Kaydedildi!")
                st.rerun()

# --- 2. KOLEKSİYON & ÖNERİ (FİLTRELER GERİ GELDİ) ---
elif menu == "📋 Koleksiyon & Öneri":
    # FİLTRELEME ALANI
    with st.expander("🔍 Filtreleme Seçenekleri", expanded=False):
        f_col1, f_col2 = st.columns(2)
        secilen_tur = f_col1.multiselect("Tür Seç", options=df["Tür"].unique() if not df.empty else [])
        secilen_yil = f_col2.slider("Yıl Aralığı", 1950, 2026, (1950, 2026))
        secilen_hassas = st.radio("İçerik", ["Hepsi", "Temiz", "18+"], horizontal=True)
        secilen_izlendi = st.radio("Durum", ["Hepsi", "İzlenmeyenler", "İzlenenler"], horizontal=True)

    # Filtre Uygulama
    filtered_df = df.copy()
    if secilen_tur:
        filtered_df = filtered_df[filtered_df["Tür"].isin(secilen_tur)]
    filtered_df = filtered_df[(filtered_df["Yıl"] >= secilen_yil[0]) & (filtered_df["Yıl"] <= secilen_yil[1])]
    
    if secilen_hassas == "Temiz": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Hayır"]
    elif secilen_hassas == "18+": filtered_df = filtered_df[filtered_df["Hassas_Icerik"] == "Evet"]
        
    if secilen_izlendi == "İzlenmeyenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Hayır"]
    elif secilen_izlendi == "İzlenenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Evet"]

    # ÖNERİ BUTONU
    if st.button("🎲 BANA BİR FİLM ÖNER"):
        izlenmemisler = filtered_df[filtered_df["İzlendi"] == "Hayır"]
        if not izlenmemisler.empty:
            f = izlenmemisler.sample(n=1).iloc[0]
            st.info(f"Önerim: {f['İsim']} ({f['Yıl']})")
        else: st.warning("Seçilen filtrelere uygun izlenmemiş film yok.")

    st.markdown(f"**{len(filtered_df)} Film Listeleniyor**")

    # LİSTELEME
    for i, row in filtered_df.iterrows():
        with st.container():
            badge = '<span class="age-badge">18+</span>' if row['Hassas_Icerik'] == "Evet" else ""
            st.markdown(f'<div class="film-card">{badge}<div class="film-title">🎬 {row["İsim"]} ({row["Yıl"]})</div><div style="color:#888; font-size:0.85rem;">{row["Tür"]} | {row["Bilgi"]}</div></div>', unsafe_allow_html=True)
            check = st.checkbox("İzlendi", value=(row["İzlendi"] == "Evet"), key=f"c_{i}")
            if check != (row["İzlendi"] == "Evet"):
                df.at[i, "İzlendi"] = "Evet" if check else "Hayır"
                save_data(df)
                st.rerun()

# --- 3. DÜZENLEME MODU ---
elif menu == "✍️ Kayıtları Düzenle":
    st.subheader("Kayıt Güncelle veya Sil")
    if not df.empty:
        film_listesi = df["İsim"].tolist()
        secilen_film = st.selectbox("Düzenlenecek Filmi Seç", options=film_listesi)
        film_index = df[df["İsim"] == secilen_film].index[0]
        film_verisi = df.iloc[film_index]
        
        with st.form("duzenle_form"):
            yeni_isim = st.text_input("Film Adı", value=film_verisi["İsim"])
            yeni_yil = st.number_input("Yıl", 1950, 2030, value=int(film_verisi["Yıl"]))
            yeni_tur = st.selectbox("Tür", ["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Suç", "Belgesel", "Animasyon"], 
                                    index=["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Suç", "Belgesel", "Animasyon"].index(film_verisi["Tür"]))
            yeni_bilgi = st.text_area("Notlar", value=film_verisi["Bilgi"])
            yeni_hassas = st.checkbox("18+ İçerik", value=(film_verisi["Hassas_Icerik"] == "Evet"))
            silme_onayi = st.checkbox("⚠️ BU KAYDI TAMAMEN SİL")
            
            if st.form_submit_button("Güncelle"):
                if silme_onayi:
                    df = df.drop(film_index)
                    st.warning("Silindi.")
                else:
                    df.at[film_index, "İsim"] = yeni_isim
                    df.at[film_index, "Yıl"] = yeni_yil
                    df.at[film_index, "Tür"] = yeni_tur
                    df.at[film_index, "Bilgi"] = yeni_bilgi
                    df.at[film_index, "Hassas_Icerik"] = "Evet" if yeni_hassas else "Hayır"
                    st.success("Güncellendi!")
                save_data(df)
                st.rerun()

# --- 4. HIZLI SORGU ---
elif menu == "🔍 Hızlı Sorgu":
    ara = st.text_input("Film ara...")
    if ara:
        res = df[df["İsim"].str.contains(ara, na=False, case=False)]
        st.dataframe(res[["İsim", "Yıl", "Tür", "İzlendi"]], use_container_width=True)
