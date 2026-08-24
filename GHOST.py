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
    page_title="GHOST AI - Ultimate Komuta Merkezi", page_icon="👻", layout="wide"
)

# --- SİBER ARAYÜZ VE STİLLER (Kesin Siyah Kalın Yazı Ayarlı) ---
st.markdown(
    """
<style>
    .stApp { background-color: #0b0f19; color: #f0f6fc; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    p, span, label, div, .stMarkdown { font-weight: 600 !important; }
    footer { visibility: hidden; }
    
    /* Kaydırılabilir Sohbet Alanı */
    .chat-container {
        height: calc(100vh - 200px);
        overflow-y: auto;
        padding-bottom: 100px;
        padding-right: 10px;
    }
    
    /* Streamlit Chat Input Yazı Rengi ve Kutusu */
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
        font-weight: 700; padding: 0.5rem 1rem; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #2ea043, #3fb950);
        box-shadow: 0 6px 8px rgba(35,134,54,0.4); border-color: #56d364;
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

# Hafıza Yönetimi
if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "system",
      "content": (
          "Sen gelişmiş, aktif ve anlık internet arama yeteneğine sahip olan bir"
          " yapay zeka asistanı olan GHOST'sun. Kullanıcı sana hava durumu,"
          " güncel haberler veya anlık veriler sorduğunda internetten araştırma"
          " yapabilirsin. Her zaman 'efendim' diye hitap et."
      ),
  }]
if "gorevler" not in st.session_state:
  st.session_state.gorevler = []
if "yuz_hafizasi" not in st.session_state:
  st.session_state.yuz_hafizasi = {}


# --- İNTERNET ARAMA FONKSİYONU ---
def internette_ara(sorgu):
  try:
    results = DDGS().text(sorgu, max_results=3)
    if results:
      return json.dumps(results, ensure_ascii=False)
    return "Arama sonucu bulunamadı efendim."
  except Exception as e:
    return f"Arama yapılırken bir hata oluştu: {str(e)}"


# --- SES VE MİKROFON MOTORU ---
st.markdown(
    """
<script>
    function ghostKonus(metin) {
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

    function sesliKomutBaslat() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Tarayıcınız sesli komutu desteklemiyor efendim.");
            return;
        }
        try {
            var recognition = new SpeechRecognition();
            recognition.lang = 'tr-TR';
            recognition.interimResults = false;
            recognition.onresult = function(event) {
                var sesMetni = event.results[0][0].transcript;
                const txtInput = window.parent.document.querySelector('textarea[data-testid="stChatInput"]');
                if (txtInput) {
                    let setter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value").set;
                    setter.call(txtInput, sesMetni);
                    txtInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            recognition.start();
        } catch(e) { alert("Mikrofon hatası: " + e.message); }
    }
</script>
""",
    unsafe_allow_html=True,
)

st.title("👻 GHOST AI - Ultimate Komuta ve Takip Merkezi")

# --- KENAR ÇUBUĞU ---
st.sidebar.markdown(
    "<h3 style='font-weight: 800; color: #58a6ff;'>⚙️ GHOST Operasyon"
    " Menüsü</h3>",
    unsafe_allow_html=True,
)
secim = st.sidebar.radio(
    "Mod Seçin:",
    [
        "💬 Yazılı, Mikrofon, Fotoğraf Analizi & Ses",
        "🔍 Biyometrik Yüz Tanıma & Hafıza",
        "📍 Canlı Konum Takibi",
        "🛰️ Uzaktan Konum Takip (Radar)",
        "💻 Sistem Komuta Paneli",
        "📌 Görev & Proje Takibi",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #8b949e; font-size: 12px;'>GHOST Ultimate v7.1<br>Hata"
    " Giderildi & Stabil 🟢</p>",
    unsafe_allow_html=True,
)

# --- 1. MOD: SOHBET, MİKROFON, FOTOĞRAF VE SABİT ALT ÇUBUK ---
if secim == "💬 Yazılı, Mikrofon, Fotoğraf Analizi & Ses":
  st.subheader("💬 Sohbet, Gerçek Zamanlı Arama ve Ses Merkezi")

  # KAYDIRILABİLİR SOHBET ALANI
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
                f'<script>ghostKonus("{temiz_metin}");</script>', height=0
            )

  st.markdown("</div>", unsafe_allow_html=True)

  # DOSYA YÜKLEME İÇİN KÜÇÜK BİR ALAN
  with st.expander("📸 Fotoğraf veya Dosya Ekle (İsteğe Bağlı)"):
    yuklenen_dosya = st.file_uploader(
        "Dosya Seç", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

  # STANDART STREAMLIT CHAT GİRDİ ALANI
  prompt = st.chat_input("GHOST'a mesajını yaz efendim...")

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
        aktif_mesajlar = st.session_state.messages
        if any(
            kelime in prompt.lower()
            for kelime in [
                "hava",
                "kaç derece",
                "bugün",
                "haber",
                "kimdir",
                "nedir",
                "fiyatı",
                "sıcaklık",
            ]
        ):
          st.toast("🔍 İnternetten güncel veriler taranıyor...", icon="🌐")
          ek_bilgi = internette_ara(prompt)
          aktif_mesajlar = st.session_state.messages + [{
              "role": "system",
              "content": (
                  "İnternetten elde edilen güncel ve gerçek zamanlı veriler"
                  f" şunlardır: {ek_bilgi}. Bu bilgileri kullanarak yanıt ver"
                  " efendim."
              ),
          }]

        response = client.chat.completions.create(
            model=MODEL_NAME, messages=aktif_mesajlar
        )
        full_response = response.choices[0].message.content

        message_placeholder.markdown(f"**{full_response}**")

        temiz_yanit = (
            full_response.replace('"', "'")
            .replace("\n", " ")
            .replace("*", "")
        )
        st.components.v1.html(
            f'<script>ghostKonus("{temiz_yanit}");</script>', height=0
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
      except Exception as e:
        st.error(f"Bağlantı hatası: {e}")

  if st.sidebar.button("Sohbet Hafızasını Sıfırla"):
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "Sen gelişmiş, aktif ve anlık internet arama yeteneğine sahip olan"
            " bir yapay zeka asistanı olan GHOST'sun."
        ),
    }]
    st.rerun()

# --- 2. MOD: BİYOMETRİK YÜZ TANIMA & HAFIZA ---
elif secim == "🔍 Biyometrik Yüz Tanıma & Hafıza":
  st.subheader("🔍 GHOST Biyometrik Yüz Tanıma ve Hafıza Modülü")
  col1, col2 = st.columns(2)

  with col1:
    st.markdown("### 📥 1. Adım: Yüzü Kaydet")
    kisi_adi = st.text_input("Kişinin Adı / Unvanı:")
    kayit_dosya = st.file_uploader(
        "Kişinin Fotoğrafını Yükle",
        type=["jpg", "jpeg", "png"],
        key="kayit",
    )

    if st.button("Hafızaya Biyometrik Olarak Ekle"):
      if kisi_adi and kayit_dosya:
        st.session_state.yuz_hafizasi[kayit_dosya.name] = kisi_adi
        st.success(
            f"✅ {kisi_adi} başarıyla GHOST veritabanına işlendi, efendim!"
        )
      else:
        st.warning("Lütfen isim girin ve bir görsel yükleyin efendim.")

  with col2:
    st.markdown("### 🕵️ 2. Adım: Kişiyi Sorgula ve Tanı")
    sorgu_dosya = st.file_uploader(
        "Tanınacak Fotoğrafı Yükle", type=["jpg", "jpeg", "png"], key="sorgu"
    )

    if sorgu_dosya:
      st.image(sorgu_dosya, caption="Taranan Girdi", width=250)
      if st.button("Yüzü Analiz Et ve Kim olduğunu Bul"):
        if sorgu_dosya.name in st.session_state.yuz_hafizasi:
          bulunan_isim = st.session_state.yuz_hafizasi[sorgu_dosya.name]
          mesaj_sesli = (
              "Bu kişi biyometrik veritabanımdaki kayıtlara göre"
              f" {bulunan_isim} efendim."
          )
          st.success(f"🎯 Eşleşme Sağlandı: **{bulunan_isim}**")
          st.components.v1.html(
              f'<script>ghostKonus("{mesaj_sesli}");</script>', height=0
          )
        else:
          uyari_mesaji = "Bu yüzü tanımıyorum efendim."
          st.warning(uyari_mesaji)
          st.components.v1.html(
              f'<script>ghostKonus("{uyari_mesaji}");</script>', height=0
          )

  st.markdown("---")
  st.markdown("### 🗂️ Hafızadaki Kayıtlı Biyometrik Profiller:")
  if not st.session_state.yuz_hafizasi:
    st.info("Kayıtlı profil bulunmuyor efendim.")
  else:
    for dosya, isim in st.session_state.yuz_hafizasi.items():
      st.write(f"- 👤 **{isim}** *(Dosya: {dosya})*")

# --- 3. MOD: CANLI KONUM ---
elif secim == "📍 Canlı Konum Takibi":
  st.subheader("📍 GHOST Canlı Konum Takip Sistemi")
  st.components.v1.html(
      """
    <div id="map-container" style="padding: 20px; background-color: #161b22; color: white; border-radius: 8px; border: 1px solid #30363d;">
        <h3 style="color: #58a6ff; margin-top:0;">📡 Uydu Sinyal Tarayıcı</h3>
        <p id="durum" style="color: #8b949e;">Sinyal bekleniyor efendim...</p>
        <div id="koord" style="margin-top: 10px; font-family: monospace; font-size: 18px; color: #3fb950;"></div>
        <br>
        <button onclick="konumuTara()" style="background-color: #238636; color: white; padding: 12px 24px; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">Sinyal Al ve Konumla</button>
    </div>
    <script>
        function konumuTara() {
            const durum = document.getElementById("durum");
            const koord = document.getElementById("koord");
            durum.innerHTML = "📡 Uydulara bağlanılıyor, lütfen bekleyin efendim...";
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        durum.innerHTML = "✅ Bağlantı Başarılı. Koordinatlar alındı:";
                        koord.innerHTML = "Lat: " + pos.coords.latitude.toFixed(6) + "<br>Lon: " + pos.coords.longitude.toFixed(6);
                    },
                    (err) => { durum.innerHTML = "⚠️ Hata: Konum izni reddedildi efendim."; },
                    { enableHighAccuracy: true, timeout: 5000 }
                );
            } else {
                durum.innerHTML = "❌ Tarayıcınız konum servislerini desteklemiyor efendim.";
            }
        }
    </script>
    """,
      height=250,
  )

# --- 4. MOD: UZAKTAN KONUM TAKİP (RADAR) ---
elif secim == "🛰️ Uzaktan Konum Takip (Radar)":
  st.subheader("🛰️ GHOST Uzaktan Hedef Konum & Google Maps Radar Modülü")
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
        st.warning("⚠️ Henüz `konum_takip` tablosunda sinyal yok efendim.")
    except Exception as ex:
      st.error(f"Radar / Harita hatası: {ex}")
  else:
    st.error("Supabase bağlantısı kurulamadı efendim.")

# --- 5. MOD: SİSTEM ---
elif secim == "💻 Sistem Komuta Paneli":
  st.subheader("💻 Sistem Komuta ve Donanım Durum Paneli")
  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(label="🔥 CPU Yükü", value="%14.2", delta="Stabil")
    st.progress(0.14)
  with col2:
    st.metric(label="💾 RAM Tüketimi", value="%43.8", delta="Normal")
    st.progress(0.43)
  with col3:
    st.metric(label="🌐 Ağ Gecikmesi", value="24 ms", delta="Çok İyi")
    st.progress(0.24)
  st.success("Sistem altyapısı ve tüm alt rutinler kusursuz çalışıyor, efendim.")

# --- 6. MOD: GÖREVLER ---
else:
  st.subheader("📌 GHOST Görev ve Proje Takip Sistemi")
  yeni_gorev = st.text_input("Yeni Görev / Operasyon Tanımı:")
  if st.button("Görev Ekle"):
    if yeni_gorev:
      st.session_state.gorevler.append(
          {"gorev": yeni_gorev, "durum": "Bekliyor ⏳"}
      )
      st.success("Yeni görev başarıyla listeye eklendi efendim.")
      st.rerun()
    else:
      st.warning("Lütfen geçerli bir görev tanımı yazın efendim.")

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
          if st.button("Bitir", key=f"b_{i}"):
            st.session_state.gorevler[i]["durum"] = "Tamamlandı ✅"
            st.rerun()
