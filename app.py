import streamlit as st
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Emre'nin Film Arşivi", page_icon="🎬", layout="wide")

# Beşiktaş Temalı CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    .stButton>button { background-color: #000000; color: #ffffff; width: 100%; border-radius: 5px; }
    .stTextInput>div>div>input { background-color: #f0f0f0; }
    .warning-box { 
        background-color: #ff4b4b; 
        color: white; 
        padding: 10px; 
        border-radius: 5px; 
        font-weight: bold; 
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Veriyi Yükleme (Örnek olarak yerel CSV kullanıyoruz, Google Sheets entegrasyonu için kütüphane eklenir)
@st.cache_data
def load_data():
    try:
        return pd.read_csv("filmler.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["İsim", "Yıl", "Tür", "Bilgi", "İzlendi", "Hassas_Icerik"])

df = load_data()

# --- YAN MENÜ ---
st.sidebar.title("🏁 Menü")
sayfa = st.sidebar.radio("Git:", ["Film Ekle", "Arşivde Ara", "Tüm Liste"])

# --- FİLM EKLEME SAYFASI ---
if sayfa == "Film Ekle":
    st.header("🎬 Yeni Film Kaydet")
    col1, col2 = st.columns(2)
    
    with col1:
        isim = st.text_input("Film Adı").strip().title()
        yil = st.number_input("Yıl", 1900, 2026, 2024)
        tur = st.selectbox("Tür", ["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Diğer"])
    
    with col2:
        bilgi = st.text_area("Kısa Bilgi/Notlar")
        hassas = st.checkbox("⚠️ Hassas/Cinsel İçerik Barındırıyor")
    
    if st.button("Listeye Ekle"):
        yeni_veri = pd.DataFrame([[isim, yil, tur, bilgi, "Hayır", "Evet" if hassas else "Hayır"]], 
                                columns=df.columns)
        df = pd.concat([df, yeni_veri], ignore_index=True)
        df.to_csv("filmler.csv", index=False)
        st.success("Film başarıyla kaydedildi!")

# --- ARAMA SAYFASI ---
elif sayfa == "Arşivde Ara":
    st.header("🔍 Film Sorgula")
    arama = st.text_input("Film ismi yazın...").strip().title()
    
    if arama:
        sonuc = df[df['İsim'].str.contains(arama, na=False)]
        if not sonuc.empty:
            for i, row in sonuc.iterrows():
                with st.expander(f"{row['İsim']} ({row['Yıl']})"):
                    st.write(f"**Tür:** {row['Tür']}")
                    st.write(f"**Not:** {row['Bilgi']}")
                    st.write(f"**İzlendi mi?:** {row['İzlendi']}")
                    
                    if row['Hassas_Icerik'] == "Evet":
                        st.markdown('<div class="warning-box">⚠️ UYARI: BU FİLM HASSAS İÇERİK BARINDIRIR!</div>', unsafe_allow_html=True)
                    
                    if st.button("İzlendi Olarak İşaretle", key=f"btn_{i}"):
                        df.at[i, "İzlendi"] = "Evet"
                        df.to_csv("filmler.csv", index=False)
                        st.rerun()
        else:
            st.warning("Bu film listede yok.")

# --- TÜM LİSTE ---
elif sayfa == "Tüm Liste":
    st.header("📋 Tüm Arşiv")
    filtre = st.multiselect("Türleri Filtrele", options=df["Tür"].unique())
    
    temp_df = df if not filtre else df[df["Tür"].isin(filtre)]
    st.dataframe(temp_df, use_container_width=True)