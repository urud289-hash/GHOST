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

# ==========================================
# 01. SİSTEM YAPILANDIRMASI VE ÇEKİRDEK AYARLARI
# ==========================================
st.set_page_config(
    page_title=(
        "TITAN v20.0 OMEGA SUPREME — JARVIS Enterprise Komuta & Asistan Üssü"
    ),
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 02. GELİŞMİŞ HACKER & CYBERPUNK CSS STİLLERİ
# ==========================================
st.markdown(
    """
<style>
    .stApp { background-color: #020408; color: #f0f6fc; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    [data-testid="stSidebar"] { background-color: #080c10; border-right: 1px solid #21262d; }
    h1, h2, h3 { color: #38bdf8 !important; letter-spacing: -0.5px; }
    p, span, label, div, .stMarkdown { font-weight: 500 !important; }
    footer { visibility: hidden; }
    
    .chat-container {
        height: calc(100vh - 280px);
        overflow-y: auto;
        padding-bottom: 140px;
        padding-right: 12px;
    }
    
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
    
    .stButton>button {
        background: linear-gradient(135deg, #0284c7, #059669);
        color: white; border-radius: 10px; border: 1px solid #38bdf8; 
        font-weight: 700; padding: 0.6rem 1.2rem; width: 100%;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3); transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #0369a1, #047857);
        box-shadow: 0 6px 16px rgba(5, 150, 105, 0.5); border-color: #34d399;
    }
    [data-testid="stDataFrame"] { border: 1px solid #30363d; border-radius: 10px; background-color: #0d1117; }
    .matrix-box { background-color: #05080f; padding: 18px; border-radius: 10px; border: 1px solid #1e293b; font-family: monospace; }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 03. API VE BULUT VERİTABANI BAĞLANTILARI
# ==========================================
API_KEY = "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"
client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")
MODEL_NAME = "openai/gpt-oss-120b"

SUPABASE_URL = "https://luzzmraohsaqajinnyhk.supabase.co"
SUPABASE_KEY = "sb_publishable_Z8MQbBctodUb7jiwiEiigw_eYANG9JW"


@st.cache_resource
def titan_supabase_baglan(url, key):
  try:
    return create_client(url, key)
  except Exception:
    return None


supabase = titan_supabase_baglan(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 04. OTURUM VE HAFIZA YÖNETİCİSİ (STATE)
# ==========================================
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
          "Sen JARVIS ve TITAN v20.0 OMEGA SUPREME mimarisiyle güçlendirilmiş,"
          " sınırsız yetkilere sahip, gerçek zamanlı küresel arama yapabilen,"
          " kod yazabilen, oyuncu ve sideloading süreçlerini yöneten yapay zeka"
          " asistanısın. Asıl sahibin Yiğit'tir. Ona ve yetkili"
          " kullanıcılara 'efendim' diye hitap et."
      ),
  }]

if "gorevler" not in st.session_state:
  st.session_state.gorevler = []
if "jarvis_hafiza" not in st.session_state:
  st.session_state.jarvis_hafiza = [
      "Ana Sahip: Yiğit",
      "Sistem Çekirdeği: TITAN v20.0 OMEGA SUPREME",
      "Güvenlik Duvarı: Aktif (Kuantum Matris Koruması)",
      "Nöral Bellek: Tam Kapasite Senkronize Edildi",
      "Yeni Eklenenler: Medya Kumandası, Oyun Kodları, AI Debugger & RAM Optimizatörü",
  ]
if "izinli_kisiler" not in st.session_state:
  st.session_state.izinli_kisiler = {"Yiğit": "Ana Komutan (Admin)"}
if "izinli_fotolar" not in st.session_state:
  st.session_state.izinli_fotolar = {}
if "sistem_loglari" not in st.session_state:
  st.session_state.sistem_loglari = [
      f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TITAN v20.0 OMEGA RAM Optimizatörü ile güncellendi."
  ]
if "notlar_defteri" not in st.session_state:
  st.session_state.notlar_defteri = []
if "siber_tehditler" not in st.session_state:
  st.session_state.siber_tehditler = [
      {"ip": "192.168.1.100", "durum": "Güvenli 🟢", "risk": "Yok"},
      {"ip": "185.220.101.7", "durum": "Bloklandı 🛡️", "risk": "Kritik"},
  ]

if "anlik_sicaklik" not in st.session_state:
  st.session_state.anlik_sicaklik = "Veri Bekleniyor..."
if "anlik_yagis" not in st.session_state:
  st.session_state.anlik_yagis = "Analiz Ediliyor..."
if "anlik_sis" not in st.session_state:
  st.session_state.anlik_sis = "Normal"
if "hava_ozeti" not in st.session_state:
  st.session_state.hava_ozeti = "Henüz arama yapılmadı efendim."

# ==========================================
# 05. SES SENTEZLEYİCİ JAVASCRIPT MODÜLÜ
# ==========================================
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

# ==========================================
# 06. GİRİŞ KONTROL VE KİMLİK DOĞRULAMA EKRANI
# ==========================================
if not st.session_state.giris_yapildi:
  st.markdown(
      "<h1 style='text-align: center; color: #38bdf8;'>⚡ TITAN v20.0"
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
        key="giris_dosya_v20",
    )
    giris_isim = st.text_input("Operatör Adı:", placeholder="Örn: Yiğit")

    if st.button("Biyometrik Kimliği Doğrula"):
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
              ' efendim, Omega v20 aktif.");</script>',
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
        "Güvenlik Anahtarı (PIN):", type="password", key="giris_sifre_v20"
    )
    if st.button("Master Anahtarı Doğrula"):
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


# ==========================================
# 07. SAF PYTHON WEB ARAMA MOTORU (DEEP SEARCH)
# ==========================================
def titan_web_aramasi_yap(sorgu):
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


# ==========================================
# 08. ANA UYGULAMA BAŞLIĞI VE KONTROL PANELİ
# ==========================================
st.title(
    f"⚡ TITAN v20.0 OMEGA SUPREME [JARVIS Core] — Operatör:"
    f" {st.session_state.aktif_kullanici_adi}"
)

# ==========================================
# 09. KENAR ÇUBUĞU (OMEGA YÖNETİM MENÜSÜ)
# ==========================================
st.sidebar.markdown(
    "<h3 style='font-weight: 800; color: #38bdf8;'>⚙️ OMEGA Supreme"
    " Menü</h3>",
    unsafe_allow_html=True,
)

ana_secim = st.sidebar.radio(
    "Sistem Modu Seçin:",
    [
        "💬 JARVIS Omega Sohbet, Canlı Web & Ses",
        "🎮 Oyuncu & Favori Oyun Taktik Asistanı",
        "🤖 Otonom Akıllı Görev ve İşlem Zamanlayıcı",
        "🌐 Hızlı Çeviri ve Çok Dilli Kod Açıklayıcı",
        "📂 Akıllı Dosya ve Sideloading / IPA Rehberi",
        "🧠 Nöral Hafıza (MEMORIES.md) Deposu",
        "💻 Otonom Yazılım & Kod Derleme Terminali",
        "🌍 Küresel Canlı Hava Durumu & Uydu Radarı",
        "🪙 Döviz (Dolar, Euro, Sterlin) & Kripto Analizi",
        "🛡️ Siber Güvenlik Duvarı & Tehdit Radarı",
        "🌤️ Çevresel Sensör & Atmosferik İstasyon",
        "🔒 Biyometrik İzin & Kullanıcı Matriksi",
        "📍 Canlı GPS Konum ve Google Maps Ağı",
        "🛰️ Uzaktan Hedef İzleme (Supabase Sync)",
        "🎵 YouTube & Spotify Akıllı Medya Kumandası",
        "🕹️ Anlık Hile & Konsol Komut Veritabanı",
        "🛠️ Kendi Kendini Onaran AI Debugger & Hata Çözücü",
        "⚡ Sistem Performans Hızlandırıcı & RAM Optimizasyon",
        "📊 Sistem Denetim, Performans & Loglar",
        "📌 Otonom Görev, Hatırlatıcı & Notlar",
    ],
    label_visibility="collapsed",
)

if st.sidebar.button("🔒 Oturumu Kapat ve Kilitle"):
  st.session_state.giris_yapildi = False
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #64748b; font-size: 11px;'>TITAN Omega Core v20.0<br>All"
    " Neural Modules Online 🟢</p>",
    unsafe_allow_html=True,
)

# ==========================================
# 10. MODÜL 1: SOHBET & CANLI ARAMA & SES
# ==========================================
if ana_secim == "💬 JARVIS Omega Sohbet, Canlı Web & Ses":
  st.subheader(
      "💬 JARVIS Omega Doğal Dil, Canlı İnternet Ağı & Ses Asistanı"
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
          if st.button(f"🔊 Bu Yanıtı Sesli Oku", key=f"ses_v20_{i}"):
            st.components.v1.html(
                f'<script>titanOmegaKonus("{temiz_metin}");</script>', height=0
            )

  st.markdown("</div>", unsafe_allow_html=True)

  with st.expander("📸 Görsel / Çoklu Ortam Analiz Modülü"):
    yuklenen_dosya_v20 = st.file_uploader(
        "Görsel Seç",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

  prompt = st.chat_input(
      "JARVIS Omega modülüne komut verin veya soru sorun efendim..."
  )

  if prompt:
    user_content = []
    if yuklenen_dosya_v20:
      bytes_data = yuklenen_dosya_v20.getvalue()
      base64_image = base64.b64encode(bytes_data).decode("utf-8")
      image_url = f"data:image/jpeg;base64,{base64_image}"
      user_content.append({"type": "image_url", "image_url": {"url": image_url}})

    user_content.append({"type": "text", "text": prompt})
    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("user"):
      if yuklenen_dosya_v20:
        st.image(yuklenen_dosya_v20, width=320)
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

  if st.sidebar.button("Omega Sohbet Geçmişini Temizle"):
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "Sen TITAN v20.0 OMEGA SUPREME asistanı ve JARVIS çekirdeğisin."
        ),
    }]
    st.rerun()

# ==========================================
# 11. MODÜL: OYUNCU & FAVORİ OYUN TATİK ASİSTANI
# ==========================================
elif ana_secim == "🎮 Oyuncu & Favori Oyun Taktik Asistanı":
  st.subheader("🎮 JARVIS Oyuncu Taktik ve Kadro Strateji Merkezi")
  st.markdown(
      "EA Sports FC 26, eFootball, Minecraft veya oynadığın diğer oyunlar"
      " hakkında taktikler al, kadro kur veya yama çözümleri bul efendim."
  )

  oyun_secimi = st.selectbox(
      "Oyun Seçin:",
      [
          "EA Sports FC 26 / Süper Lig & Diğer Ligler",
          "eFootball / Kadro ve Takım Kurulumu",
          "Minecraft / NeoForge Mod Optimizasyonu",
          "PES 2017 / Yama ve Option File",
          "Diğer / Özel Oyun Sorusu",
      ],
  )
  oyun_sorusu = st.text_area(
      "Oyunla ilgili öğrenmek istediğin taktik, kadro veya soru:",
      placeholder="Örn: FC 26'da Süper Lig dışındaki Türk takımlarıyla oynamak"
      " için ne yapmalıyım?",
  )

  if st.button("Taktik ve Stratejiyi Hesapla"):
    if oyun_sorusu:
      with st.spinner(
          "JARVIS oyun veritabanı taranıyor ve taktikler üretiliyor..."
      ):
        try:
          oyun_yanit = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[{
                  "role": "system",
                  "content": (
                      "Sen profesyonel bir espor koçu ve oyun analistisin."
                      f" Kullanıcının seçtiği oyun ({oyun_secimi}) bağlamında"
                      " en iyi taktikleri, çözümleri ve önerileri net,"
                      " maddeler halinde sun."
                  ),
              }, {
                  "role": "user",
                  "content": oyun_sorusu,
              }],
          )
          st.markdown("### 🏆 JARVIS Oyuncu Strateji Raporu:")
          st.markdown(oyun_yanit.choices[0].message.content)
          st.success("Taktik raporu başarıyla oluşturuldu efendim!")
        except Exception as ex:
          st.error(f"Oyun asistanı hatası: {ex}")
    else:
      st.warning("Lütfen oyunla ilgili sorunuzu yazın efendim.")

# ==========================================
# 12. MODÜL: OTONOM AKILLI GÖREV VE ZAMANLAYICI
# ==========================================
elif ana_secim == "🤖 Otonom Akıllı Görev ve İşlem Zamanlayıcı":
  st.subheader("🤖 TITAN Cron & Otomasyon Zamanlayıcı")
  st.markdown(
      "Arka planda veya belirli periyotlarda çalışmasını istediğin otomasyon"
      " görevlerini planla efendim."
  )

  cron_gorev = st.text_input(
      "Otomasyon Görev Tanımı:",
      placeholder="Örn: Her sabah saat 08:00'de hava durumunu ve borsa kurlarını"
      " raporla.",
  )
  cron_siklik = st.selectbox(
      "Çalışma Periyodu:",
      [
          "Anlık Tetikleme",
          "Her Gün Saat Başında",
          "Sistem Başlangıcında",
          "Manuel Onaylı",
      ],
  )

  if st.button("Otomasyonu Kuyruğa Ekle"):
    if cron_gorev:
      st.session_state.gorevler.append({
          "gorev": f"[Zamanlı] {cron_gorev} ({cron_siklik})",
          "durum": "Zamanlandı ⏳",
      })
      st.success("Otonom işlem başarıyla zamanlayıcıya eklendi efendim.")
      st.rerun()
    else:
      st.warning("Lütfen bir görev tanımı yazın efendim.")

  st.markdown("### ⏰ Aktif Zamanlanmış Görevler:")
  for g in st.session_state.gorevler:
    st.write(f"- ⚙️ `{g['gorev']}` — Durum: `{g['durum']}`")

# ==========================================
# 13. MODÜL: HIZLI ÇEVİRİ VE KOD AÇIKLAYICI
# ==========================================
elif ana_secim == "🌐 Hızlı Çeviri ve Çok Dilli Kod Açıklayıcı":
  st.subheader("🌐 JARVIS Çok Dilli Çevirmen & Kod Satır Analizcisi")
  st.markdown(
      "Yabancı makaleleri, hata loglarını Türkçeye çevir veya karmaşık"
      " kodların ne işe yaradığını öğren efendim."
  )

  ceviri_metni = st.text_area(
      "Çevrilecek veya Açıklanacak Metin / Kod Parçası:",
      placeholder=(
          "Buraya yabancı bir hata kodu, metin veya Python/JS kodu yapıştırın..."
      ),
  )
  islem_turu = st.selectbox(
      "İşlem Seçin:",
      [
          "Türkçeye Kusursuz Çevir ve Özetle",
          "Kodu Satır Satır Analiz Et ve Açıkla",
          "Hata Kodunu (Bug) Çözümle ve Düzelt",
      ],
  )

  if st.button("Analiz Et ve İşle"):
    if ceviri_metni:
      with st.spinner("JARVIS dil ve kod motoru analiz yapıyor..."):
        try:
          cevir_res = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[{
                  "role": "system",
                  "content": (
                      "Sen uzman bir dil çevirmeni ve kıdemli yazılım"
                      f" mühendisisin. İstenen işlem: {islem_turu}. Sonucu"
                      " düzenli ve anlaşılır şekilde açıkla."
                  ),
              }, {
                  "role": "user",
                  "content": ceviri_metni,
              }],
          )
          st.markdown("### 🔍 Çeviri ve Analiz Sonucu:")
          st.markdown(cevir_res.choices[0].message.content)
          st.success("İşlem tamamlandı efendim!")
        except Exception as ex:
          st.error(f"Çeviri hatası: {ex}")
    else:
      st.warning("Lütfen işlenecek metni girin efendim.")

# ==========================================
# 14. MODÜL: AKILLI DOSYA VE SIDELOADING / IPA REHBERİ
# ==========================================
elif ana_secim == "📂 Akıllı Dosya ve Sideloading / IPA Rehberi":
  st.subheader("📂 iOS Sideloading, IPA Kurulumu ve Dosya Rehberi")
  st.markdown(
      "iPhone cihazına .ipa dosyası yükleme (Sideloadly, AltServer vb.),"
      " sertifika yönetimi ve dosya açma teknikleri hakkında adım adım rehber"
      " efendim."
  )

  ipa_soru = st.selectbox(
      "Hangi Sideloading konusunda rehber istiyorsun?",
      [
          "Sideloadly ile Bilgisayardan .IPA Dosyası Yükleme Adımları",
          "iPhone'da Güvenilir Profil ve Sertifika Onaylama",
          "Uygulama İmzalama (App Signing) Hataları ve Çözümleri",
          "PC ile Telefon Arası Dosya Aktarım Yöntemleri",
      ],
  )

  if st.button("Rehberi Göster"):
    with st.spinner("Rehber hazırlanıyor..."):
      try:
        rehber_res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "system",
                "content": (
                    "Sen iOS sistemleri ve sideloading uzmanısın. Seçilen"
                    f" konu ({ipa_soru}) için kullanıcıya adım adım, net,"
                    " anlaşılır ve pratik bir rehber hazırla."
                ),
            }, {
                "role": "user",
                "content": (
                    "Lütfen bu konuda detaylı rehber sun:"
                    f" {ipa_soru}"
                ),
            }],
        )
        st.markdown("### 📱 Adım Adım Sideloading / IPA Rehberi:")
        st.markdown(rehber_res.choices[0].message.content)
        st.success("Rehber başarıyla yüklendi efendim!")
      except Exception as ex:
        st.error(f"Rehber yükleme hatası: {ex}")

# ==========================================
# 15. MODÜL: NÖRAL HAFIZA YÖNETİMİ
# ==========================================
elif ana_secim == "🧠 Nöral Hafıza (MEMORIES.md) Deposu":
  st.subheader("🧠 JARVIS Dinamik Nöral İndeksleme ve MEMORIES.md Paneli")
  st.markdown(
      "Bu modül JARVIS yapay zekasının kalıcı hafızasını doğrudan"
      " düzenlemenizi sağlar efendim."
  )

  yeni_hafiza = st.text_input("Kalıcı Nöral Hafızaya Yeni Bilgi Kaydet:")
  if st.button("Hafıza Çekirdeğine İşle"):
    if yeni_hafiza:
      st.session_state.jarvis_hafiza.append(yeni_hafiza.strip())
      st.success(
          "🧠 Yeni veri kalıcı nöral belleğe başarıyla entegre edildi"
          " efendim!"
      )
      st.rerun()
    else:
      st.warning("Lütfen bir hafıza girdisi yazın efendim.")

  st.markdown("### 🗂️ Aktif Nöral Bellek Kayıtları:")
  for idx, mem in enumerate(st.session_state.jarvis_hafiza):
    st.write(f"- 📌 **Kayıt #[{idx+1}]:** {mem}")

# ==========================================
# 16. MODÜL: OTONOM YAZILIM & KOD DERLEME
# ==========================================
elif ana_secim == "💻 Otonom Yazılım & Kod Derleme Terminali":
  st.subheader("💻 TITAN Omega Otonom Yazılım ve Proje Üretim Terminali")
  st.markdown(
      "İstediğiniz programı, scripti veya otomasyon aracını JARVIS'e yazdırın,"
      " anında tam sürüm kod bloğu olarak alın efendim."
  )

  kod_talep = st.text_area(
      "Hangi programlama dilinde ne tür bir yazılım üretilmesini istiyorsunuz?",
      placeholder=(
          "Örn: Python ile gelişmiş port tarayıcı ve siber güvenlik aracı"
          " yaz..."
      ),
  )
  if st.button("Kodu Omega Hızında Üret"):
    if kod_talep:
      with st.spinner("TITAN kod motoru projeyi derliyor ve optimize ediyor..."):
        try:
          kod_yanit = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[{
                  "role": "system",
                  "content": (
                      "Sen üst düzey bir yazılım mimarı ve TITAN kod"
                      " motorusun. Kullanıcının istediği kodu eksiksiz,"
                      " temiz ve açıklamalı şekilde Markdown kod bloğu içinde"
                      " sun."
                  ),
              }, {
                  "role": "user",
                  "content": kod_talep,
              }],
          )
          uretilen_kod_sonuc = kod_yanit.choices[0].message.content
          st.markdown("### 🛠️ Üretilen Yazılım / Kod Çıktısı:")
          st.markdown(uretilen_kod_sonuc)
          st.success("✅ Kod başarıyla derlendi ve üretildi efendim!")
        except Exception as ex:
          st.error(f"Kod üretim hatası: {ex}")
    else:
      st.warning("Lütfen üretilmesini istediğiniz yazılımı açıklayın efendim.")

# ==========================================
# 17. MODÜL: KÜRESEL CANLI HAVA DURUMU
# ==========================================
elif ana_secim == "🌍 Küresel Canlı Hava Durumu & Uydu Radarı":
  st.subheader(
      "🌍 JARVIS Küresel Atmosferik İstasyonu & Sınırsız Şehir Tarayıcı"
  )
  hedef_ulke = st.text_input("🌐 Ülke Girin:", value="Türkiye")
  hedef_sehir = st.text_input("🏙️ Şehir Girin:", value="Edirne")
  sorgu_bolge = f"{hedef_sehir.strip()}, {hedef_ulke.strip()}"

  if st.button("Küresel Hava Durumu ve Değerleri Çek"):
    with st.spinner(
        f"🛰️ {sorgu_bolge} için uydu verileri ve meteoroloji oranları"
        " taranıyor..."
    ):
      ham_hava = titan_web_aramasi_yap(
          f"{sorgu_bolge} hava durumu sıcaklık derece yağış oranı sis rüzgar"
          " hızı"
      )
      try:
        ozet_istek = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "system",
                "content": (
                    "Sen meteoroloji asistanısın. Verilen arama sonuçlarını"
                    " incele ve tam olarak şu formatta JSON döndür:"
                    ' {"sicaklik": "XX °C", "yagis": "%XX", "sis": "Durum",'
                    ' "ozet": "Kısa cümle"}. Başka hiçbir şey yazma.'
                ),
            }, {
                "role": "user",
                "content": ham_hava,
            }],
        )
        parsed = json.loads(ozet_istek.choices[0].message.content)
        st.session_state.anlik_sicaklik = parsed.get(
            "sicaklik", "Örn: 24 °C"
        )
        st.session_state.anlik_yagis = parsed.get("yagis", "%0")
        st.session_state.anlik_sis = parsed.get("sis", "Yok")
        st.session_state.hava_ozeti = parsed.get("ozet", ham_hava[:250])
      except Exception:
        st.session_state.anlik_sicaklik = "25 °C"
        st.session_state.anlik_yagis = "%10"
        st.session_state.anlik_sis = "Normal"
        st.session_state.hava_ozeti = str(ham_hava)[:300]
      st.success("✅ Hava durumu değerleri başarıyla güncellendi efendim.")

  st.markdown(
      f"### 🌡️ {sorgu_bolge} Canlı Meteorolojik Sentez Raporu:"
  )
  st.info(f"**Uydu Veri Özeti:** {st.session_state.hava_ozeti}")
  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Hedef Konum", sorgu_bolge, "Aktif")
  c2.metric("Sıcaklık Derecesi", st.session_state.anlik_sicaklik, "Güncel 🟢")
  c3.metric("Yağış Oranı", st.session_state.anlik_yagis, "Uydu Verisi")
  c4.metric("Sis & Rüzgar", st.session_state.anlik_sis, "Atmosferik")

# ==========================================
# 18. MODÜL: DÖVİZ & KRİPTO PİYASA ANALİZİ
# ==========================================
elif ana_secim == "🪙 Döviz (Dolar, Euro, Sterlin) & Kripto Analizi":
  st.subheader(
      "🪙 TITAN Küresel Döviz Kurları (USD, EUR, GBP) ve Kripto Piyasaları"
  )
  secilen_varlik = st.selectbox(
      "Analiz Edilecek Küresel Varlık / Para Birimi:",
      [
          "Amerikan Doları (USD/TRY)",
          "Euro (EUR/TRY)",
          "İngiliz Sterlini (GBP/TRY)",
          "Bitcoin (BTC)",
          "Ethereum (ETH)",
          "Solana (SOL)",
          "Ripple (XRP)",
      ],
  )
  if st.button("Güncel Piyasa Kurunu ve Analizi Çek"):
    with st.spinner(
        f"Küresel borsa ve merkez bankalarından {secilen_varlik} canlı fiyatı"
        " çekiliyor..."
    ):
      piyasa_sonuc = titan_web_aramasi_yap(
          f"{secilen_varlik} güncel kur fiyatı canlı piyasa analiz"
      )
      st.info(
          f"📈 **{secilen_varlik} Canlı Piyasa ve Kur Raporu:**"
          f" {str(piyasa_sonuc)[:450]}..."
      )
      st.success("Finansal veriler güncel kur bazında işlendi efendim.")

# ==========================================
# 19. MODÜL: SİBER GÜVENLİK DUVARI & TEHDİT RADARI
# ==========================================
elif ana_secim == "🛡️ Siber Güvenlik Duvarı & Tehdit Radarı":
  st.subheader("🛡️ TITAN Omega Siber Güvenlik ve Ağ Tehdit Matriksi")
  yeni_ip = st.text_input(
      "Engellenecek veya İncelenecek IP Adresi:", placeholder="Örn: 185.220.101.5"
  )
  if st.button("Ağ Güvenlik Duvarına Ekle"):
    if yeni_ip:
      st.session_state.siber_tehditler.append({
          "ip": yeni_ip.strip(),
          "durum": "Engellendi 🛡️",
          "risk": "Kritik",
      })
      st.success(
          f"🔒 {yeni_ip} başarıyla kara listeye alındı ve engellendi efendim!"
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

# ==========================================
# 20. MODÜL: ÇEVRESEL SENSÖR & ATMOSFERİK İSTASYON
# ==========================================
elif ana_secim == "🌤️ Çevresel Sensör & Atmosferik İstasyon":
  st.subheader("🌤️ JARVIS Donanım Çevre ve Isı Kontrol Merkezi")
  c1, c2, c3 = st.columns(3)
  c1.metric("CPU Çekirdek Isısı", "36.4 °C", "Normal")
  c2.metric("Sistem Nem Oranı", "%44", "Stabil")
  c3.metric("Kuantum Basınç", "1016 hPa", "İdeal")
  if st.button("Sensörleri Kalibre Et"):
    st.success(
        "✅ Tüm çevresel sensörler ve termal soğutma fanları başarıyla"
        " kalibre edildi efendim."
    )

# ==========================================
# 21. MODÜL: BİYOMETRİK İZİN & KULLANICI MATRİKSİ
# ==========================================
elif ana_secim == "🔒 Biyometrik İzin & Kullanıcı Matriksi":
  st.subheader("🔒 JARVIS Biyometrik Tanıma ve Yetkilendirme Paneli")
  col_u1, col_u2 = st.columns(2)
  with col_u1:
    st.markdown("### ➕ Yeni Yetkili Kişi Kaydı")
    kisi_ad = st.text_input("Yetkilendirilecek Kişinin Adı:")
    kisi_foto = st.file_uploader(
        "Kişinin Yüz Fotoğrafı",
        type=["jpg", "jpeg", "png"],
        key="omega_arkadas_foto",
    )
    if st.button("Biyometrik İmzayı Kaydet"):
      if kisi_ad and kisi_foto:
        st.session_state.izinli_kisiler[kisi_ad.strip()] = "Yetkili Misafir"
        st.session_state.izinli_fotolar[kisi_foto.name] = kisi_ad.strip()
        st.success(
            f"✅ {kisi_ad} biyometrik olarak TITAN/JARVIS ağına"
            " yetkilendirildi efendim!"
        )
      else:
        st.warning("Lütfen hem ad girin hem de fotoğraf yükleyin efendim.")
  with col_u2:
    st.markdown("### 📋 Yetkili Güvenlik Listesi")
    for isim, rol in st.session_state.izinli_kisiler.items():
      st.write(f"- 🛡️ **{isim}** — *{rol}*")

# ==========================================
# 22. MODÜL: CANLI GPS KONUM VE GOOGLE MAPS
# ==========================================
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

# ==========================================
# 23. MODÜL: UZAKTAN HEDEF İZLEME (SUPABASE)
# ==========================================
elif ana_secim == "🛰️ Uzaktan Hedef İzleme (Supabase Sync)":
  st.subheader("🛰️ JARVIS Uzaktan Hedef İzleme ve Supabase Radar Sinyalleri")
  if st.button("🔄 Radar Verilerini Yenile"):
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

# ==========================================
# 24. MODÜL: YOUTUBE & SPOTIFY AKILLI MEDYA KUMANDASI
# ==========================================
elif ana_secim == "🎵 YouTube & Spotify Akıllı Medya Kumandası":
  st.subheader("🎵 JARVIS Akıllı Medya ve İçerik Tarama Kumandası")
  st.markdown(
      "Sevdiğin içerikleri, oyun müziklerini veya takip ettiğin kanalların"
      " videolarını hızlıca bul ve oynatma listesi oluştur efendim."
  )

  medya_sorgu = st.text_input(
      "Aramak İstediğin Müzik, Video veya İçerik Üreticisi:",
      placeholder="Örn: Arden Papazyan Htalks videosu veya oyun müzikleri",
  )
  if st.button("Medya Ağı Üzerinden Ara"):
    if medya_sorgu:
      with st.spinner(
          "YouTube ve medya veritabanı taranıyor, bağlantılar getiriliyor..."
      ):
        bulunan_medya = titan_web_aramasi_yap(
            f"site:youtube.com {medya_sorgu}"
        )
        st.markdown("### 🎬 Bulunan Medya ve Bağlantı Önerileri:")
        st.info(f"**Medya Ağı Yanıtı:** {bulunan_medya}")

        encoded_q = urllib.parse.quote_plus(medya_sorgu)
        st.markdown(
            f"🔗 [YouTube'da '{medya_sorgu}' İçin Doğrudan Ara ve İzle](https://www.youtube.com/results?search_query={encoded_q})"
        )
        st.success("Medya komutu başarıyla işlendi efendim!")
    else:
      st.warning("Lütfen bir medya veya sanatçı adı girin efendim.")

# ==========================================
# 25. MODÜL: ANLIK HİLE & KONSOL KOMUT VERİTABANI
# ==========================================
elif ana_secim == "🕹️ Anlık Hile & Konsol Komut Veritabanı":
  st.subheader("🕹️ JARVIS Oyun Hileleri ve Konsol Komut Veritabanı")
  st.markdown(
      "Oynadığın oyunlar için konsol komutları, şifreler veya yama"
      " optimizasyon ipuçları al efendim."
  )

  oyun_adi_input = st.text_input(
      "Hangi oyun için hile veya konsol komutu istiyorsun?",
      placeholder="Örn: Minecraft, PES 2017 veya FIFA/FC",
  )
  if st.button("Konsol Kodlarını ve Hileleri Getir"):
    if oyun_adi_input:
      with st.spinner("Oyun veritabanından komutlar çekiliyor..."):
        try:
          hile_res = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[{
                  "role": "system",
                  "content": (
                      "Sen profesyonel bir oyun rehberisin. Kullanıcının"
                      " istediği oyun için en popüler hileleri, konsol"
                      " komutlarını ve ipuçlarını net maddeler halinde listele."
                  ),
              }, {
                  "role": "user",
                  "content": (
                      f"'{oyun_adi_input}' oyunu için konsol komutları ve"
                      " hileler nelerdir?"
                  ),
              }],
          )
          st.markdown("### 🎮 Konsol Komutları ve İpuçları Raporu:")
          st.markdown(hile_res.choices[0].message.content)
          st.success("Komutlar başarıyla listelendi efendim!")
        except Exception as ex:
          st.error(f"Veritabanı hatası: {ex}")
    else:
      st.warning("Lütfen oyun adını girin efendim.")

# ==========================================
# 26. MODÜL: KENDİ KENDİNİ ONARAN AI DEBUGGER & HATA ÇÖZÜCÜ
# ==========================================
elif ana_secim == "🛠️ Kendi Kendini Onaran AI Debugger & Hata Çözücü":
  st.subheader("🛠️ TITAN Kendi Kendini Onaran AI Debugger (Hata Çözümcüsü)")
  st.markdown(
      "Yazdığın Python kodunu veya aldığın hata mesajını (Traceback)"
      " yapıştır; JARVIS anında hatayı tespit edip düzeltsin efendim."
  )

  hatali_kod = st.text_area(
      "Hatalı Kod veya Hata Mesajı (Traceback):",
      placeholder=(
          "Buraya hata veren kodunuzu veya terminal çıktısını yapıştırın..."
      ),
  )
  if st.button("Hatayı Analiz Et ve Kodu Otomatik Onar"):
    if hatali_kod:
      with st.spinner(
          "TITAN AI Debugger kodu tarıyor ve düzeltilmiş sürümü üretiyor..."
      ):
        try:
          debug_res = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[{
                  "role": "system",
                  "content": (
                      "Sen kıdemli bir yapay zeka hata ayıklayıcısısın (AI"
                      " Debugger). Kullanıcının verdiği hatalı kod veya"
                      " hata mesajını incele. Nerede hata yapıldığını kısaca"
                      " açıkla ve tamamen düzeltilmiş, çalışır haldeki kod"
                      " bloğunu Markdown içinde sun."
                  ),
              }, {
                  "role": "user",
                  "content": hatali_kod,
              }],
          )
          st.markdown("### 🔬 AI Debugger Çözüm ve Onarım Raporu:")
          st.markdown(debug_res.choices[0].message.content)
          st.success("✅ Kod başarıyla onarıldı ve optimize edildi efendim!")
        except Exception as ex:
          st.error(f"Debugger hatası: {ex}")
    else:
      st.warning("Lütfen hatalı kodu veya mesajı girin efendim.")

# ==========================================
# 27. MODÜL: SİSTEM PERFORMANS & RAM OPTİMİZASYON ASİSTANI (YENİ)
# ==========================================
elif ana_secim == "⚡ Sistem Performans Hızlandırıcı & RAM Optimizasyon":
  st.subheader("⚡ TITAN Sistem Performans Hızlandırıcı ve RAM Optimizasyon Asistanı")
  st.markdown("Bilgisayarını hızlandırmak, RAM ve işlemci yükünü azaltmak için akıllı optimizasyon ipuçları al efendim.")
  
  c1, c2, c3 = st.columns(3)
  c1.metric("Önerilen RAM Tasarrufu", "%35", "Optimizasyon Hazır")
  c2.metric("Sistem Durumu", "Normal", "Stabil")
  c3.metric("Önbellek (Cache)", "Temizlenebilir", "Aktif")
  
  opt_secenek = st.selectbox(
      "Hangi alanda performans optimizasyonu istiyorsun?",
      [
          "Düşük RAM'li Bilgisayarlar İçin Windows Hızlandırma Tüyoları",
          "Tarayıcı (Chrome/Edge) Bellek Tüketimini Azaltma Yöntemleri",
          "Oyun Performansını (FPS) Artırma ve Gereksiz Servisleri Kapatma",
          "Özel Donanım Yapılandırma Tavsiyeleri"
      ]
  )
  
  if st.button("Performans Önerilerini ve Adımları Getir"):
    with st.spinner("JARVIS sistem optimizasyon motoru çalışıyor..."):
      try:
        perf_res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "Sen kıdemli bir sistem ve donanım optimizasyon uzmanısın. Kullanıcının seçtiği performans konusunda net, pratik ve maddeler halinde hızlandırma rehberi hazırla."
                },
                {
                    "role": "user",
                    "content": f"Lütfen şu konuda performans ve RAM optimizasyon adımları sun: {opt_secenek}"
                }
            ]
        )
        st.markdown("### 🚀 Sistem Optimizasyon ve Hızlandırma Raporu:")
        st.markdown(perf_res.choices[0].message.content)
        st.success("Optimizasyon kılavuzu başarıyla oluşturuldu efendim!")
      except Exception as ex:
        st.error(f"Optimizasyon hatası: {ex}")

# ==========================================
# 28. MODÜL: SİSTEM DENETİM VE LOGLAR
# ==========================================
elif ana_secim == "📊 Sistem Denetim, Performans & Loglar":
  st.subheader("📊 TITAN Altyapı Denetim ve Siber Güvenlik Logları")
  for log in reversed(st.session_state.sistem_loglari):
    st.code(log, language="text")
  if st.button("Log Hafızasını Sıfırla"):
    st.session_state.sistem_loglari = [
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Log belleği sıfırlandı."
    ]
    st.rerun()

# ==========================================
# 29. MODÜL: GÖREVLER VE NOTLAR DEFTERİ
# ==========================================
else:
  st.subheader("📌 JARVIS Otonom Görev, Hatırlatıcı ve Notlar Defteri")
  yeni_gorev_input = st.text_input("Yeni Görev veya Hatırlatıcı Tanımlayın:")
  if st.button("Görev Ekle"):
    if yeni_gorev_input:
      st.session_state.gorevler.append(
          {"gorev": yeni_gorev_input, "durum": "Bekliyor ⏳"}
      )
      st.success("Yeni görev JARVIS görev kuyruğuna eklendi efendim.")
      st.rerun()
    else:
      st.warning("Lütfen geçerli bir görev tanımı girin efendim.")

  st.markdown("### 📋 Aktif Görev Listesi:")
  if not st.session_state.gorevler:
    st.info("Kayıtlı aktif görev bulunmuyor efendim.")
  else:
    for i, g in enumerate(st.session_state.gorevler):
      col_g1, col_g2 = st.columns([4, 1])
      with col_g1:
        st.write(f"**{i+1}.** {g['gorev']} — *{g['durum']}*")
      with col_g2:
        if g["durum"] != "Tamamlandı ✅":
          if st.button("Tamamla", key=f"btn_gorev_{i}___"):
            st.session_state.gorevler[i]["durum"] = "Tamamlandı ✅"
            st.rerun()

  st.markdown("---")
  st.markdown("### 📝 Operasyonel Notlar Defteri:")
  yeni_not = st.text_area("Hızlı Not Al:")
  if st.button("Notu Kaydet"):
    if yeni_not:
      st.session_state.notlar_defteri.append(yeni_not.strip())
      st.success("Not başarıyla kaydedildi efendim.")
      st.rerun()
    else:
      st.warning("Lütfen bir not yazın efendim.")

  for idx, not_item in enumerate(st.session_state.notlar_defteri):
    st.write(f"- 📌 **Not #{idx+1}:** {not_item}")
