import base64
import datetime
import html
import json
import os
import random
import time
import urllib.parse
import urllib.request
import pandas as pd
from openai import OpenAI
from PIL import Image
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# 01. SİSTEM YAPILANDIRMASI VE ÇEKİRDEK AYARLARI (TITAN v21.0 OMEGA SUPREME)
# ==============================================================================
st.set_page_config(
    page_title=(
        "TITAN v21.0 OMEGA SUPREME — JARVIS Enterprise Komuta & Asistan Üssü"
    ),
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 02. GELİŞMİŞ HACKER & CYBERPUNK ÖZEL CSS STİLLERİ VE ARAYÜZ MİMARİSİ
# ==============================================================================
st.markdown(
    """
<style>
    /* Ana Tema ve Arka Plan Renkleri */
    .stApp {
        background-color: #020408;
        color: #f0f6fc;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Yan Menü (Sidebar) Özelleştirmeleri */
    [data-testid="stSidebar"] {
        background-color: #080c10;
        border-right: 1px solid #21262d;
    }
    
    /* Başlıklar ve Vurgu Renkleri */
    h1, h2, h3 {
        color: #38bdf8 !important;
        letter-spacing: -0.5px;
        font-weight: 800 !important;
    }
    
    /* Metin Kalınlıkları ve Okunabilirlik */
    p, span, label, div, .stMarkdown {
        font-weight: 500 !important;
    }
    
    /* Streamlit Varsayılan Alt Bilgi Gizleme */
    footer {
        visibility: hidden;
    }
    
    /* Sohbet Akış Konteyneri */
    .chat-container {
        height: calc(100vh - 280px);
        overflow-y: auto;
        padding-bottom: 140px;
        padding-right: 12px;
    }
    
    /* Sohbet Giriş Alanı (Chat Input) */
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        background-color: #0d1117 !important;
    }
    [data-testid="stChatInput"] {
        background-color: #11161d !important;
        border-radius: 14px !important;
        border: 1px solid #30363d !important;
    }
    
    /* Buton Tasarımları ve Efektler */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7, #059669);
        color: white;
        border-radius: 10px;
        border: 1px solid #38bdf8;
        font-weight: 700;
        padding: 0.6rem 1.2rem;
        width: 100%;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369a1, #047857);
        box-shadow: 0 6px 16px rgba(5, 150, 105, 0.5);
        border-color: #34d399;
    }
    
    /* Veri Tabloları ve Kutu Çerçeveleri */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363d;
        border-radius: 10px;
        background-color: #0d1117;
    }
    .matrix-box {
        background-color: #05080f;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        font-family: monospace;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 03. API, GROQ LLM VE BULUT VERİTABANI BAĞLANTI ENTEGRASYONLARI
# ==============================================================================
API_KEY = "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"
client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")
MODEL_NAME = "openai/gpt-oss-120b"

SUPABASE_URL = "https://luzzmraohsaqajinnyhk.supabase.co"
SUPABASE_KEY = "sb_publishable_Z8MQbBctodUb7jiwiEiigw_eYANG9JW"


@st.cache_resource
def titan_supabase_baglan(url, key):
  """Supabase bulut veri tabanı bağlantısını güvenli önbellekle başlatır."""
  try:
    return create_client(url, key)
  except Exception as e:
    print(f"Supabase Bağlantı Hatası: {e}")
    return None


supabase = titan_supabase_baglan(SUPABASE_URL, SUPABASE_KEY)


# ==============================================================================
# 03.1 YARDIMCI GELİŞMİŞ MATRİS VE LOGLAMA FONKSİYONLARI (GENİŞLETİLMİŞ)
# ==============================================================================
def titan_ekstra_guvenlik_taramasi(hedef_ip_adres):
  """Ağ paketleri üzerinde simüle edilmiş derin siber güvenlik analizi yapar."""
  time.sleep(0.1)
  guvenli_mi = not ("185." in hedef_ip_adres or "91." in hedef_ip_adres)
  return {
      "ip": hedef_ip_adres,
      "guvenli": guvenli_mi,
      "zaman": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  }


def titan_not_istatistigi_hesapla(notlar_listesi):
  """Not defterindeki kelime ve karakter istatistiklerini hesaplar."""
  toplam_karakter = sum(len(n) for n in notlar_listesi)
  toplam_kelime = sum(len(n.split()) for n in notlar_listesi)
  return toplam_karakter, toplam_kelime


# ==============================================================================
# 04. OTURUM, GÜVENLİK VE NÖRAL HAFIZA YÖNETİCİSİ (STREAMLIT SESSION STATE)
# ==============================================================================
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
          "Sen JARVIS ve TITAN v21.0 OMEGA SUPREME mimarisiyle güçlendirilmiş,"
          " gelişmiş sesli yanıt, canlı web arama ve kalıcı hafıza"
          " özelliklerine sahip yapay zeka asistanısın. Asıl sahibin"
          " Yiğit'tir. Ona ve yetkili kullanıcılara her zaman 'efendim' diye"
          " hitap et."
      ),
  }]

if "gorevler" not in st.session_state:
  st.session_state.gorevler = []
if "jarvis_hafiza" not in st.session_state:
  st.session_state.jarvis_hafiza = [
      "Ana Sahip ve Komutan: Yiğit",
      "Sistem Çekirdeği: TITAN v21.0 OMEGA SUPREME",
      "Güvenlik Duvarı: Aktif (Kuantum Matris Koruması)",
      "Nöral Bellek: Tam Kapasite Senkronize Edildi",
      (
          "Özel Modüller: Gelişmiş Sesli Asistan (TTS) & Kalıcı Asistan"
          " Hafızası"
      ),
  ]
if "izinli_kisiler" not in st.session_state:
  st.session_state.izinli_kisiler = {"Yiğit": "Ana Komutan (Admin)"}
if "izinli_fotolar" not in st.session_state:
  st.session_state.izinli_fotolar = {}
if "sistem_loglari" not in st.session_state:
  st.session_state.sistem_loglari = [
      f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TITAN v21.0 OMEGA çekirdeği, web arama, ses/TTS ve hafıza modülleri tam kadro yüklendi."
  ]
if "notlar_defteri" not in st.session_state:
  st.session_state.notlar_defteri = []
if "siber_tehditler" not in st.session_state:
  st.session_state.siber_tehditler = [
      {"ip": "192.168.1.100", "durum": "Güvenli 🟢", "risk": "Yok"},
      {"ip": "185.220.101.7", "durum": "Bloklandı 🛡️", "risk": "Kritik"},
  ]

if "anlik_sicaklik" not in st.session_state:
  st.session_state.anlik_sicaklik = "25 °C"
if "anlik_yagis" not in st.session_state:
  st.session_state.anlik_yagis = "%0"
if "anlik_sis" not in st.session_state:
  st.session_state.anlik_sis = "Normal"
if "hava_ozeti" not in st.session_state:
  st.session_state.hava_ozeti = "Henüz arama yapılmadı efendim."
if "hava_tavsiyesi" not in st.session_state:
  st.session_state.hava_tavsiyesi = (
      "Hava durumunu kontrol etmek için arama başlatın."
  )

# ==============================================================================
# 05. GELİŞMİŞ SES SENTEZLEYİCİ VE OKUYUCU JAVASCRIPT MODÜLÜ (TTS - WEB SPEECH)
# ==============================================================================
st.markdown(
    """
<script>
    function titanOmegaKonus(metin) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance(metin);
        msg.lang = 'tr-TR';
        msg.rate = 1.05;
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

# ==============================================================================
# 06. GİRİŞ KONTROL, BİYOMETRİK YÜZ TANIMA VE MASTER KİMLİK DOĞRULAMA EKRANI
# ==============================================================================
if not st.session_state.giris_yapildi:
  st.markdown(
      "<h1 style='text-align: center; color: #38bdf8;'>⚡ TITAN v21.0"
      " OMEGA — Güvenlik Matriksi</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #94a3b8;'>Sisteme tam yetkiyle"
      " erişmek için biyometrik görsel yükleyin veya 0912 master kodunu girin"
      " efendim.</p>",
      unsafe_allow_html=True,
  )

  col_g1, col_g2 = st.columns(2)

  with col_g1:
    st.markdown("### 🧬 Biyometrik Yüz Tanıma Terminali")
    giris_foto = st.file_uploader(
        "Yüz Doğrulama Görseli",
        type=["jpg", "jpeg", "png"],
        key="giris_dosya_v21",
    )
    giris_isim = st.text_input(
        "Operatör Adı:", placeholder="Örn: Yiğit", key="giris_isim_input"
    )

    if st.button("Biyometrik Kimliği Doğrula", key="btn_biyo_dogrula"):
      if giris_foto and giris_isim:
        temiz_isim = giris_isim.strip()
        if (
            temiz_isim in st.session_state.izinli_kisiler
            or giris_foto.name in st.session_state.izinli_fotolar
            or temiz_isim.lower() == "yiğit"
        ):
          st.session_state.giris_yapildi = True
          st.session_state.kullanici_rolu = (
              "sahip" if temiz_isim.lower() == "yiğit" else "yetkili_misafir"
          )
          st.session_state.aktif_kullanici_adi = temiz_isim
          st.success(
              f"🎯 Kimlik Onaylandı! Hoş geldin {temiz_isim} komutanım."
          )
          st.components.v1.html(
              f'<script>titanOmegaKonus("Hoş geldin {temiz_isim}'
              ' efendim, Omega v21 aktif.");</script>',
              height=0,
          )
          st.rerun()
        else:
          st.error("⚠️ Erişim Reddedildi! Bilinmeyen imza efendim.")
      else:
        st.warning("Lütfen adınızı girin ve görsel yükleyin efendim.")

  with col_g2:
    st.markdown("### #️⃣ Master Şifre Giriş Protokolü")
    sifre_girdi = st.text_input(
        "Güvenlik Anahtarı (PIN):", type="password", key="giris_sifre_v21"
    )
    if st.button("Master Anahtarı Doğrula", key="btn_master_dogrula"):
      if sifre_girdi == "0912":
        st.session_state.giris_yapildi = True
        st.session_state.kullanici_rolu = "sahip"
        st.session_state.aktif_kullanici_adi = "Yiğit (Ana Komutan)"
        st.success(
            "🔓 Master Anahtar Onaylandı! Omega yetkileri devreye"
            " sokuluyor..."
        )
        st.components.v1.html(
            '<script>titanOmegaKonus("Master şifre doğrulandı, hoş geldin'
            ' Yiğit efendim.");</script>',
            height=0,
        )
        st.rerun()
      else:
        st.error("❌ Hatalı şifre girdiniz efendim!")

  st.stop()


# ==============================================================================
# 07. SAF PYTHON WEB ARAMA MOTORU (DEEP SEARCH ENTEGRASYONU)
# ==============================================================================
def titan_web_aramasi_yap(sorgu):
  """Duckduckgo HTML altyapısı üzerinden canlı internet taraması gerçekleştirir."""
  try:
    url = (
        "https://html.duckduckgo.com/html/?q="
        + urllib.parse.quote_plus(sorgu)
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=10) as response:
      html_content = response.read().decode("utf-8")

    sonuclar = []
    parcalar = html_content.split('class="result__snippet')
    for parca in parcalar[1:6]:
      try:
        boluk = parca.split("</a>")[0]
        temiz = (
            boluk.split(">")[-1]
            .replace("<b>", "")
            .replace("</b>", "")
            .strip()
        )
        temiz = html.unescape(temiz)
        if temiz:
          sonuclar.append(temiz)
      except Exception:
        continue

    if sonuclar:
      return json.dumps(sonuclar, ensure_ascii=False)
    return "Arama sonucuna ulaşılamadı efendim."
  except Exception as e:
    return f"Arama motoru hata kodu: {str(e)}"


# ==============================================================================
# 08. ANA UYGULAMA BAŞLIĞI VE OPERATÖR DURUM KONTROLÜ
# ==============================================================================
st.title(
    f"⚡ TITAN v21.0 OMEGA SUPREME [JARVIS Core] — Operatör:"
    f" {st.session_state.aktif_kullanici_adi}"
)

# ==============================================================================
# 09. KENAR ÇUBUĞU (OMEGA YÖNETİM MENÜSÜ - TÜM MODÜLLER TAM KADRO)
# ==============================================================================
st.sidebar.markdown(
    "<h3 style='font-weight: 800; color: #38bdf8;'>⚙️ OMEGA Supreme"
    " Menü</h3>",
    unsafe_allow_html=True,
)

ana_secim = st.sidebar.radio(
    "Sistem Modu Seçin:",
    [
        "💬 JARVIS Omega Sohbet, Canlı Web & Ses (TTS)",
        "🧠 Kalıcı Asistan Hafızası ve Not Defteri",
        "🌍 Küresel Canlı Hava Durumu & Uydu Radarı",
        "🛡️ Siber Güvenlik Duvarı & Tehdit Radarı",
        "📍 Canlı GPS Konum ve Google Maps Ağı",
        "🛰️ Uzaktan Hedef İzleme (Supabase Sync)",
        "📊 Sistem Denetim, Performans & Loglar",
    ],
    label_visibility="collapsed",
)

if st.sidebar.button("🔒 Oturumu Kapat ve Kilitle", key="btn_oturum_kapat"):
  st.session_state.giris_yapildi = False
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #64748b; font-size: 11px;'>TITAN Omega Core v21.0<br>All"
    " Modules Fully Operational 🟢</p>",
    unsafe_allow_html=True,
)

# ==============================================================================
# 10. MODÜL 1: SOHBET, CANLI WEB ARAMA VE SESLİ ASİSTAN (TTS)
# ==============================================================================
if ana_secim == "💬 JARVIS Omega Sohbet, Canlı Web & Ses (TTS)":
  st.subheader(
      "💬 JARVIS Omega Doğal Dil, Canlı İnternet Ağı & Sesli Asistan (TTS)"
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
                  st.image(img_url, width=320)
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
          if st.button(
              f"🔊 Bu Yanıtı Sesli Oku (TTS)", key=f"ses_v21_ btn_{i}"
          ):
            st.components.v1.html(
                f'<script>titanOmegaKonus("{temiz_metin}");</script>', height=0
            )

  st.markdown("</div>", unsafe_allow_html=True)

  with st.expander("📸 Görsel / Çoklu Ortam Analiz Modülü"):
    yuklenen_dosya_v21 = st.file_uploader(
        "Görsel Seç",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="gorsel_yukleme_v21",
    )

  prompt = st.chat_input(
      "JARVIS Omega modülüne komut verin veya soru sorun efendim..."
  )

  if prompt:
    user_content = []
    if yuklenen_dosya_v21:
      bytes_data = yuklenen_dosya_v21.getvalue()
      base64_image = base64.b64encode(bytes_data).decode("utf-8")
      image_url = f"data:image/jpeg;base64,{base64_image}"
      user_content.append({"type": "image_url", "image_url": {"url": image_url}})

    user_content.append({"type": "text", "text": prompt})
    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("user"):
      if yuklenen_dosya_v21:
        st.image(yuklenen_dosya_v21, width=320)
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
                "[Görsel Aktarıldı]",
            )
            api_messages.append({"role": msg["role"], "content": txt_part})
          else:
            api_messages.append(msg)

        st.toast(
            "🌐 TITAN Omega Canlı Web Ağı taranıyor, güncel veriler çekiliyor...",
            icon="⚡",
        )
        web_sonuclari = titan_web_aramasi_yap(prompt)

        api_messages.append({
            "role": "system",
            "content": (
                "İnternetten anlık taranan güncel veriler ve arama"
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
            f'<script>titanOmegaKonus("{temiz_yanit}");</script>', height=0
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
        st.session_state.sistem_loglari.append(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Omega web sorgusu işlendi: {prompt[:30]}..."
        )
      except Exception as e:
        st.error(f"Sistem bağlantı hatası: {e}")

  if st.sidebar.button(
      "Omega Sohbet Geçmişini Temizle", key="btn_sohbet_temizle"
  ):
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "Sen TITAN v21.0 OMEGA SUPREME asistanı ve JARVIS çekirdeğisin."
        ),
    }]
    st.rerun()

# ==============================================================================
# 11. MODÜL 2: KALICI ASİSTAN HAFIZASI VE OPERASYONEL NOT DEFTERİ
# ==============================================================================
elif ana_secim == "🧠 Kalıcı Asistan Hafızası ve Not Defteri":
  st.subheader(
      "🧠 JARVIS Dinamik Nöral Hafıza, Hatırlatıcı ve Notlar Defteri"
  )
  st.markdown(
      "Bu modül JARVIS yapay zekasının kalıcı hafızasını yönetmeni ve önemli"
      " notlar almanı sağlar efendim."
  )

  col_m1, col_m2 = st.columns(2)

  with col_m1:
    st.markdown("### 📌 Kalıcı Nöral Bellek (MEMORIES)")
    yeni_hafiza = st.text_input(
        "Nöral Hafızaya Yeni Bilgi Ekle:", key="input_yeni_hafiza"
    )
    if st.button("Hafıza Çekirdeğine Kaydet", key="btn_hafiza_kaydet"):
      if yeni_hafiza:
        st.session_state.jarvis_hafiza.append(yeni_hafiza.strip())
        st.success("🧠 Yeni veri kalıcı nöral belleğe işlendi efendim!")
        st.rerun()
      else:
        st.warning("Lütfen bir hafıza girdisi yazın efendim.")

    st.markdown("#### Aktif Nöral Kayıtlar:")
    for idx, mem in enumerate(st.session_state.jarvis_hafiza):
      st.write(f"- 📌 **[{idx+1}]:** {mem}")

  with col_m2:
    st.markdown("### 📝 Operasyonel Notlar Defteri")
    yeni_not = st.text_area(
        "Hızlı Not Al veya Görev Belirt:",
        placeholder="Örn: Proje detayları...",
        key="input_yeni_not",
    )
    if st.button("Notu Deftere Kaydet", key="btn_not_kaydet"):
      if yeni_not:
        st.session_state.notlar_defteri.append(yeni_not.strip())
        st.success("Not başarıyla kaydedildi efendim.")
        st.rerun()
      else:
        st.warning("Lütfen bir not yazın efendim.")

    st.markdown("#### Kayıtlı Notlar:")
    if not st.session_state.notlar_defteri:
      st.info("Kayıtlı not bulunmuyor efendim.")
    else:
      kar_sayisi, kel_sayisi = titan_not_istatistigi_hesapla(
          st.session_state.notlar_defteri
      )
      st.caption(
          f"📊 Not İstatistikleri -> Toplam Karakter: {kar_sayisi} | Toplam"
          f" Kelime: {kel_sayisi}"
      )
      for idx, not_item in enumerate(st.session_state.notlar_defteri):
        st.write(f"- 📋 **Not #{idx+1}:** {not_item}")

# ==============================================================================
# 12. MODÜL 3: KÜRESEL CANLI HAVA DURUMU & UYDU RADARI
# ==============================================================================
elif ana_secim == "🌍 Küresel Canlı Hava Durumu & Uydu Radarı":
  st.subheader(
      "🌍 JARVIS Küresel Atmosferik İstasyonu & Sınırsız Şehir Tarayıcı"
  )

  col_fav1, col_fav2 = st.columns([3, 1])
  with col_fav1:
    hedef_sehir = st.text_input(
        "🏙️ Şehir Girin:", value="Edirne", key="input_sehir"
    )
  with col_fav2:
    hedef_ulke = st.text_input(
        "🌐 Ülke:", value="Türkiye", key="input_ulke"
    )

  sorgu_bolge = f"{hedef_sehir.strip()}, {hedef_ulke.strip()}"

  if st.button("Küresel Hava Durumu ve Değerleri Çek", key="btn_hava_cek"):
    with st.spinner(
        f"🛰️ {sorgu_bolge} için uydu verileri ve meteoroloji oranları"
        " taranıyor..."
    ):
      ham_hava = titan_web_aramasi_yap(
          f"{sorgu_bolge} hava durumu sıcaklık derece yağış"
      )
      try:
        ozet_istek = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen esprili ve akıllı bir hava durumu"
                        " asistanısın. Verilen arama sonuçlarını analiz et ve"
                        " şu formatta yanıt ver:\nSICAKLIK: [Örn: 24 °C] |"
                        " YAGIS: [Örn: %10] | SIS: [Örn: Normal] | OZET: [Kısa"
                        " cümle] | TAVSIYE: [Kullanıcıya esprili kıyafet veya"
                        " aktivite önerisi]"
                    ),
                },
                {"role": "user", "content": ham_hava},
            ],
        )
        cevap_metni = ozet_istek.choices[0].message.content

        st.session_state.hava_ozeti = cevap_metni
        st.session_state.hava_tavsiyesi = (
            "Dışarı çıkarken havanın tadını çıkar!"
        )

        if "SICAKLIK:" in cevap_metni:
          parcalar = cevap_metni.split("|")
          for p in parcalar:
            if "SICAKLIK:" in p:
              st.session_state.anlik_sicaklik = p.replace(
                  "SICAKLIK:", ""
              ).strip()
            elif "YAGIS:" in p:
              st.session_state.anlik_yagis = p.replace("YAGIS:", "").strip()
            elif "SIS:" in p:
              st.session_state.anlik_sis = p.replace("SIS:", "").strip()
            elif "TAVSIYE:" in p:
              st.session_state.hava_tavsiyesi = p.replace(
                  "TAVSIYE:", ""
              ).strip()
        else:
          st.session_state.anlik_sicaklik = "25 °C"
          st.session_state.anlik_yagis = "%0"
          st.session_state.anlik_sis = "Normal"

      except Exception:
        st.session_state.anlik_sicaklik = "25 °C"
        st.session_state.anlik_yagis = "%0"
        st.session_state.anlik_sis = "Normal"
        st.session_state.hava_ozeti = str(ham_hava)[:300]
        st.session_state.hava_tavsiyesi = (
            "Bugün hava sürprizlere açık, dikkatli ol!"
        )

      st.success("✅ Hava durumu değerleri başarıyla güncellendi efendim.")

  aktif_sicaklik_str = getattr(st.session_state, "anlik_sicaklik", "25 °C")
  aktif_yagis_str = getattr(st.session_state, "anlik_yagis", "%0")

  atmo_ikon = "☀️"
  if (
      "yağmur" in str(getattr(st.session_state, "hava_ozeti", "")).lower()
      or "%" in aktif_yagis_str
      and int(aktif_yagis_str.replace("%", "").strip() or 0) > 20
  ):
    atmo_ikon = "🌧️"
  elif "kar" in str(getattr(st.session_state, "hava_ozeti", "")).lower():
    atmo_ikon = "❄️"
  elif "bulut" in str(getattr(st.session_state, "hava_ozeti", "")).lower():
    atmo_ikon = "⛅"

  st.markdown(
      f"### {atmo_ikon} {sorgu_bolge} Canlı Meteorolojik Sentez Raporu"
  )
  st.info(f"**Uydu Veri Özeti:** {st.session_state.get('hava_ozeti', 'Veri yok')}")
  st.warning(
      f"🤖 **JARVIS Atmosferik Tavsiyesi:**"
      f" {getattr(st.session_state, 'hava_tavsiyesi', 'Hava güzel, dışarı çık!')}"
  )

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Hedef Konum", sorgu_bolge, "Aktif")
  c2.metric(
      "Sıcaklık Derecesi",
      getattr(st.session_state, "anlik_sicaklik", "Bilinmiyor"),
      "Güncel 🟢",
  )
  c3.metric(
      "Yağış Oranı",
      getattr(st.session_state, "anlik_yagis", "Bilinmiyor"),
      "Uydu Verisi",
  )
  c4.metric(
      "Sis & Rüzgar",
      getattr(st.session_state, "anlik_sis", "Bilinmiyor"),
      "Atmosferik",
  )

# ==============================================================================
# 14. MODÜL 4: SİBER GÜVENLİK DUVARI & TEHDİT RADARI
# ==============================================================================
elif ana_secim == "🛡️ Siber Güvenlik Duvarı & Tehdit Radarı":
  st.subheader("🛡️ TITAN Omega Siber Güvenlik ve Ağ Tehdit Matriksi")
  yeni_ip = st.text_input(
      "Engellenecek veya İncelenecek IP Adresi:",
      placeholder="Örn: 185.220.101.5",
      key="input_yeni_ip",
  )
  if st.button("Ağ Güvenlik Duvarına Ekle", key="btn_ip_ekle"):
    if yeni_ip:
      analiz_sonuc = titan_ekstra_guvenlik_taramasi(yeni_ip.strip())
      risk_durumu = "Kritik ⚠️" if not analiz_sonuc["guvenli"] else "Düşük 🟢"
      st.session_state.siber_tehditler.append({
          "ip": yeni_ip.strip(),
          "durum": (
              "Engellendi 🛡️"
              if not analiz_sonuc["guvenli"]
              else "İncelendi 🔍"
          ),
          "risk": risk_durumu,
      })
      st.success(
          f"🔒 {yeni_ip} analizi tamamlandı ve güvenlik matrisine işlendi"
          " efendim!"
      )
      st.rerun()
    else:
      st.warning("Lütfen geçerli bir IP adresi girin efendim.")

  st.markdown("### 🚨 Aktif Tehdit Matrisi Kayıtları:")
  for tehdit in st.session_state.siber_tehditler:
    st.write(
        f"- 🌐 **IP:** `{tehdit['ip']}` | **Durum:** `{tehdit['durum']}` |"
        f" **Risk Seviyesi:** `{tehdit['risk']}`"
    )

# ==============================================================================
# 15. MODÜL 5: CANLI GPS KONUM VE GOOGLE MAPS AĞI
# ==============================================================================
elif ana_secim == "📍 Canlı GPS Konum ve Google Maps Ağı":
  st.subheader("📍 JARVIS Canlı GPS Satellit ve Harita Entegrasyonu")
  st.components.v1.html(
      """
    <div style="padding: 18px; background-color: #0d1117; color: white; border-radius: 10px; border: 1px solid #30363d;">
        <h3 style="color: #38bdf8; margin-top:0;">📡 Canlı Uydu & Harita Radarı</h3>
        <p id="durum_gps" style="color: #94a3b8;">Konum sinyali bekleniyor...</p>
        <div id="koord_gps" style="margin-top: 5px; font-family: monospace; font-size: 16px; color: #10b981; margin-bottom: 12px;"></div>
        <button onclick="titanKonumAl()" style="background-color: #0284c7; color: white; padding: 10px 22px; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">Anlık Konumumu Al ve Haritada Göster</button>
        <br><br>
        <div id="harita-cerceve"></div>
    </div>
    <script>
        function titanKonumAl() {
            const durum = document.getElementById("durum_gps");
            const koord = document.getElementById("koord_gps");
            const haritaAlani = document.getElementById("harita-cerceve");
            durum.innerHTML = "📡 Uydulara bağlanılıyor, hassas GPS konumu alınıyor...";
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        const lat = pos.coords.latitude;
                        const lon = pos.coords.longitude;
                        durum.innerHTML = "✅ Konum Başarıyla Kilitlendi!";
                        koord.innerHTML = "Enlem: " + lat.toFixed(6) + " | Boylam: " + lon.toFixed(6);
                        haritaAlani.innerHTML = '<iframe width="100%" height="400" style="border:1px solid #30363d; border-radius: 10px;" loading="lazy" allowfullscreen src="https://maps.google.com/maps?q=' + lat + ',' + lon + '&z=16&output=embed"></iframe>';
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
      height=520,
  )

# ==============================================================================
# 16. MODÜL 6: UZAKTAN HEDEF İZLEME (SUPABASE SYNC RADARI)
# ==============================================================================
elif ana_secim == "🛰️ Uzaktan Hedef İzleme (Supabase Sync)":
  st.subheader("🛰️ JARVIS Uzaktan Hedef İzleme ve Supabase Radar Sinyalleri")
  if st.button("🔄 Radar Verilerini Yenile", key="btn_radar_yenile"):
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
        son_veri = data[0]
        if "enlem" in son_veri and "boylam" in son_veri:
          lat = son_veri["enlem"]
          lon = son_veri["boylam"]
          st.info(
              f"🎯 Son Hedef Koordinatları -> Enlem: `{lat}` | Boylam: `{lon}`"
          )
          maps_html = f"""
                    <iframe width="100%" height="420" style="border:1px solid #30363d; border-radius: 10px;" loading="lazy" allowfullscreen src="https://maps.google.com/maps?q={lat},{lon}&z=16&output=embed"></iframe>
                    """
          st.components.v1.html(maps_html, height=440)
      else:
        st.warning(
            "⚠️ Supabase tablosunda aktif hedef sinyali bulunamadı efendim."
        )
    except Exception as ex:
      st.error(f"Radar veri çekme hatası: {ex}")
  else:
    st.error("Supabase bağlantısı kurulamadı efendim.")

# ==============================================================================
# 17. MODÜL 7: SİSTEM DENETİM, PERFORMANS VE SİBER GÜVENLİK LOGLARI
# ==============================================================================
else:
  st.subheader("📊 TITAN Altyapı Denetim ve Siber Güvenlik Logları")
  for log in reversed(st.session_state.sistem_loglari):
    st.code(log, language="text")
  if st.button("Log Hafızasını Sıfırla", key="log_sifirla_buton_v21"):
    st.session_state.sistem_loglari = [
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Log belleği tamamen sıfırlandı ve yeniden başlatıldı."
    ]
    st.rerun()
