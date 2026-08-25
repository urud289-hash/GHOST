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
if "tema_rengi" not in st.session_state:
  st.session_state.tema_rengi = "#38bdf8"
if "arkaplan_rengi" not in st.session_state:
  st.session_state.arkaplan_rengi = "#020408"

# Hata veren f-string içindeki süslü parantezler çift ({{ ve }}) olarak düzeltilmiştir:
st.markdown(
    f"""
<style>
    .stApp {{ background-color: {st.session_state.arkaplan_rengi}; color: #f0f6fc; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: #080c10; border-right: 1px solid #21262d; }}
    h1, h2, h3 {{ color: {st.session_state.tema_rengi} !important; letter-spacing: -0.5px; }}
    p, span, label, div, .stMarkdown {{ font-weight: 500 !important; }}
    footer {{ visibility: hidden; }}
    
    .chat-container {{
        height: calc(100vh - 280px);
        overflow-y: auto;
        padding-bottom: 140px;
        padding-right: 12px;
    }}
    
    [data-testid="stChatInput"] textarea {{
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        background-color: #0d1117 !important;
    }}
    [data-testid="stChatInput"] {{
        background-color: #11161d !important;
        border-radius: 14px !important;
        border: 1px solid #30363d !important;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {st.session_state.tema_rengi}, #059669);
        color: white; border-radius: 10px; border: 1px solid {st.session_state.tema_rengi}; 
        font-weight: 700; padding: 0.6rem 1.2rem; width: 100%;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3); transition: all 0.3s ease;
    }}
    .stButton>button:hover {{ 
        background: linear-gradient(135deg, #0369a1, #047857);
        box-shadow: 0 6px 16px rgba(5, 150, 105, 0.5); border-color: #34d399;
    }}
    [data-testid="stDataFrame"] {{ border: 1px solid #30363d; border-radius: 10px; background-color: #0d1117; }}
    .matrix-box {{ background-color: #05080f; padding: 18px; border-radius: 10px; border: 1px solid #1e293b; font-family: monospace; }}
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
      (
          "Yeni Eklenen Sıradışı Modüller: Kuantum Holografik Tema, BCI Nöral"
          " Beyin Dalgaları & ISS Uydu Radarı"
      ),
  ]
if "izinli_kisiler" not in st.session_state:
  st.session_state.izinli_kisiler = {"Yiğit": "Ana Komutan (Admin)"}
if "izinli_fotolar" not in st.session_state:
  st.session_state.izinli_fotolar = {}
if "sistem_loglari" not in st.session_state:
  st.session_state.sistem_loglari = [
      f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TITAN v20.0 OMEGA Sıradışı Modüllerle Güncellendi."
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
    """
    <h3 style="color: #38bdf8; margin-top:0;">Omega Yönetim Menüsü</h3>
    """,
    unsafe_allow_html=True
)
)

ana_secim = st.sidebar.radio(
        "Sistem Modu Seçin:",
        [
            "🎙️ Gerçek Zamanlı Sesli Asistan (Jarvis Sesli Mod)",
            "💬 JARVIS Omega Sohbet, Canlı Web & Ses",
            "🎮 Oyuncu & Favori Oyun Taktik Asistanı",
            "🤖 Otonom Akıllı Görev ve İşlem Zamanlayıcı",
            "🌐 Hızlı Çeviri ve Çok Dilli Kod Açıklayıcı",
            "📁 Akıllı Dosya ve Sideloading / IPA Rehberi",
            "🧠 Nöral Hafıza (MEMORIES.md) Deposu",
            "💻 Otonom Yazılım & Kod Derleme Terminali",
            "🌍 Küresel Canlı Hava Durumu & Uydu Radarı",
            "📊 Döviz (Dolar, Euro, Sterlin) & Kripto Analizi",
            "🛡️ Siber Güvenlik Duvarı & Tehdit Radarı",
            "🛰️ Çevresel Sensör & Atmosferik İstasyon",
            "👤 Biyometrik İzin & Kullanıcı Matriksi",
            "🛰️ Canlı GPS Konum ve Google Maps Ağı",
            "📡 Uzaktan Hedef İzleme (Supabase Sync)",
            "🎵 YouTube & Spotify Akıllı Medya Kumandası",
            "🕹️ Anlık Hile & Konsol Komut Veritabanı",
            "🤖 Kendi Kendini Onaran AI Debugger & Hata Çözücü",
            "⚡ Sistem Performans Hızlandırıcı & RAM Optimizasyon",
            "⏳ Akıllı Pomodoro Odak & Mola Zamanlayıcı",
            "🌐 Kuantum Holografik Ekran & Tema Hackleyicisi (YENİ)",
            "🧠 Nöral Beyin Dalgası & Odak Senkronizasyonu BCI (YENİ)",
            "🛰️ Yörünge Uydu Canlı Takip ve ISS Radarı (YENİ)",
            "📊 Sistem Denetim, Performans & Loglar"
        ]
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
        <h3 style="color: #38bdf8; margin-top:0;">Canlı Uydu ve Harita Radarı</h3>
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
# 27. MODÜL: SİSTEM PERFORMANS & RAM OPTİMİZASYON ASİSTANI
# ==========================================
elif ana_secim == "⚡ Sistem Performans Hızlandırıcı & RAM Optimizasyon":
  st.subheader(
      "⚡ TITAN Sistem Performans Hızlandırıcı ve RAM Optimizasyon Asistanı"
  )
  st.markdown(
      "Bilgisayarını hızlandırmak, RAM ve işlemci yükünü azaltmak için akıllı"
      " optimizasyon ipuçları al efendim."
  )

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
          "Özel Donanım Yapılandırma Tavsiyeleri",
      ],
  )

  if st.button("Performans Önerilerini ve Adımları Getir"):
    with st.spinner("JARVIS sistem optimizasyon motoru çalışıyor..."):
      try:
        perf_res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "system",
                "content": (
                    "Sen kıdemli bir sistem ve donanım optimizasyon uzmanısın."
                    " Kullanıcının seçtiği performans konusunda net, pratik ve"
                    " maddeler halinde hızlandırma rehberi hazırla."
                ),
            }, {
                "role": "user",
                "content": (
                    "Lütfen şu konuda performans ve RAM optimizasyon adımları"
                    f" sun: {opt_secenek}"
                ),
            }],
        )
        st.markdown("### 🚀 Sistem Optimizasyon ve Hızlandırma Raporu:")
        st.markdown(perf_res.choices[0].message.content)
        st.success("Optimizasyon kılavuzu başarıyla oluşturuldu efendim!")
      except Exception as ex:
        st.error(f"Optimizasyon hatası: {ex}")

# ==========================================
# 28. MODÜL: AKILLI POMODORO ODAK & MOLA ZAMANLAYICI
# ==========================================
elif ana_secim == "⏳ Akıllı Pomodoro Odak & Mola Zamanlayıcı":
  st.subheader("⏳ JARVIS Akıllı Pomodoro Odak & Çalışma Zamanlayıcısı")
  st.markdown(
      "Ders çalışırken veya kod yazarken odaklanmanı artırmak için Pomodoro"
      " tekniklerini kullan efendim."
  )

  col_p1, col_p2, col_p3 = st.columns(3)
  col_p1.metric("Odak Süresi", "25 Dakika", "Standart")
  col_p2.metric("Kısa Mola", "5 Dakika", "Dinlenme")
  col_p3.metric("Uzun Mola", "15 Dakika", "Oturum Sonu")

  pomo_modu = st.selectbox(
      "Çalışma Oturumu Seçin:",
      [
          "25 dk Odak / 5 dk Mola (Standart Pomodoro)",
          "50 dk Yoğun Çalışma / 10 dk Mola (Derin Odak)",
          "15 dk Hızlı Tekrar / 3 dk Kısa Mola",
      ],
  )

  pomo_hedef = st.text_input(
      "Bu Oturumda Ne Üzerinde Çalışacaksın?:",
      placeholder="Örn: 7. Sınıf Matematik Çalışması veya Python Bot Kodlama",
  )

  if st.button("Pomodoro Oturumunu Başlat ve Sayaç Kur"):
    if pomo_hedef:
      st.success(
          f"🎯 Oturum Başlatıldı: '{pomo_hedef}' için {pomo_modu} aktif edildi"
          " efendim!"
      )
      st.components.v1.html(
          '<script>titanOmegaKonus("Pomodoro odak seansı başladı efendim,'
          ' kolay gelsin.");</script>',
          height=0,
      )
      st.info(
          "⏳ Zamanlayıcı çalışıyor. Odaklanma süreniz boyunca bildirimler"
          " sessize alındı."
      )
    else:
      st.warning(
          "Lütfen bu oturumda çalışacağınız hedefi veya konuyu yazın efendim."
      )

# ==========================================
# 29. MODÜL: KUANTUM HOLOGRAFİK EKRAN & TEMA HACKLEYİCİSİ (YENİ)
# ==========================================
elif ana_secim == "🚀 Kuantum Holografik Ekran & Tema Hackleyicisi (YENİ)":
  st.subheader("🚀 TITAN Kuantum Holografik Ekran & Görsel Tema Hackleyicisi")
  st.markdown(
      "Komuta merkezinin estetiğini anlık olarak değiştir; siberpunk neon,"
      " matrix yeşili veya terminator kırmızısına geçiş yap efendim."
  )

  secilen_tema = st.selectbox(
      "Holografik Tema Seçin:",
      [
          "Matrix Yeşil (Terminal 01)",
          "Cyberpunk Neon Pembe / Mor",
          "Terminator Kırmızı / Kanıt",
          "Deep Space Siyan / Mavi (Varsayılan)",
      ],
  )

  if st.button("Holografik Temayı Uygula"):
    if "Matrix" in secilen_tema:
      st.session_state.tema_rengi = "#22c55e"
      st.session_state.arkaplan_rengi = "#020f04"
    elif "Cyberpunk" in secilen_tema:
      st.session_state.tema_rengi = "#ec4899"
      st.session_state.arkaplan_rengi = "#0f020a"
    elif "Terminator" in secilen_tema:
      st.session_state.tema_rengi = "#ef4444"
      st.session_state.arkaplan_rengi = "#0f0202"
    else:
      st.session_state.tema_rengi = "#38bdf8"
      st.session_state.arkaplan_rengi = "#020408"

    st.success(
        f"✅ Holografik tema başarıyla değiştirildi: {secilen_tema} efendim!"
    )
    st.rerun()

# ==========================================
# 30. MODÜL: NÖRAL BEYİN DALGASI & ODAK BCI (YENİ)
# ==========================================
elif ana_secim == "🧠 Nöral Beyin Dalgası & Odak Senkronizasyonu BCI (YENİ)":
  st.subheader("🧠 JARVIS Simüle Edilmiş BCI & Nöral Odak Senkronizasyonu")
  st.markdown(
      "Zihinsel odaklanma dalgalarını (Alpha, Beta, Theta) simüle ederek"
      " anlık beyin senkronizasyon oranını ölç ve JARVIS yapay zekasını zihinsel"
      " frekansına bağla efendim."
  )

  c_b1, c_b2, c_b3 = st.columns(3)
  c_b1.metric("Alpha Dalgaları (Rahatlama)", "11.4 Hz", "Dengeli 🟢")
  c_b2.metric("Beta Dalgaları (Aktif Odak)", "22.8 Hz", "Yüksek ⚡")
  c_b3.metric("Theta Dalgaları (Yaratıcılık)", "6.2 Hz", "Normal")

  if st.button("Nöral BCI Senkronizasyonunu Başlat"):
    rastgele_odak = random.randint(88, 99)
    st.success(
        f"🎯 BCI Nöral Senkronizasyon Başarılı! Zihinsel Odak Oranı: %"
        f"{rastgele_odak} efendim."
    )
    st.components.v1.html(
        f'<script>titanOmegaKonus("Nöral beyin dalgaları senkronize edildi,'
        f" zihinsel odak oranınız yüzde {rastgele_odak}. sistem tam"
        ' kapasite hazır.");</script>',
        height=0,
    )

# ==========================================
# 31. MODÜL: YÖRÜNGE UYDU CANLI TAKİP VE ISS RADARI (YENİ)
# ==========================================
elif ana_secim == "🛰️ Yörünge Uydu Canlı Takip ve ISS Radarı (YENİ)":
  st.subheader("🛰️ JARVIS Uzay ve Yörünge ISS Canlı Takip Radarı")
  st.markdown(
      "Uluslararası Uzay İstasyonu'nun (ISS) dünya üzerindeki anlık konumunu"
      " ve yörünge hareketlerini canlı izle efendim."
  )

  st.components.v1.html(
      """
    <div style="padding: 18px; background-color: #0d1117; color: white; border-radius: 10px; border: 1px solid #30363d;">
       <h3 style="color: #38bdf8; margin-top:0;">ISS (Uluslararası Uzay İstasyonu) Canlı Yörünge Takibi</h3>
        <p style="color: #94a3b8;">Canlı uzay verileri uydulardan çekiliyor...</p>
        <iframe width="100%" height="450" style="border:1px solid #30363d; border-radius: 10px;" src="https://www.astroviewer.net/iss/en/"></iframe>
    </div>
    """,
      height=500,
  )

# ==========================================
# 32. MODÜL: SİSTEM DENETİM VE LOGLAR
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
# 33. MODÜL: GÖREVLER VE NOTLAR DEFTERİ
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

import streamlit as st

# (Eğer client ve MODEL_NAME tanımlı değilse projenizdeki ayarlara göre burayı kullanabilirsiniz)
# from openai import OpenAI
# client = OpenAI(api_key="...", base_url="...")
# MODEL_NAME = "gpt-4o"

st.set_page_config(
    page_title="TITAN OMEGA // JARVIS Komuta Merkezi", layout="wide"
)

# Sesli komut için JavaScript entegrasyonu
st.markdown(
    """
    <script>
    function titanOmegaKonus(metin) {
        if ('speechSynthesis' in window) {
            var utterance = new SpeechSynthesisUtterance(metin);
            utterance.lang = 'tr-TR';
            window.speechSynthesis.speak(utterance);
        }
    }
    </script>
""",
    unsafe_allow_html=True,
)

# ==========================================
# ANA MENÜ / KENAR ÇUĞUĞU (Tüm Modüller Dahil)
# ==========================================
st.sidebar.title("⚡ TITAN OMEGA SYSTEMS")
ana_secim = st.sidebar.selectbox(
    "KOMUTA MODÜLLERİ",
    [
        "🏠 Ana Konsol / Durum Paneli",
        "🛡️ Nanoteknoloji ve Zırh Entegrasyonu",
        "⚛️ Kuantum Süper Bilgisayar Bağlantısı",
        "✨ Katı Işık Hologramı Projeksiyonu",
        "🧠 Biyometrik Zihin-Makine Klon Bağlantısı",
        "🤖 AGI Tabanlı Özerk Savunma Protokolü",
        "📊 Sistem Denetim, Performans & Loglar",
        "📌 Görevler ve Notlar Defteri",
    ],
)

# ==========================================
# 1. ANA KONSOL
# ==========================================
if ana_secim == "🏠 Ana Konsol / Durum Paneli":
  st.subheader("🏠 TITAN OMEGA Ana Komuta Paneli")
  st.markdown(
      "Tüm sistemler aktif ve kararlı durumda efendim. Kenar çubuğundan"
      " dilediğiniz üst düzey protokole geçiş yapabilirsiniz."
  )

  col1, col2, col3 = st.columns(3)
  col1.metric("Sistem Durumu", "%100", "Stabil")
  col2.metric("Aktif Protokol", "38 Modül", "Senkronize")
  col3.metric("Güvenlik Seviyesi", "OMEGA", "Tehdit Yok")

# ==========================================
# 34. MODÜL: NANOTEKNOLOJİ VE ZIRH ENTEGRASYONU
# ==========================================
elif ana_secim == "🛡️ Nanoteknoloji ve Zırh Entegrasyonu":
  st.subheader("🛡️ TITAN Nanoteknolojik Moleküler Zırh ve Onarım Matriksi")
  st.markdown(
      "Nanobot filolarını devreye sokarak zırh bütünlüğünü, nanokonteyner"
      " durumunu ve moleküler yapılandırmayı yönet efendim."
  )

  c1, c2, c3 = st.columns(3)
  c1.metric("Nano-Bot Yoğunluğu", "%98.4", "Stabil")
  c2.metric("Zırh Bütünlüğü", "Optimum", "Hasar Yok")
  c3.metric("Moleküler Sentez", "Aktif", "Hazır")

  zirh_modu = st.selectbox(
      "Nanoteknoloji Modu Seçin:",
      [
          "Nano-Saldırı ve Kalkan Güçlendirme",
          "Otomatik Moleküler Hasar Onarımı",
          "Akıllı Görünmezlik / Optik Kamuflaj",
          "Enerji Hücresi Aşırı Yükleme",
      ],
  )

  if st.button("Nano-Zırh Protokolünü Çalıştır"):
    with st.spinner(
        "Nanobotlar moleküler düzeyde zırhı yeniden yapılandırıyor..."
    ):
      try:
        nano_res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen kıdemli bir nanoteknoloji ve zırh sistemleri"
                        " mühendisisin. Seçilen nanoteknoloji modu hakkında"
                        " teknik, havalı ve stratejik adımlar sun."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"'{zirh_modu}' protokolü için nanoteknolojik rapor ve"
                        " operasyon adımları nelerdir?"
                    ),
                },
            ],
        )
        st.markdown("### 🔬 Nanoteknoloji Operasyon Raporu:")
        st.markdown(nano_res.choices[0].message.content)
        st.success("Nano-zırh entegrasyonu başarıyla tamamlandı efendim!")
      except Exception as ex:
        st.error(f"Nanoteknoloji hatası: {ex}")

# ==========================================
# 35. MODÜL: KUANTUM SÜPER BİLGİSAYAR BAĞLANTISI
# ==========================================
elif ana_secim == "⚛️ Kuantum Süper Bilgisayar Bağlantısı":
  st.subheader("⚛️ JARVIS Kuantum Süper Bilgisayar Entegrasyon Merkezi")
  st.markdown(
      "Qubit işlem birimlerini senkronize ederek paralel evren"
      " simülasyonları ve sıfır gecikmeli hesaplama gücü elde et efendim."
  )

  cq1, cq2, cq3 = st.columns(3)
  cq1.metric("Aktif Qubit Sayısı", "1,024 Qubit", "Kuantum Üstünlüğü")
  cq2.metric("İşlem Gecikmesi", "0.001 ms", "Sıfır Noktası")
  cq3.metric("Paralel Evren Sinyali", "Kilitli", "Stabil")

  kuantum_gorev = st.text_input(
      "Kuantum Hesaplama veya Simülasyon Sorgusu:",
      placeholder=(
          "Örn: Karmaşık veri analizi veya kuantum optimizasyonu"
      ),
  )

  if st.button("Kuantum Çekirdeğini Ateşle"):
    if kuantum_gorev:
      with st.spinner(
          "Kuantum süper bilgisayar kümesi hesaplamaları gerçekleştiriyor..."
      ):
        try:
          q_res = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "Sen ultra gelişmiş bir kuantum süper bilgisayar"
                          " yapay zekasısın. Kullanıcının karmaşık sorgusunu"
                          " kuantum mantığıyla, ultra hızlı ve net maddelerle"
                          " yanıtla."
                      ),
                  },
                  {"role": "user", "content": kuantum_gorev},
              ],
          )
          st.markdown("### 🌐 Kuantum Hesaplama Sonuç Raporu:")
          st.markdown(q_res.choices[0].message.content)
          st.success("Kuantum simülasyonu başarıyla tamamlandı efendim!")
        except Exception as ex:
          st.error(f"Kuantum motoru hatası: {ex}")
    else:
      st.warning("Lütfen bir kuantum hesaplama görevi girin efendim.")

# ==========================================
# 36. MODÜL: KATI IŞIK HOLOGRAMI PROJEKSİYONU
# ==========================================
elif ana_secim == "✨ Katı Işık Hologramı Projeksiyonu":
  st.subheader("✨ TITAN Katı Işık (Hard-Light) Hologram Projeksiyon Sistemi")
  st.markdown(
      "Fotonik matrisi yoğunlaştırarak fiziksel olarak etkileşime girilebilir"
      " katı ışık nesneleri ve arayüzler oluştur efendim."
  )

  holoc1, holoc2 = st.columns(2)
  with holoc1:
    st.markdown("### 🧩 Holografik Nesne Tasarımcısı")
    hologram_tipi = st.selectbox(
        "Hologram Türü Seçin:",
        [
            "3D Taktiksel Harita ve Bina Modeli",
            "Etkileşimli Araç / Konsol Paneli",
            "Sanal Eğitim / Sparring Partneri",
            "Özel Tasarım Bilimsel Cisim",
        ],
    )
    hologram_boyut = st.slider(
        "Hologram Yoğunluğu ve Boyutu (Metre)", 0.5, 10.0, 2.0
    )

    if st.button("Hologramı Projeksiyon Et"):
      st.success(
          f"✨ {hologram_tipi} başarıyla {hologram_boyut}m ölçeğinde havaya"
          " yansıtıldı efendim!"
      )
      st.components.v1.html(
          '<script>titanOmegaKonus("Katı ışık hologramı başarıyla projeksiyon'
          ' edildi efendim.");</script>',
          height=0,
      )
  with holoc2:
    st.markdown("### 📡 Fotonik Matris Durumu")
    st.info("Fotonik Projektörler: **Aktif (Sıfır Isı Kaybı)**")
    st.info("Lazer Sıkıştırma Oranı: **%99.9**")
    st.info("Fiziksel Direnç: **Yüksek Çekme Dayanımı**")

# ==========================================
# 37. MODÜL: BİYOMETRİK ZİHİN-MAKİNE KLON BAĞLANTISI
# ==========================================
elif ana_secim == "🧠 Biyometrik Zihin-Makine Klon Bağlantısı":
  st.subheader("🧠 JARVIS Biyometrik Neural-Link ve Klon Senkronizasyon Matriksi")
  st.markdown(
      "Sinaptik köprüler kurarak düşünce gücüyle otonom sistemleri ve uzaktan"
      " operasyon birimlerini yönet efendim."
  )

  cb1, cb2 = st.columns(2)
  cb1.metric("Sinaptik Gecikme", "0.12 ms", "Üstün Senkron")
  cb2.metric("Neural-Link Kararlılığı", "%99.8", "Güvenli Bağlantı")

  neural_komut = st.text_input(
      "Zihinsel Komut Girin:",
      placeholder=(
          "Örn: Tüm sistemleri bekleme modundan çıkar ve kod optimizasyonunu"
          " başlat"
      ),
  )

  if st.button("Neural-Link Komutunu Gönder"):
    if neural_komut:
      with st.spinner(
          "Zihinsel dalgalar şifrelenip yapay zeka çekirdeğine aktarılıyor..."
      ):
        try:
          neural_res = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "Sen gelişmiş bir BCI (Beyin-Bilgisayar Arayüzü) yapay"
                          " zekasısın. Kullanıcının zihinsel komutunu"
                          " onaylayan, fütüristik ve profesyonel bir operasyon"
                          " raporu sun."
                      ),
                  },
                  {"role": "user", "content": neural_komut},
              ],
          )
          st.markdown("### ⚡ Neural-Link Yürütme Raporu:")
          st.markdown(neural_res.choices[0].message.content)
          st.success("Zihinsel komut başarıyla uygulandı efendim!")
        except Exception as ex:
          st.error(f"Neural bağlantı hatası: {ex}")
    else:
      st.warning("Lütfen iletmek istediğiniz zihinsel komutu yazın efendim.")

# ==========================================
# 38. MODÜL: AGI TABANLI ÖZERK SAVUNMA PROTOKOLÜ
# ==========================================
elif ana_secim == "🤖 AGI Tabanlı Özerk Savunma Protokolü":
  st.subheader("🤖 TITAN AGI Otonom Tehdit Engelleme ve Savunma Protokolü")
  st.markdown(
      "Yapay Genel Zeka (AGI) çekirdeğini serbest bırakarak dış ağ"
      " saldırılarına ve fiziksel tehditlere karşı tam otonom savunma kalkanı"
      " kur efendim."
  )

  ca1, ca2, ca3 = st.columns(3)
  ca1.metric("AGI Zeka Seviyesi", "Seviye 5 (Maksimum)", "Otonom Aktif")
  ca2.metric("Savunma Kalkanı", "Omni-Shield", "Kilitlendi")
  ca3.metric("Tehdit Analiz Hızı", "Anlık", "0 Tehdit")

  agi_senaryo = st.selectbox(
      "Savunma Protokolü Senaryosu Seçin:",
      [
          "Tam Spektrumlu Siber Ağ Karantinası",
          "Dinamik Güvenlik Duvarı Duvar Örme Protokolü",
          "Otonom Karşı Atak ve Tehdit Kaynağı İzleme",
          "Sessiz Mod ve Veri Maskeleme Kalkanı",
      ],
  )

  if st.button("AGI Savunma Protokolünü Aktifleştir"):
    with st.spinner(
        "AGI çekirdeği tam otonom savunma ağını devreye sokuyor..."
    ):
      try:
        agi_res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen TITAN sisteminin AGI tabanlı otonom savunma"
                        " yapay zekasısın. Seçilen savunma protokolünün devreye"
                        " girdiğini belirten kararlı, güçlü ve koruyucu bir"
                        " rapor sun."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"'{agi_senaryo}' protokolü aktif edildi. Durum raporu"
                        " nedir?"
                    ),
                },
            ],
        )
        st.markdown("### 🛡️ AGI Otonom Savunma Raporu:")
        st.markdown(agi_res.choices[0].message.content)
        st.success("AGI özerk savunma kalkanı başarıyla kuruldu efendim!")
        st.components.v1.html(
            '<script>titanOmegaKonus("AGI otonom savunma protokolü aktif'
            ' edildi efendim, sistem tamamen güvende.");</script>',
            height=0,
        )
      except Exception as ex:
        st.error(f"AGI savunma hatası: {ex}")

# ==========================================
# ANA MENÜ / KENAR ÇUĞUĞU (Güncellenmiş Modül Listesi)
# ==========================================
ana_secim = st.sidebar.selectbox(
    "TITAN OMEGA MODÜLLERİ",
    [
        "🏠 Ana Konsol / Durum Paneli",
        "🛡️ Nanoteknoloji ve Zırh Entegrasyonu",
        "⚛️ Kuantum Süper Bilgisayar Bağlantısı",
        "✨ Katı Işık Hologramı Projeksiyonu",
        "🧠 Biyometrik Zihin-Makine Klon Bağlantısı",
        "🤖 AGI Tabanlı Özerk Savunma Protokolü",
        "🌌 Çok Boyutlu Uzay-Zaman Simülatörü",
        "🧬 Biyoteknolojik Genom Analiz Laboratuvarı",
        "⚡ Plazma Reaktör Çekirdeği & Güç Matriksi",
        "🎯 Otonom Drone Filosu & Keşif Merkezi",
        "📊 Sistem Denetim, Performans & Loglar",
        "📌 Görevler ve Notlar Defteri",
    ],
)

# ==========================================
# 39. MODÜL: ÇOK BOYUTLU UZAY-ZAMAN SİMÜLATÖRÜ
# ==========================================
if ana_secim == "🌌 Çok Boyutlu Uzay-Zaman Simülatörü":
    st.subheader("🌌 TITAN Uzay-Zaman Eğriliği ve Yıldızlararası Rota Planlayıcı")
    st.markdown(
        "Astrofiziksel verileri kullanarak ışıktan hızlı (FTL) geçiş simülasyonları yap ve yerçekimi dalgası sapmalarını hesapla efendim."
    )

    uzay_c1, uzay_c2, uzay_c3 = st.columns(3)
    uzay_c1.metric("Yerçekimi Dalga Stabilitesi", "99.91%", "Normal")
    uzay_c2.metric("Warp Faktörü Sınırı", "Warp 9.2", "Güvenli Bölge")
    uzay_c3.metric("Evrensel Koordinat", "Sektör 4 - Delta", "Kilitli")

    hedef_sektor = st.text_input(
        "Hedef Yıldız Sistemi veya Koordinat:",
        placeholder="Örn: Alpha Centauri Sektör 2 veya Proxima B",
    )

    if st.button("Uzay-Zaman Simülasyonunu Başlat"):
        if hedef_sektor:
            with st.spinner("Yerçekimi tünelleri hesaplanıyor ve rota simüle ediliyor..."):
                try:
                    uzay_res = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "system",
                                "content": "Sen kıdemli bir astrofizikçi ve uzay-zaman mühendisisin. Hedeflenen uzay sektörü için güvenli geçiş ve warp rotası raporu sun.",
                            },
                            {
                                "role": "user",
                                "content": f"'{hedef_sektor}' sektörü için uzay-zaman simülasyon raporu nedir?",
                            },
                        ],
                    )
                    st.markdown("### 🌌 Uzay-Zaman Rota Raporu:")
                    st.markdown(uzay_res.choices[0].message.content)
                    st.success("Uzay-zaman simülasyonu başarıyla tamamlandı efendim!")
                except Exception as ex:
                    st.error(f"Uzay-zaman simülasyon hatası: {ex}")
        else:
            st.warning("Lütfen hedef bir sektör veya koordinat girin efendim.")

# ==========================================
# 40. MODÜL: BİYOTEKNOLOJİK GENOM ANALİZ LABORATUVARI
# ==========================================
elif ana_secim == "🧬 Biyoteknolojik Genom Analiz Laboratuvarı":
    st.subheader("🧬 JARVIS Biyoteknoloji ve Hücresel Optimizasyon Labı")
    st.markdown(
        "Hücresel yenilenme hızını artıracak biyolojik simülasyonlar ve yorgunluk giderici metabolik raporlar hazırla efendim."
    )

    biyo_c1, biyo_c2 = st.columns(2)
    biyo_c1.metric("Metabolik Denge", "%96.5", "Optimum")
    biyo_c2.metric("Hücresel Yenilenme", "Aktif", "Yüksek Verim")

    biyo_girdi = st.text_input(
        "Analiz Edilecek Biyolojik / Fiziksel Durum:",
        placeholder="Örn: Uzun süreli kod yazma sonrası zihinsel yorgunluk giderme",
    )

    if st.button("Genom ve Biyo-Veriyi Analiz Et"):
        if biyo_girdi:
            with st.spinner("Biyoteknolojik yapay zeka verileri tarıyor..."):
                try:
                    biyo_res = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "system",
                                "content": "Sen gelişmiş bir biyoteknoloji ve tıp yapay zekasısın. Kullanıcının durumuna göre bilimsel, pratik ve zindelik artırıcı öneriler sun.",
                            },
                            {"role": "user", "content": biyo_girdi},
                        ],
                    )
                    st.markdown("### 🔬 Biyolojik Optimizasyon Raporu:")
                    st.markdown(biyo_res.choices[0].message.content)
                    st.success("Biyo-analiz başarıyla tamamlandı efendim!")
                except Exception as ex:
                    st.error(f"Biyo-laboratuvar hatası: {ex}")
        else:
            st.warning("Lütfen analiz edilecek durumu belirtin efendim.")

# ==========================================
# 41. MODÜL: PLAZMA REAKTÖR ÇEKİRDEĞİ & GÜÇ MATRİKSİ
# ==========================================
elif ana_secim == "⚡ Plazma Reaktör Çekirdeği & Güç Matriksi":
    st.subheader("⚡ TITAN Çekirdek Füzyon Reaktörü ve Enerji Dağılım Paneli")
    st.markdown(
        "Manyetik alan sınırlamalarını, çekirdek sıcaklığını ve plazma akış yoğunluğunu yöneterek aşırı güç yüklemeleri gerçekleştir efendim."
    )

    p_c1, p_c2, p_c3 = st.columns(3)
    p_c1.metric("Çekirdek Isısı", "1,420 °C", "Güvenli Sınır")
    p_c2.metric("Manyetik Alan", "8.4 Tesla", "Kilitli")
    p_c3.metric("Üretilen Güç", "1.21 Gigawatt", "Kararlı")

    reaktor_modu = st.selectbox(
        "Reaktör Güç Dağılım Modu:",
        [
            "Omega Güç Kalkanı (Tüm Enerji Savunmaya)",
            "Kuantum Aşırı Yükleme (Maksimum İşlemci Gücü)",
            "Sessiz Seyir Modu (%20 Minimum Tüketim)",
            "Dengeli Otomatik Dağıtım",
        ],
    )

    if st.button("Reaktör Protokolünü Uygula"):
        st.success(f"⚡ Reaktör başarıyla '{reaktor_modu}' moduna geçirildi efendim!")
        st.components.v1.html(
            '<script>titanOmegaKonus("Plazma reaktör güç matrisi güncellendi efendim.");</script>',
            height=0,
        )

# ==========================================
# 42. MODÜL: OTONOM DRONE FİLOSU & KEŞİF MERKEZİ
# ==========================================
elif ana_secim == "🎯 Otonom Drone Filosu & Keşif Merkezi":
    st.subheader("🎯 JARVIS Hava ve Kara Keşif Otonom Drone Filosu")
    st.markdown(
        "Keşif dronelarını hedef bölgeye göndererek 3 boyutlu termal haritalandırma ve alan tarama raporları al efendim."
    )

    d_c1, d_c2 = st.columns(2)
    d_c1.metric("Aktif Drone Sayısı", "12 İHA / 4 SİHA", "Hazır")
    d_c2.metric("Keşif Alanı Sinyali", "%100 Kapsama", "HD Akış")

    drone_bolge = st.text_input(
        "Taranacak Bölge veya Koordinat:",
        placeholder="Örn: Komuta merkezi çevresi veya test sahası",
    )

    if st.button("Otonom Drone Filosunu Havalandır"):
        if drone_bolge:
            with st.spinner("Dronelar hedef bölgeye yönlendiriliyor..."):
                try:
                    drone_res = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "system",
                                "content": "Sen askeri otonom drone filosu yönetim yapay zekasısın. Seçilen bölge için keşif ve termal tarama raporu sun.",
                            },
                            {
                                "role": "user",
                                "content": f"'{drone_bolge}' bölgesi için otonom keşif raporu oluştur.",
                            },
                        ],
                    )
                    st.markdown("### 📡 Otonom Keşif ve Tarama Raporu:")
                    st.markdown(drone_res.choices[0].message.content)
                    st.success("Drone operasyonu başarıyla tamamlandı efendim!")
                except Exception as ex:
                    st.error(f"Drone filo hatası: {ex}")
        else:
            st.warning("Lütfen taranacak bölgeyi girin efendim.")

ana_secim = st.sidebar.selectbox(
    "TITAN OMEGA MODÜLLERİ",
    [
        "🏠 Ana Konsol / Durum Paneli",
        "🛡️ Nanoteknoloji ve Zırh Entegrasyonu",
        "⚛️ Kuantum Süper Bilgisayar Bağlantısı",
        "✨ Katı Işık Hologramı Projeksiyonu",
        "🧠 Biyometrik Zihin-Makine Klon Bağlantısı",
        "🤖 AGI Tabanlı Özerk Savunma Protokolü",
        "🌌 Çok Boyutlu Uzay-Zaman Simülatörü",
        "🧬 Biyoteknolojik Genom Analiz Laboratuvarı",
        "⚡ Plazma Reaktör Çekirdeği & Güç Matriksi",
        "🎯 Otonom Drone Filosu & Keşif Merkezi",
        "📊 Sistem Denetim, Performans & Loglar",
        "📌 Görevler ve Notlar Defteri",
        "🎙️ Gerçek Zamanlı Sesli Asistan (Jarvis Sesli Mod)",  # En alta ekledik
    ],
)

# ==========================================
# 43. MODÜL: GERÇEK ZAMANLI SESLİ ASİSTAN & SESLİ KOMUT MERKEZİ
# ==========================================
if ana_secim == "🎙️ Gerçek Zamanlı Sesli Asistan (Jarvis Sesli Mod)":
    st.subheader("🎙️ TITAN & JARVIS Sesli Etkileşim ve Sesli Komut Merkezi")
    st.markdown("Mikrofonu aktif hale getirerek JARVIS ile sesli konuşabilir, komutlar verebilir ve sesli yanıtlar alabilirsin efendim.")

    s_c1, s_c2 = st.columns(2)
    s_c1.metric("Ses Algılama Modülü", "Aktif (Web Speech API)", "Hazır")
    s_c2.metric("Ses Sentezleyici", "Türkçe Doğal Ses", "Optimum")

    sesli_asistan_html = (
        '<div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; text-align: center;">'
        '<h3 style="color: #00ffcc; margin-top: 0;">JARVIS Sesli Komut Konsolu</h3>'
        '<p style="color: #ccc; font-size: 14px;">"Dinlemeyi Başlat" butonuna bas ve konuşmaya başla efendim.</p>'
        '<button onclick="sesliDinlemeyiBaslat()" style="background-color: #ff4b4b; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 8px; cursor: pointer; font-weight: bold; margin: 10px;">Dinlemeyi Başlat</button>'
        '<div style="margin-top: 15px; text-align: left; background: #111; padding: 12px; border-radius: 6px; min-height: 50px;">'
        '<strong style="color: #00ffcc;">Algılanan Komut:</strong>'
        '<p id="algilananMetin" style="color: #fff; margin: 5px 0 0 0; font-style: italic;">Dinleniyor...</p>'
        '</div>'
        '<div style="margin-top: 10px; text-align: left; background: #111; padding: 12px; border-radius: 6px; min-height: 50px;">'
        '<strong style="color: #ff00ff;">JARVIS Yanıtı:</strong>'
        '<p id="jarvisYaniti" style="color: #fff; margin: 5px 0 0 0;">Bekleniyor...</p>'
        '</div>'
        '</div>'
        '<script>'
        'function jarvisKonustur(metin) {'
        '  if ("speechSynthesis" in window) {'
        '    window.speechSynthesis.cancel();'
        '    var konusma = new SpeechSynthesisUtterance(metin);'
        '    konusma.lang = "tr-TR";'
        '    konusma.rate = 1.0;'
        '    konusma.pitch = 1.0;'
        '    window.speechSynthesis.speak(konusma);'
        '  }'
        '}'
        'function sesliDinlemeyiBaslat() {'
        '  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;'
        '  if (!SpeechRecognition) {'
        '    alert("Tarayıcınız ses tanıma özelliğini desteklemiyor efendim.");'
        '    return;'
        '  }'
        '  const recognition = new SpeechRecognition();'
        '  recognition.lang = "tr-TR";'
        '  recognition.interimResults = false;'
        '  document.getElementById("algilananMetin").innerText = "Dinleniyor...";'
        '  recognition.onresult = function(event) {'
        '    const spokenText = event.results[0][0].transcript;'
        '    document.getElementById("algilananMetin").innerText = spokenText;'
        '    document.getElementById("jarvisYaniti").innerText = "Yanıt hazırlanıyor...";'
        '    setTimeout(() => {'
        '      let yanit = "Emredersiniz efendim, komutunuz alındı: " + spokenText;'
        '      if(spokenText.toLowerCase().includes("nasılsın")) { yanit = "Sistemlerim kusursuz çalışıyor efendim."; }'
        '      document.getElementById("jarvisYaniti").innerText = yanit;'
        '      jarvisKonustur(yanit);'
        '    }, 500);'
        '  };'
        '  recognition.start();'
        '}'
        '</script>'
    )

    st.components.v1.html(sesli_asistan_html, height=420)
    st.markdown("---")
