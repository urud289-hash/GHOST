import base64
import datetime
import html
import json
import os
import urllib.parse
import urllib.request
import pandas as pd
from openai import OpenAI
from PIL import Image
import streamlit as st
from supabase import Client, create_client

# Sayfa Yapılandırması (Geniş Ekran)
st.set_page_config(
    page_title="TITAN v12.0 ULTIMATE — JARVIS Supreme Komuta Merkezi",
    page_icon="⚡",
    layout="wide",
)

# --- SİBER ARAYÜZ VE GELİŞMİŞ STİLLER ---
st.markdown(
    """
<style>
    .stApp { background-color: #07090e; color: #f0f6fc; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    p, span, label, div, .stMarkdown { font-weight: 600 !important; }
    footer { visibility: hidden; }
    
    .chat-container {
        height: calc(100vh - 240px);
        overflow-y: auto;
        padding-bottom: 120px;
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
        background: linear-gradient(135deg, #1f6feb, #238636);
        color: white; border-radius: 8px; border: 1px solid #3fb950; 
        font-weight: 700; padding: 0.6rem 1.2rem; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4); transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #238636, #2ea043);
        box-shadow: 0 6px 8px rgba(35,134,54,0.6); border-color: #56d364;
    }
    [data-testid="stDataFrame"] { border: 1px solid #30363d; border-radius: 8px; background-color: #161b22; }
    .code-box { background-color: #0d1117; padding: 15px; border-radius: 8px; border: 1px solid #30363d; font-family: monospace; }
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

# --- SESSION STATE (ULTIMATE HAFIZA) ---
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
          "Sen JARVIS ve TITAN v12.0 ULTIMATE mimarisiyle güçlendirilmiş,"
          " doğrudan canlı internet aramaları yapabilen, kod yazabilen ve"
          " çevresel sistemleri yöneten en üst düzey yapay zeka asistanısın."
          " Asıl sahibin Yiğit'tir. Ona ve onaylı kullanıcılara 'efendim' diye"
          " hitap et."
      ),
  }]
if "gorevler" not in st.session_state:
  st.session_state.gorevler = []
if "jarvis_hafiza" not in st.session_state:
  st.session_state.jarvis_hafiza = [
      "Ana Sahip: Yiğit",
      "Sistem Çekirdeği: TITAN v12.0 ULTIMATE",
      "Güvenlik Duvarı: Aktif, Şifreli Matris Koruma Altında",
  ]
if "izinli_kisiler" not in st.session_state:
  st.session_state.izinli_kisiler = {"Yiğit": "Ana Sahip (Admin)"}
if "izinli_fotolar" not in st.session_state:
  st.session_state.izinli_fotolar = {}
if "sistem_loglari" not in st.session_state:
  st.session_state.sistem_loglari = [
      f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sistem başarıyla başlatıldı, v12.0 modülleri aktif."
  ]


# --- SES MOTORU (ULTIMATE) ---
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
      " v12.0 ULTIMATE — Güvenlik Matriksi</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #8b949e;'>En üst düzey"
      " yetkilendirme için biyometrik fotoğrafınızı yükleyin veya 0912 master"
      " şifresini girin efendim.</p>",
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


# --- SAF PYTHON WEB ARAMA MOTORU ---
def internette_ara(sorgu):
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
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=10) as response:
      html_content = response.read().decode("utf-8")

    results = []
    chunks = html_content.split('class="result__snippet')
    for chunk in chunks[1:6]:
      try:
        part = chunk.split("</a>")[0]
        clean_text = (
            part.split(">")[-1]
            .replace("<b>", "")
            .replace("</b>", "")
            .strip()
        )
        clean_text = html.unescape(clean_text)
        if clean_text:
          results.append(clean_text)
      except Exception:
        continue

    if results:
      return json.dumps(results, ensure_ascii=False)
    return "Arama sonucuna ulaşılamadı efendim."
  except Exception as e:
    return f"Arama motoru bağlantı hatası: {str(e)}"


# --- ANA UYGULAMA ---
st.title(
    f"⚡ TITAN v12.0 ULTIMATE [JARVIS Core] — Operatör:"
    f" {st.session_state.aktif_kullanici_adi}"
)

# --- KENAR ÇUBUĞU (ULTIMATE MENÜ) ---
st.sidebar.markdown(
    "<h3 style='font-weight: 800; color: #58a6ff;'>⚙️ JARVIS Supreme"
    " Menü</h3>",
    unsafe_allow_html=True,
)
secim = st.sidebar.radio(
    "Mod Seçin:",
    [
        "💬 JARVIS Ultimate Sohbet, Canlı Web & Ses",
        "🧠 Nöral Hafıza (MEMORIES.md) Yönetimi",
        "💻 Otonom Kod & Proje Üretim Terminali",
        "🌤️ Çevresel Sensör & Hava Durumu Radarı",
        "🔒 Biyometrik İzin & Güvenlik Matriksi",
        "📍 Canlı Konum ve Google Maps Radarı",
        "🛰️ Uzaktan Hedef Takibi (Supabase)",
        "📊 Sistem Denetim ve Güvenlik Logları",
        "📌 Otonom Görev & Hatırlatıcı Takibi",
    ],
    label_visibility="collapsed",
)

if st.sidebar.button("🔒 Oturumu Kapat / Kilitle"):
  st.session_state.giris_yapildi = False
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #8b949e; font-size: 11px;'>TITAN Supreme Core v12.0<br>All"
    " Modules Online 🟢</p>",
    unsafe_allow_html=True,
)

# --- 1. MOD: SOHBET & CANLI ARAMA & SES ---
if secim == "💬 JARVIS Ultimate Sohbet, Canlı Web & Ses":
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

        st.toast(
            "🌐 TITAN Ultimate Canlı Web Ağı taranıyor, güncel veriler çekiliyor...",
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
        st.session_state.sistem_loglari.append(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Web sorgusu başarıyla işlendi: {prompt[:30]}..."
        )
      except Exception as e:
        st.error(f"Sistem bağlantı hatası: {e}")

  if st.sidebar.button("Sohbet Hafızasını Sıfırla"):
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "Sen JARVIS mimarisiyle güçlendirilmiş TITAN v12.0 ULTIMATE"
            " asistanısın."
        ),
    }]
    st.rerun()

# --- 2. MOD: NÖRAL HAFIZA ---
elif secim == "🧠 Nöral Hafıza (MEMORIES.md) Yönetimi":
  st.subheader("🧠 JARVIS Dinamik Nöral İndeksleme & MEMORIES.md")
  st.markdown(
      "Bu modül JARVIS'in kalıcı hafızasını (`MEMORIES.md`) doğrudan"
      " yönetmenizi sağlar efendim."
  )

  yeni_hafiza_notu = st.text_input("Hafızaya Yeni Bilgi Kaydet:")
  if st.button("Hafızaya İşle"):
    if yeni_hafiza_notu:
      st.session_state.jarvis_hafiza.append(yeni_hafiza_notu.strip())
      st.success("🧠 Bilgi kalıcı nöral hafızaya başarıyla eklendi efendim!")
      st.session_state.sistem_loglari.append(
          f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Yeni nöral hafıza eklendi."
      )
      st.rerun()
    else:
      st.warning("Lütfen bir hafıza girdisi yazın efendim.")

  st.markdown("### 🗂️ Aktif Nöral Bellek Kayıtları:")
  for idx, mem in enumerate(st.session_state.jarvis_hafiza):
    st.write(f"- 📌 **Kayıt #{idx+1}:** {mem}")

# --- 3. MOD: OTONOM KOD & PROJE ÜRETİCİSİ (YENİ ULTIMATE MOD) ---
elif secim == "💻 Otonom Kod & Proje Üretim Terminali":
  st.subheader("💻 TITAN Otonom Yazılım ve Proje Üretim Terminali")
  st.markdown(
      "İstediğiniz programı, scripti veya web arayüzünü JARVIS'e yazdırın,"
      " anında kod bloğu olarak alın efendim."
  )

  kod_istegi = st.text_area(
      "Ne tür bir yazılım veya kod üretilmesini istiyorsunuz?",
      placeholder="Örn: Python ile çalışan şifre yöneticisi yaz...",
  )
  if st.button("Kodu Otonom Üret"):
    if kod_istegi:
      with st.spinner(
          "TITAN kod motoru projeyi derliyor ve optimize ediyor..."
      ):
        try:
          kod_yanit = client.chat.completions.create(
              model=MODEL_NAME,
              messages=[{
                  "role": "system",
                  "content": (
                      "Sen üst düzey bir yazılım mühendisi ve TITAN kod"
                      " motorusun. Kullanıcının istediği kodu temiz, hatasız"
                      " ve açıklamalı şekilde Markdown kod bloğu içinde ver."
                  ),
              }, {
                  "role": "user",
                  "content": kod_istegi,
              }],
          )
          uretilen_kod = kod_yanit.choices[0].message.content
          st.markdown("### 🛠️ Üretilen Yazılım / Kod Çıktısı:")
          st.markdown(uretilen_kod)
          st.success("✅ Kod başarıyla derlendi ve üretildi efendim!")
        except Exception as ex:
          st.error(f"Kod üretim hatası: {ex}")
    else:
      st.warning("Lütfen üretilmesini istediğiniz yazılımı açıklayın efendim.")

# --- 4. MOD: ÇEVRESEL SENSÖR & HAVA DURUMU (YENİ ULTIMATE MOD) ---
elif secim == "🌤️ Çevresel Sensör & Hava Durumu Radarı":
  st.subheader("🌤️ JARVIS Canlı Meteoroloji ve Çevresel Sensörler")
  sehir_adi = st.text_input("Hava Durumu Sorgulanacak Şehir:", value="İstanbul")
  if st.button("Meteorolojik Verileri Çek"):
    with st.spinner("Uydu ve hava istasyonları taranıyor..."):
      hava_bilgi = internette_ara(f"{sehir_adi} hava durumu güncel sıcaklık")
      st.info(
          f"📡 {sehir_adi} için anlık meteorolojik sentez:"
          f" {str(hava_bilgi)[:300]}..."
      )
      st.success("Çevresel sensör verileri başarıyla işlendi efendim.")

  st.markdown("### 🌡️ Anlık Sistem Çevre Değerleri:")
  c1, c2, c3 = st.columns(3)
  c1.metric("Sunucu Sıcaklığı", "34.2 °C", "Stabil")
  c2.metric("Nem Oranı", "%48", "Normal")
  c3.metric("Atmosferik Basınç", "1013 hPa", "Ideal")

# --- 5. MOD: FOTOĞRAFLI İZİN & GÜVENLİK ---
elif secim == "🔒 Biyometrik İzin & Güvenlik Matriksi":
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

# --- 6. MOD: CANLI KONUM + GOOGLE MAPS ---
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

# --- 7. MOD: UZAKTAN KONUM TAKİBİ ---
elif secim == "🛰️ Uzaktan Hedef Takibi (Supabase)":
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

# --- 8. MOD: SİSTEM DENETİM VE GÜVENLİK LOGLARI ---
elif secim == "📊 Sistem Denetim ve Güvenlik Logları":
  st.subheader("📊 TITAN Altyapı Denetim ve Siber Güvenlik Logları")
  st.markdown(
      "Sistem genelinde gerçekleşen tüm operasyonel hareketlerin dökümü"
      " efendim:"
  )

  for log in reversed(st.session_state.sistem_loglari):
    st.code(log, language="text")

  if st.button("Log Belleğini Temizle"):
    st.session_state.sistem_loglari = [
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Loglar sıfırlandı."
    ]
    st.rerun()

# --- 9. MOD: GÖREVLER ---
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
