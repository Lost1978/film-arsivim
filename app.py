import streamlit as st
import pandas as pd
import os
import random

# Sayfa Ayarları
st.set_page_config(page_title="Emre'nin Film Arşivi", page_icon="🎬", layout="centered")

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .film-card {
        background: #111111;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 8px;
    }
    .puan-text { color: #ffca28; font-weight: bold; font-size: 0.9rem; margin-top: 5px; }
    .age-badge {
        background: #ff0000; color: white; padding: 2px 6px;
        border-radius: 4px; font-size: 0.7rem; float: right;
    }
    .stCheckbox { 
        background: #1a1a1a; padding: 8px 15px; border-radius: 12px; 
        border: 1px solid #333; margin-bottom: 20px;
    }
    [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #222; }
    .stButton>button { background: #ffffff; color: #000; font-weight: bold; width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ YÖNETİMİ ---
TUR_LISTESI = ["Aksiyon", "Dram", "Komedi", "Korku", "Bilim Kurgu", "Suç", "Belgesel", "Animasyon", "Gerilim", "Macera", "Fantastik", "Biyografi"]

def load_data():
    if os.path.exists("filmler.csv"):
        df = pd.read_csv("filmler.csv")
        if "Puan" not in df.columns: df["Puan"] = 0.0
        return df
    return pd.DataFrame(columns=["İsim", "Yıl", "Tür", "Bilgi", "İzlendi", "Hassas_Icerik", "Puan"])

def save_data(df):
    df.to_csv("filmler.csv", index=False)

df = load_data()

# --- ŞİFRE KONTROLÜ ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

def check_password():
    if st.session_state['auth']: return True
    st.subheader("🔒 Yetkili Erişimi")
    pin = st.text_input("Giriş Şifresi", type="password")
    if pin == "5444":
        st.session_state['auth'] = True
        st.rerun()
        return True
    return False

# --- YAN MENÜ ---
st.sidebar.title("🦅 KARTAL PANEL")
menu = st.sidebar.radio("MENÜ", ["🔍 İçerik Ara", "📋 Koleksiyon & Öneri", "🎥 Film Kaydet", "✍️ Kayıtları Düzenle"])

# --- 1. İÇERİK ARA ---
if menu == "🔍 İçerik Ara":
    st.subheader("Hızlı Arama")
    ara = st.text_input("Film adı...").strip().title()
    if ara:
        res = df[df["İsim"].str.contains(ara, na=False, case=False)]
        st.dataframe(res[["İsim", "Yıl", "Tür", "Puan", "İzlendi"]], use_container_width=True)

# --- 2. KOLEKSİYON & ÖNERİ ---
elif menu == "📋 Koleksiyon & Öneri":
    with st.expander("🔍 Filtreleme Seçenekleri"):
        f_col1, f_col2 = st.columns(2)
        # Filtreleme kısmında da çoklu tür seçimi
        secilen_tur = f_col1.multiselect("Tür Seç", options=TUR_LISTESI)
        min_puan = st.slider("Minimum Puan", 0.0, 10.0, 0.0, step=0.5)
        secilen_izlendi = st.radio("Durum", ["Hepsi", "İzlenmeyenler", "İzlenenler"], horizontal=True)

    filtered_df = df.copy()
    
    # Çoklu tür filtreleme mantığı (Seçilen türlerden biri bile varsa gösterir)
    if secilen_tur:
        filtered_df = filtered_df[filtered_df['Tür'].apply(lambda x: any(t in str(x) for t in secilen_tur))]
    
    filtered_df = filtered_df[filtered_df["Puan"] >= min_puan]
    if secilen_izlendi == "İzlenmeyenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Hayır"]
    elif secilen_izlendi == "İzlenenler": filtered_df = filtered_df[filtered_df["İzlendi"] == "Evet"]

    if st.button("🎲 RASTGELE ÖNER"):
        if not filtered_df.empty:
            f = filtered_df.sample(n=1).iloc[0]
            st.info(f"Önerim: {f['İsim']} (⭐ {f['Puan']}/10)")
        else: st.warning("Uygun film yok.")

    for i, row in filtered_df.iterrows():
        with st.container():
            badge = '<span class="age-badge">18+</span>' if row['Hassas_Icerik'] == "Evet" else ""
            st.markdown(f'''
                <div class="film-card">
                    {badge}
                    <div style="font-weight:bold;">🎬 {row["İsim"]} ({row["Yıl"]})</div>
                    <div style="color:#888; font-size:0.85rem;">{row["Tür"]} | {row["Bilgi"]}</div>
                    <div class="puan-text">⭐ {row['Puan']}/10</div>
                </div>
            ''', unsafe_allow_html=True)
            check = st.checkbox("İzlendi", value=(row["İzlendi"] == "Evet"), key=f"c_{i}")
            if check != (row["İzlendi"] == "Evet"):
                df.at[i, "İzlendi"] = "Evet" if check else "Hayır"
                save_data(df)
                st.rerun()

# --- 3. FİLM KAYDET (ÇOKLU TÜR EKLENDİ) ---
elif menu == "🎥 Film Kaydet":
    if check_password():
        st.subheader("Yeni Film Ekle")
        with st.form("kayit"):
            isim = st.text_input("Film Adı").strip().title()
            # MULTISELECT Kullanıyoruz
            turler = st.multiselect("Türler", options=TUR_LISTESI)
            c1, c2 = st.columns(2)
            yil = c1.number_input("Yıl", 1950, 2030, 2025)
            puan = st.slider("Senin Puanın", 0.0, 10.0, 5.0, step=0.5)
            bilgi = st.text_area("Not")
            hassas = st.checkbox("18+ İçerik")
            
            if st.form_submit_button("Arşive Ekle"):
                if isim and turler:
                    # Türleri virgülle birleştirip tek bir string olarak kaydediyoruz
                    tur_str = ", ".join(turler)
                    yeni = pd.DataFrame([[isim, yil, tur_str, bilgi, "Hayır", "Evet" if hassas else "Hayır", puan]], columns=df.columns)
                    df = pd.concat([df, yeni], ignore_index=True)
                    save_data(df)
                    st.success("Başarıyla eklendi!")
                    st.rerun()
                elif not turler:
                    st.error("Lütfen en az bir tür seçin!")

# --- 4. KAYITLARI DÜZENLE ---
elif menu == "✍️ Kayıtları Düzenle":
    if check_password():
        st.subheader("Güncelle")
        if not df.empty:
            secilen_film = st.selectbox("Film Seç", options=df["İsim"].tolist())
            idx = df[df["İsim"] == secilen_film].index[0]
            f_v = df.iloc[idx]
            
            # Mevcut türleri listeye geri çeviriyoruz
            mevcut_turler = str(f_v["Tür"]).split(", ")
            
            with st.form("duzenle"):
                n_isim = st.text_input("Film Adı", value=f_v["İsim"])
                n_turler = st.multiselect("Türleri Güncelle", options=TUR_LISTESI, default=[t for t in mevcut_turler if t in TUR_LISTESI])
                n_puan = st.slider("Puan", 0.0, 10.0, float(f_v["Puan"]), step=0.5)
                n_bilgi = st.text_area("Notlar", value=f_v["Bilgi"])
                sil = st.checkbox("⚠️ SİL")
                
                if st.form_submit_button("Değişiklikleri Kaydet"):
                    if sil: df = df.drop(idx)
                    else:
                        df.at[idx, "İsim"] = n_isim
                        df.at[idx, "Tür"] = ", ".join(n_turler)
                        df.at[idx, "Puan"] = n_puan
                        df.at[idx, "Bilgi"] = n_bilgi
                    save_data(df)
                    st.success("Güncellendi!")
                    st.rerun()
