import base64
import os
import pandas as pd
from openai import OpenAI
from PIL import Image
import streamlit as st
from supabase import Client, create_client

# Sayfa Yapılandırması (Mobil ve Geniş Ekran Optimizasyonlu)
st.set_page_config(
    page_title="GHOST AI - Ultimate Komuta Merkezi", page_icon="👻", layout="wide"
)

# --- GELİŞMİŞ SİBER ARAYÜZ STİLLERİ VE MOBİL UYUM CSS ---
st.markdown(
    """
<style>
    /* Genel Arka Plan ve Metin Renkleri */
    .stApp { 
        background-color: #0b0f19; 
        color: #f0f6fc; 
    }
    
    /* Kenar Çubuğu (Sidebar) Tasarımı */
    [data-testid="stSidebar"] { 
        background-color: #0d1117; 
        border-right: 1px solid #30363d; 
    }
    
    /* Başlıklar */
    h1, h2, h3 { 
        color: #58a6ff !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    
    /* Tipografi Optimizasyonu (Kalın ve Okunaklı) */
    p, span, label, div, .stMarkdown { 
        font-weight: 600 !important; 
    }
    
    /* Alt Bilgi Gizleme ve Koyu Tema Sabitleme */
    footer { visibility: hidden; }
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
        background-color: #0b0f19 !important;
    }
    
    /* Özel Buton Stilleri (Mobil Uyumlu Genişlik) */
    .stButton>button {
        background: linear-gradient(135deg, #238636, #2ea043);
        color: white; 
        border-radius: 8px; 
        border: 1px solid #3fb950; 
        font-weight: 700; 
        padding: 0.5rem 1rem;
        width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #2ea043, #3fb950);
        box-shadow: 0 6px 8px rgba(35,134,54,0.4);
        border-color: #56d364;
    }
    
    /* Veri Çerçevesi (DataFrame) ve Tablo Çerçeveleri */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363d;
        border-radius: 8px;
        background-color: #161b22;
    }
    
    /* Metin Giriş Kutuları */
    .stTextInput input, .stChatInput input {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    .stTextInput input:focus, .stChatInput input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 5px rgba(88,166,255,0.4);
    }
</style>
""",
    unsafe_allow_html=True,
)

# API Anahtarı ve Güncel Model Tanımı
API_KEY = "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"
client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")
MODEL_NAME = "openai/gpt-oss-120b"

# --- SUPABASE BAĞLANTI MERKEZİ ---
SUPABASE_URL = "https://luzzmraohsaqajinnyhk.supabase.co"
SUPABASE_KEY = "sb_publishable_Z8MQbBctodUb7jiwiEiigw_eYANG9JW"


@st.cache_resource
def init_supabase(url, key):
  try:
    return create_client(url, key)
  except Exception:
    return None


supabase = init_supabase(SUPABASE_URL, SUPABASE_KEY)

# Hafıza ve Durum Yönetimi
if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "system",
      "content": (
          "Sen gelişmiş bir yapay zeka asistanı olan GHOST'sun. Matematik"
          " ödevlerini adım adım çözer, bilgisayar hatalarını ve içerikleri"
          " analiz edip yardımcı olursun. Her zaman 'efendim' diye hitap et."
      ),
  }]
if "gorevler" not in st.session_state:
  st.session_state.gorevler = []
if "yuz_hafizasi" not in st.session_state:
  st.session_state.yuz_hafizasi = {}

# --- GELİŞTİRİLMİŞ SES VE MİKROFON MOTORU ---
st.markdown(
    """
<script>
    function ghostKonus(metin) {
        if (!('speechSynthesis' in window)) {
            alert("Tarayıcınız ses sentezleme özelliğini desteklemiyor efendim.");
            return;
        }
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance(metin);
        msg.lang = 'tr-TR';
        msg.rate = 1.0;
        
        var voices = window.speechSynthesis.getVoices();
        for(var i = 0; i < voices.length; i++) {
            if(voices[i].lang === 'tr-TR' || voices[i].lang === 'tr_TR') {
                msg.voice = voices[i];
                break;
            }
        }
        window.speechSynthesis.speak(msg);
    }

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = function() {
            window.speechSynthesis.getVoices();
        };
    }

    function sesliKomutBaslat() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Tarayıcınız sesli komut özelliğini desteklemiyor efendim.");
            return;
        }

        try {
            var recognition = new SpeechRecognition();
            recognition.lang = 'tr-TR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            
            recognition.onresult = function(event) {
                var sesMetni = event.results[0][0].transcript;
                const inputs = window.parent.document.querySelectorAll('input[type="text"], input');
                let targetInput = null;
                for (let input of inputs) {
                    if (input.placeholder && input.placeholder.includes("GHOST")) {
                        targetInput = input;
                        break;
                    }
                }
                if (!targetInput && inputs.length > 0) {
                    targetInput = inputs[inputs.length - 1];
                }

                if (targetInput) {
                    let setter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
                    setter.call(targetInput, sesMetni);
                    targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                    setTimeout(() => {
                        targetInput.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true}));
                    }, 400);
                }
            };

            recognition.start();
        } catch(e) {
            alert("Mikrofon başlatılamadı: " + e.message);
        }
    }
</script>
""",
    unsafe_allow_html=True,
)

st.title("👻 GHOST AI - Ultimate Komuta ve Takip Merkezi")

# --- KENAR ÇUBUĞU MENÜSÜ ---
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
    "<p style='color: #8b949e; font-size: 12px;'>GHOST Ultimate v5.7<br>Durum:"
    " Çevrimiçi & Güvenli 🟢</p>",
    unsafe_allow_html=True,
)

# --- 1. MOD: SOHBET, MİKROFON, FOTOĞRAF ANALİZİ VE SES ---
if secim == "💬 Yazılı, Mikrofon, Fotoğraf Analizi & Ses":
  st.subheader("💬 Sohbet, Fotoğraf Analizi ve Sesli Yanıt Merkezi")
  st.markdown(
      "<p style='color: #8b949e; font-size: 14px;'>Matematik ödevi, ekran"
      " hatası veya herhangi bir görsel yükleyip GHOST'a analitik çözümler"
      " yaptırabilirsin efendim.</p>",
      unsafe_allow_html=True,
  )

  for i, message in enumerate(st.session_state.messages):
    if message["role"] != "system":
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

  st.markdown("---")

  col_alt1, col_alt2 = st.columns([1, 4])

  with col_alt1:
    if st.button("🎙️ Sesli Konuş"):
      st.components.v1.html(
          "<script>sesliKomutBaslat();</script>", height=0
      )
      st.toast(
          "Dinliyorum efendim, mikrofon izni verdiğinizden emin olun...",
          icon="🎙️",
      )

    yuklenen_dosya = st.file_uploader(
        "📸 Fotoğraf Yükle",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

  with col_alt2:
    prompt = st.chat_input("GHOST'a mesajını yaz efendim...")

  if prompt or yuklenen_dosya:
    user_content = []

    if yuklenen_dosya:
      bytes_data = yuklenen_dosya.getvalue()
      base64_image = base64.b64encode(bytes_data).decode("utf-8")
      image_url = f"data:image/jpeg;base64,{base64_image}"
      user_content.append({"type": "image_url", "image_url": {"url": image_url}})

    if prompt:
      user_content.append({"type": "text", "text": prompt})
    else:
      user_content.append(
          {"type": "text", "text": "Bu görseli analiz edip açıklar mısın?"}
      )

    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("user"):
      if yuklenen_dosya:
        st.image(yuklenen_dosya, width=300)
      if prompt:
        st.markdown(f"**{prompt}**")

    with st.chat_message("assistant"):
      message_placeholder = st.empty()
      try:
        response = client.chat.completions.create(
            model=MODEL_NAME, messages=st.session_state.messages
        )
        full_response = response.choices[0].message.content
        message_placeholder.markdown(f"**{full_response}**")
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
        st.rerun()
      except Exception as e:
        st.error(f"Bağlantı hatası: {e}")

  if st.sidebar.button("Sohbet Hafızasını Sıfırla"):
    st.session_state.messages = [{
        "role": "system",
        "content": "Sen gelişmiş bir yapay zeka asistanı olan GHOST'sun.",
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
                    (err) => {
                        durum.innerHTML = "⚠️ Hata: Konum izni reddedildi efendim.";
                    },
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

# --- 4. MOD: UZAKTAN KONUM TAKİP (RADAR, SUPABASE & GOOGLE MAPS) ---
elif secim == "🛰️ Uzaktan Konum Takip (Radar)":
  st.subheader(
      "🛰️ GHOST Uzaktan Hedef Konum, Sokak & Google Maps Radar Modülü"
  )
  st.markdown(
      "<p style='color: #8b949e; font-size: 14px;'>Supabase'den gelen"
      " koordinatlar artık Google Maps altyapısıyla haritalandırılıyor ve"
      " sokak/bina bilgileri çözümleniyor efendim.</p>",
      unsafe_allow_html=True,
  )

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

        st.markdown(
            "### 🗺️ Google Maps Entegreli Canlı Hedef Nokta Gösterimi:"
        )

        # En son gelen konumu baz alalım
        son_konum = data[0]
        if "latitude" in son_konum and "longitude" in son_konum:
          lat = son_konum["latitude"]
          lon = son_konum["longitude"]

          st.info(
              f"🎯 Son Hedef Koordinatları -> Enlem: `{lat}` | Boylam: `{lon}`"
          )

          # Google Maps Embed (Interaktif Sokak ve Bina Görünümü)
          maps_html = f"""
                    <iframe
                        width="100%"
                        height="400"
                        style="border:1px solid #30363d; border-radius: 8px;"
                        loading="lazy"
                        allowfullscreen
                        src="https://maps.google.com/maps?q={lat},{lon}&z=16&output=embed">
                    </iframe>
                    """
          st.components.v1.html(maps_html, height=420)
        else:
          st.warning(
              "Tabloda `latitude` ve `longitude` sütunları bulunamadı efendim."
          )

      else:
        st.warning(
            "⚠️ Henüz `konum_takip` tablosuna düşmüş bir sinyal bulunmuyor"
            " efendim."
        )
    except Exception as ex:
      st.error(f"Radar / Harita bağlantı hatası: {ex}")
  else:
    st.error(
        "Supabase bağlantısı kurulamadı efendim. API anahtarlarını kontrol edin."
    )

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
  st.success(
      "Sistem altyapısı ve tüm alt rutinler kusursuz çalışıyor, efendim."
  )

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
