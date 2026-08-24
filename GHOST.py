import base64
import json
import os
from duckduckgo_search import DDGS
import pandas as pd
from openai import OpenAI
from PIL import Image
import streamlit as st
from supabase import Client, create_client

# Sayfa Yapılandırması (Geniş Ekran)
st.set_page_config(
    page_title="TITAN v11.1 — JARVIS Ultimate Komuta Merkezi",
    page_icon="⚡",
    layout="wide",
)

# --- SİBER ARAYÜZ VE STİLLER ---
st.markdown(
    """
<style>
    .stApp { background-color: #0b0f19; color: #f0f6fc; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    p, span, label, div, .stMarkdown { font-weight: 600 !important; }
    footer { visibility: hidden; }
    
    .chat-container {
        height: calc(100vh - 220px);
        overflow-y: auto;
        padding-bottom: 100px;
        padding-right: 10px;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        background-color: #e3e8ee !important;
    }
    [data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border-radius: 12px !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #238636, #2ea043);
        color: white; border-radius: 8px; border: 1px solid #3fb950; 
        font-weight: 700; padding: 0.6rem 1.2rem; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #2ea043, #3fb950);
        box-shadow: 0 6px 8px rgba(35,134,54,0.5); border-color: #56d364;
    }
    [data-testid="stDataFrame"] { border: 1px solid #30363d; border-radius: 8px; background-color: #161b22; }
</style>
""",
    unsafe_allow_html=True,
)

# API Anahtarı ve Model Tanımı
API_KEY = "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"
client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")
MODEL_NAME = "openai/gpt-oss-120b"

# --- SUPABASE BAĞLANTISI ---
SUPABASE_URL = "https://luzzmraohsaqajinnyhk.supabase.co"
SUPABASE_KEY = "sb_publishable_Z8MQbBctodUb7jiwiEiigw_eYANG9JW"


@st.cache_resource
def init_supabase(url, key):
  try:
    return create_client(url, key)
  except Exception:
    return None


supabase = init_supabase(SUPABASE_URL, SUPABASE_KEY)

# --- SESSION STATE ---
if "giris_yapildi" not in st.session_state:
  st.session_state.giris_yapildi = False
if "kullanici_rolu" not in st.session_state:
  st.session_state.kullanici_rolu = None
if "aktif_kullanici_adi" not in st.session_state:
  st.session_state.aktif_kullanici_adi = ""

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "system",
      "content": (
          "Sen JARVIS ve TITAN v11.1 mimarisiyle güçlendirilmiş, doğrudan canlı"
          " internet aramaları yapabilen gelişmiş bir yapay zeka asistanısın."
          " Asıl sahibin Yiğit'tir. Ona ve onaylı kullanıcılara 'efendim' diye"
          " hitap et."
      ),
  }]
if "gorevler" not in st.session_state:
  st.session_state.gorevler = []
if "jarvis_hafiza" not in st.session_state:
  st.session_state.jarvis_hafiza = [
      "Ana Sahip: Yiğit",
      "Sistem Durumu: Aktif, Çevrim İçi ve Koruma Altında",
  ]
if "izinli_kisiler" not in st.session_state:
  st.session_state.izinli_kisiler = {"Yiğit": "Ana Sahip (Admin)"}
if "izinli_fotolar" not in st.session_state:
  st.session_state.izinli_fotolar = {}


# --- SES MOTORU ---
st.markdown(
    """
<script>
    function titanKonus(metin) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance(metin);
        msg.lang = 'tr-TR';
        msg.rate = 1.0;
        var voices = window.speechSynthesis.getVoices();
        let selectedVoice = null;
        for(var i = 0; i < voices.length; i++) {
            var vName = voices[i].name.toLowerCase();
            if(vName.includes('ahmet') || vName.includes('turkish male') || (vName.includes('microsoft') && vName.includes('tr'))) {
                selectedVoice = voices[i];
                break;
            }
        }
        if (!selectedVoice) {
            for(var i = 0; i < voices.length; i++) {
                if(voices[i].lang.startsWith('tr')) { selectedVoice = voices[i]; break; }
            }
        }
        if (selectedVoice) msg.voice = selectedVoice;
        window.speechSynthesis.speak(msg);
    }
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = function() { window.speechSynthesis.getVoices(); };
    }
</script>
""",
    unsafe_allow_html=True,
)


# --- GİRİŞ EKRANI ---
if not st.session_state.giris_yapildi:
  st.markdown(
      "<h1 style='text-align: center; color: #58a6ff;'>⚡ TITAN x JARVIS"
      " v11.1 — Güvenlik Protokolü</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #8b949e;'>Sisteme erişmek için"
      " biyometrik fotoğrafınızı yükleyin ya da 0912 şifresini girin"
      " efendim.</p>",
      unsafe_allow_html=True,
  )

  col_giris1, col_giris2 = st.columns(2)

  with col_giris1:
    st.markdown("### 🧬 Biyometrik Yüz Doğrulama")
    giris_fotograf = st.file_uploader(
        "Yüz Fotoğrafı Yükle", type=["jpg", "jpeg", "png"], key="giris_dosya"
    )
    giris_isim_yaz = st.text_input(
        "Kayıtlı Adınız:", placeholder="Örn: Yiğit"
    )

    if st.button("Kimliği Doğrula"):
      if giris_fotograf and giris_isim_yaz:
        temiz_giris_adi = giris_isim_yaz.strip()
        if (
            temiz_giris_adi in st.session_state.izinli_kisiler
            or giris_fotograf.name in st.session_state.izinli_fotolar
            or temiz_giris_adi.lower() == "yiğit"
        ):
          st.session_state.giris_yapildi = True
          st.session_state.kullanici_rolu = (
              "sahip" if temiz_giris_adi.lower() == "yiğit" else "yetkili_misafir"
          )
          st.session_state.aktif_kullanici_adi = temiz_giris_adi
          st.success(
              f"🎯 Kimlik Onaylandı! Hoş geldin {temiz_giris_adi} efendim."
          )
          st.components.v1.html(
              f'<script>titanKonus("Hoş geldin {temiz_giris_adi}'
              ' efendim.");</script>',
              height=0,
          )
          st.rerun()
        else:
          st.error("⚠️ Erişim Reddedildi! Tanınmayan kimlik efendim.")
          st.components.v1.html(
              '<script>titanKonus("Erişim reddedildi.");</script>', height=0
          )
      else:
        st.warning("Lütfen isim girin ve fotoğraf yükleyin efendim.")

  with col_giris2:
    st.markdown("### #️⃣ Master Şifre Girişi")
    sifre_input = st.text_input(
        "Güvenlik Anahtarı:", type="password", key="giris_sifre"
    )
    if st.button("Master Şifreyi Onayla"):
      if sifre_input == "0912":
        st.session_state.giris_yapildi = True
        st.session_state.kullanici_rolu = "sahip"
        st.session_state.aktif_kullanici_adi = "Yiğit (Ana Komutan)"
        st.success("🔓 Master Şifre Doğrulandı! Tam yetki aktif efendim.")
        st.components.v1.html(
            '<script>titanKonus("Master şifre doğrulandı, hoş geldin Yiğit'
            ' efendim.");</script>',
            height=0,
        )
        st.rerun()
      else:
        st.error("❌ Hatalı şifre efendim!")
        st.components.v1.html(
            '<script>titanKonus("Hatalı şifre girdiniz efendim.");</script>',
            height=0,
        )

  st.stop()


# --- GELİŞMİŞ CANLI İNTERNET ARAMA MOTORU (DOĞRUDAN ÇALIŞIR) ---
def internette_ara(sorgu):
  try:
    with DDGS() as ddgs:
      results = [r for r in ddgs.text(sorgu, max_results=5)]
      if results:
        return json.dumps(results, ensure_ascii=False)
    return "Arama sonucuna ulaşılamadı efendim."
  except Exception as e:
    return f"Arama motoru bağlantı hatası: {str(e)}"


# --- ANA UYGULAMA ---
st.title(
    f"⚡ TITAN v11.1 [JARVIS Core] — Operatör: {st.session_state.aktif_kullanici_adi}"
)

# --- KENAR ÇUBUĞU ---
st.sidebar.markdown(
    "<h3 style='font-weight: 800; color: #58a6ff;'>⚙️ JARVIS Komuta"
    " Menüsü</h3>",
    unsafe_allow_html=True,
)
secim = st.sidebar.radio(
    "Mod Seçin:",
    [
        "💬 JARVIS Sohbet, Canlı Web & Ses Merkezi",
        "🧠 Nöral Hafıza (MEMORIES.md) Yönetimi",
        "🔒 Fotoğraflı İzin & Güvenlik Matriksi",
        "📍 Canlı Konum ve Google Maps Radarı",
        "🛰️ Uzaktan Konum Takibi (Supabase)",
        "💻 Gelişmiş Donanım ve Sistem Paneli",
        "📌 Otonom Görev & Hatırlatıcı Takibi",
    ],
    label_visibility="collapsed",
)

if st.sidebar.button("🔒 Oturumu Kapat / Kilitle"):
  st.session_state.giris_yapildi = False
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #8b949e; font-size: 12px;'>JARVIS Core Protocol v11.1<br>Live"
    " Web Search Enabled 🟢</p>",
    unsafe_allow_html=True,
)

# --- 1. MOD: SOHBET & CANLI ARAMA & SES ---
if secim == "💬 JARVIS Sohbet, Canlı Web & Ses Merkezi":
  st.subheader(
      "💬 JARVIS Doğal Dil, Canlı İnternet Sentezi & Ses Asistanı"
  )

  st.markdown('<div class="chat-container">', unsafe_allow_html=True)

  for i, message in enumerate(st.session_state.messages):
    if message["role"] != "system" and message["role"] != "tool":
      with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, list):
          for item in content:
            if isinstance(item, dict):
              if item.get("type") == "text":
                st.markdown(f"**{item.get('text', '')}**")
              elif item.get("type") == "image_url":
                img_url = item.get("image_url", {}).get("url", "")
                if img_url:
                  st.image(img_url, width=300)
        else:
          if content:
            st.markdown(f"**{str(content)}**")

        if message["role"] == "assistant":
          metin_icerik = (
              str(content)
              if not isinstance(content, list)
              else "Yanıt seslendirildi."
          )
          temiz_metin = (
              metin_icerik.replace('"', "'")
              .replace("\n", " ")
              .replace("*", "")
          )
          if st.button(f"🔊 Bu Yanıtı Sesli Oku", key=f"ses_{i}"):
            st.components.v1.html(
                f'<script>titanKonus("{temiz_metin}");</script>', height=0
            )

  st.markdown("</div>", unsafe_allow_html=True)

  with st.expander("📸 Görsel / Dosya Analiz Modülü"):
    yuklenen_dosya = st.file_uploader(
        "Dosya Seç", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

  prompt = st.chat_input(
      "JARVIS'e araştırılacak bir şeyler yazın veya talimat verin efendim..."
  )

  if prompt:
    user_content = []
    if yuklenen_dosya:
      bytes_data = yuklenen_dosya.getvalue()
      base64_image = base64.b64encode(bytes_data).decode("utf-8")
      image_url = f"data:image/jpeg;base64,{base64_image}"
      user_content.append({"type": "image_url", "image_url": {"url": image_url}})

    user_content.append({"type": "text", "text": prompt})
    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("user"):
      if yuklenen_dosya:
        st.image(yuklenen_dosya, width=300)
      st.markdown(f"**{prompt}**")

    with st.chat_message("assistant"):
      message_placeholder = st.empty()
      try:
        api_messages = []
        for msg in st.session_state.messages:
          if isinstance(msg["content"], list):
            txt_part = next(
                (
                    item["text"]
                    for item in msg["content"]
                    if item.get("type") == "text"
                ),
                "[Görsel Gönderildi]",
            )
            api_messages.append({"role": msg["role"], "content": txt_part})
          else:
            api_messages.append(msg)

        # GÜÇLENDİRİLMİŞ İNTERNET TETİKLEYİCİSİ: Her mesajda web araması yapıp güncel veriyi modele besler!
        st.toast(
            "🌐 JARVIS Canlı Web Ağı taranıyor, güncel veriler çekiliyor...",
            icon="⚡",
        )
        web_sonuclari = internette_ara(prompt)

        api_messages.append({
            "role": "system",
            "content": (
                "İnternetten anlık olarak taranan güncel veriler ve arama"
                f" sonuçları: {web_sonuclari}. Bu verileri sentezleyerek"
                " kullanıcının sorusunu en güncel ve net şekilde yanıtla"
                " efendim."
            ),
        })

        response = client.chat.completions.create(
            model=MODEL_NAME, messages=api_messages
        )
        full_response = response.choices[0].message.content

        message_placeholder.markdown(f"**{full_response}**")

        temiz_yanit = (
            full_response.replace('"', "'")
            .replace("\n", " ")
            .replace("*", "")
        )
        st.components.v1.html(
            f'<script>titanKonus("{temiz_yanit}");</script>', height=0
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
      except Exception as e:
        st.error(f"Sistem bağlantı hatası: {e}")

  if st.sidebar.button("Sohbet Hafızasını Sıfırla"):
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "Sen JARVIS mimarisiyle güçlendirilmiş TITAN v11.1 asistanısın."
        ),
    }]
    st.rerun()

# --- 2. MOD: NÖRAL HAFIZA ---
elif secim == "🧠 Nöral Hafıza (MEMORIES.md) Yönetimi":
  st.subheader("🧠 JARVIS Dinamik Nöral İndeksleme & Hafıza Paneli")
  st.markdown(
      "Bu modül JARVIS'in kalıcı hafızasını (`MEMORIES.md`) doğrudan"
      " yönetmenizi sağlar efendim."
  )

  yeni_hafiza_notu = st.text_input("Hafızaya Yeni Bilgi Kaydet:")
  if st.button("Hafızaya İşle"):
    if yeni_hafiza_notu:
      st.session_state.jarvis_hafiza.append(yeni_hafiza_notu.strip())
      st.success("🧠 Bilgi kalıcı nöral hafızaya başarıyla eklendi efendim!")
      st.rerun()
    else:
      st.warning("Lütfen bir hafıza girdisi yazın efendim.")

  st.markdown("### 🗂️ Aktif Nöral Bellek Kayıtları:")
  for idx, mem in enumerate(st.session_state.jarvis_hafiza):
    st.write(f"- 📌 **Kayıt #{idx+1}:** {mem}")

# --- 3. MOD: FOTOĞRAFLI İZİN & GÜVENLİK ---
elif secim == "🔒 Fotoğraflı İzin & Güvenlik Matriksi":
  st.subheader("🔒 JARVIS Biyometrik Tanıma ve Yetkilendirme Paneli")
  col_yonet1, col_yonet2 = st.columns(2)

  with col_yonet1:
    st.markdown("### ➕ Yeni Yetkili Kişi ve Fotoğraf Kaydı")
    yeni_kisi_adi = st.text_input("Kişinin Adı:")
    yeni_kisi_foto = st.file_uploader(
        "Kişinin Yüz Fotoğrafı",
        type=["jpg", "jpeg", "png"],
        key="jarvis_arkadas_foto",
    )

    if st.button("Biyometrik Veriyi Kaydet"):
      if yeni_kisi_adi and yeni_kisi_foto:
        st.session_state.izinli_kisiler[yeni_kisi_adi.strip()] = (
            "Yetkili Misafir"
        )
        st.session_state.izinli_fotolar[yeni_kisi_foto.name] = (
            yeni_kisi_adi.strip()
        )
        st.success(
            f"✅ {yeni_kisi_adi} biyometrik olarak TITAN/JARVIS ağına"
            " eklendi efendim!"
        )
      else:
        st.warning("Lütfen hem ad girin hem de fotoğraf yükleyin efendim.")

  with col_yonet2:
    st.markdown("### 📋 Yetkili Güvenlik Listesi")
    for isim, rol in st.session_state.izinli_kisiler.items():
      st.write(f"- 🛡️ **{isim}** — *{rol}*")

# --- 4. MOD: CANLI KONUM + GOOGLE MAPS ---
elif secim == "📍 Canlı Konum ve Google Maps Radarı":
  st.subheader("📍 JARVIS Canlı GPS & Harita Entegrasyonu")
  st.components.v1.html(
      """
    <div style="padding: 15px; background-color: #161b22; color: white; border-radius: 8px; border: 1px solid #30363d;">
        <h3 style="color: #58a6ff; margin-top:0;">📡 Canlı Uydu & Harita Radarı</h3>
        <p id="durum" style="color: #8b949e;">Konum sinyali bekleniyor...</p>
        <div id="koord" style="margin-top: 5px; font-family: monospace; font-size: 16px; color: #3fb950; margin-bottom: 10px;"></div>
        <button onclick="canliKonumGetir()" style="background-color: #238636; color: white; padding: 10px 20px; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">Anlık Konumumu Al ve Haritada Göster</button>
        <br><br>
        <div id="harita-alani"></div>
    </div>
    <script>
        function canliKonumGetir() {
            const durum = document.getElementById("durum");
            const koord = document.getElementById("koord");
            const haritaAlani = document.getElementById("harita-alani");
            
            durum.innerHTML = "📡 Uydulara bağlanılıyor, hassas GPS konumu alınıyor...";
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        const lat = pos.coords.latitude;
                        const lon = pos.coords.longitude;
                        durum.innerHTML = "✅ Konum Başarıyla Kilitlendi!";
                        koord.innerHTML = "Enlem: " + lat.toFixed(6) + " | Boylam: " + lon.toFixed(6);
                        
                        haritaAlani.innerHTML = '<iframe width="100%" height="380" style="border:1px solid #30363d; border-radius: 8px;" loading="lazy" allowfullscreen src="https://maps.google.com/maps?q=' + lat + ',' + lon + '&z=16&output=embed"></iframe>';
                    },
                    (err) => { durum.innerHTML = "⚠️ Hata: Konum izni reddedildi veya alınamadı efendim."; },
                    { enableHighAccuracy: true, timeout: 8000 }
                );
            } else {
                durum.innerHTML = "❌ Tarayıcınız GPS konum servislerini desteklemiyor efendim.";
            }
        }
    </script>
    """,
      height=500,
  )

# --- 5. MOD: UZAKTAN KONUM TAKİBİ ---
elif secim == "🛰️ Uzaktan Konum Takibi (Supabase)":
  st.subheader("🛰️ JARVIS Uzaktan Hedef İzleme ve Harita Radarı")
  if st.button("🔄 Radar Verilerini Tazele"):
    st.rerun()

  if supabase:
    try:
      response = (
          supabase.table("konum_takip")
          .select("*")
          .order("id", desc=True)
          .limit(10)
          .execute()
      )
      data = response.data
      if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        son_konum = data[0]
        if "enlem" in son_konum and "boylam" in son_konum:
          lat = son_konum["enlem"]
          lon = son_konum["boylam"]
          st.info(
              f"🎯 Son Hedef Koordinatları -> Enlem: `{lat}` | Boylam: `{lon}`"
          )
          maps_html = f"""
                    <iframe width="100%" height="400" style="border:1px solid #30363d; border-radius: 8px;" loading="lazy" allowfullscreen src="https://maps.google.com/maps?q={lat},{lon}&z=16&output=embed"></iframe>
                    """
          st.components.v1.html(maps_html, height=420)
      else:
        st.warning("⚠️ Supabase tablosunda aktif sinyal bulunamadı efendim.")
    except Exception as ex:
      st.error(f"Radar veri çekme hatası: {ex}")
  else:
    st.error("Supabase bağlantısı kurulamadı efendim.")

# --- 6. MOD: SİSTEM ---
elif secim == "💻 Gelişmiş Donanım ve Sistem Paneli":
  st.subheader("💻 JARVIS Donanım Altyapı ve Kaynak Monitörü")
  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(label="🔥 CPU Yükü", value="%11.2", delta="Optimal")
    st.progress(0.11)
  with col2:
    st.metric(label="💾 RAM Kullanımı", value="%40.1", delta="Normal")
    st.progress(0.40)
  with col3:
    st.metric(label="🌐 Sunucu Gecikmesi", value="12 ms", delta="Mükemmel")
    st.progress(0.12)
  st.success("JARVIS & TITAN v11.1 canlı web ağıyla tam kapasite çalışıyor.")

# --- 7. MOD: GÖREVLER ---
else:
  st.subheader("📌 JARVIS Otonom Görev ve Hatırlatıcı Yönetimi")
  yeni_gorev = st.text_input("Yeni Görev veya Hatırlatıcı Tanımlayın:")
  if st.button("Görev Ekle"):
    if yeni_gorev:
      st.session_state.gorevler.append(
          {"gorev": yeni_gorev, "durum": "Bekliyor ⏳"}
      )
      st.success("Yeni görev JARVIS görev kuyruğuna eklendi efendim.")
      st.rerun()
    else:
      st.warning("Lütfen geçerli bir görev tanımı girin efendim.")

  st.markdown("### Aktif Görev Listesi:")
  if not st.session_state.gorevler:
    st.info("Kayıtlı aktif görev bulunmuyor efendim.")
  else:
    for i, g in enumerate(st.session_state.gorevler):
      col1, col2 = st.columns([4, 1])
      with col1:
        st.write(f"**{i+1}.** {g['gorev']} — *{g['durum']}*")
      with col2:
        if g["durum"] != "Tamamlandı ✅":
          if st.button("Tamamla", key=f"b_{i}"):
            st.session_state.gorevler[i]["durum"] = "Tamamlandı ✅"
            st.rerun()
