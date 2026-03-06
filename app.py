import streamlit as st
import pandas as pd
import os

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Emre'nin Film Arşivi", page_icon="🎬", layout="centered")

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan ve Yazı Rengi */
    .stApp { background-color: #121212; color: #FFFFFF; }
    
    /* Yan Menü Tasarımı */
    [data-testid="stSidebar"] { background-color: #000000; border-right: 2px solid #333333; }
    
    /* Kart Yapısı */
    .film-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #FFFFFF;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Hassas İçerik Uyarısı (Kırmızı ve Parlak) */
    .warning-badge {
        background-color: #FF0000;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 10px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }

    /* Buton Tasarımı */
    .stButton>button {
        background-color: #FFFFFF;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #CCCCCC;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# Veri Fonksiyonları
def load_data():
    if os.path.exists("filmler.csv"):
        return pd.read_csv("filmler.csv")
    return pd.DataFrame(columns=["İsim", "Yıl", "Tür", "Bilgi", "İzlendi", "Hassas_Icerik"])

df = load_data()

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center; color: white;'>🏁 EMRE'NİN FİLM ARŞİVİ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Beşiktaş Ruhuyla İzlenecekler Listesi</p>", unsafe_allow_html=True)

# --- MENÜ ---
menu = st.sidebar.radio("İŞLEM SEÇ", ["➕ Yeni Film Ekle", "🔍 Film Sorgula", "📋 Tüm Liste"])

if menu == "➕ Yeni Film Ekle":
    st.subheader("🎬 Listeye Yeni Bir Heyecan Ekle")
    with st.form("film_form"):
        isim = st.text_input("Film Adı").strip().title()
        col1, col2 = st.columns(2)
        yil = col1.number_input("Yıl", 1950, 2026, 2024)
        tur = col2.selectbox("Tür", ["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Suç", "Belgesel"])
        bilgi = st.text_area("Film Hakkında Kısa Notun")
        hassas = st.toggle("Hassas/Cinsel İçerik Var") # Daha modern bir buton
        
        if st.form_submit_button("🦅 KARTAL GİBİ EKLE"):
            if isim:
                yeni = pd.DataFrame([[isim, yil, tur, bilgi, "Hayır", "Evet" if hassas else "Hayır"]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv("filmler.csv", index=False)
                st.success(f"'{isim}' arşive eklendi!")
            else:
                st.error("Lütfen bir film adı gir!")

elif menu == "🔍 Film Sorgula":
    st.subheader("🕵️ Arşivde Ne Vardı?")
    arama = st.text_input("Film ismini buraya yaz...").strip().title()
    
    if arama:
        sonuclar = df[df['İsim'].str.contains(arama, na=False, case=False)]
        if not sonuclar.empty:
            for i, row in sonuclar.iterrows():
                # Kart Tasarımı Başlıyor
                st.markdown(f"""
                <div class="film-card">
                    <h3>🎬 {row['İsim']} ({row['Yıl']})</h3>
                    <p><b>Tür:</b> {row['Tür']} | <b>Durum:</b> {row['İzlendi']}</p>
                    <p>📝 {row['Bilgi']}</p>
                    {f'<div class="warning-badge">⚠️ HASSAS İÇERİK</div>' if row['Hassas_Icerik'] == "Evet" else ""}
                </div>
                """, unsafe_allow_html=True)
                
                if row['İzlendi'] == "Hayır":
                    if st.button(f"'{row['İsim']}' İzledim", key=f"btn_{i}"):
                        df.at[i, "İzlendi"] = "Evet"
                        df.to_csv("filmler.csv", index=False)
                        st.rerun()
        else:
            st.warning("Bu isimle bir kayıt bulamadım Emre.")

elif menu == "📋 Tüm Liste":
    st.subheader("📚 Tüm Koleksiyon")
    st.dataframe(df.style.set_properties(**{'background-color': '#1E1E1E', 'color': 'white'}), use_container_width=True)
