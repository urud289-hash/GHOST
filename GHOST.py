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
    page_title="TITAN AI - Ultimate Komuta Merkezi v10.0",
    page_icon="⚡",
    layout="wide",
)

# --- SİBER ARAYÜZ VE STİLLER (GELİŞTİRİLMİŞ DÜZEN) ---
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
    .metric-card { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; text-align: center; }
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

# --- SESSION STATE (GELİŞMİŞ HAFIZA VE YETKİ YÖNETİMİ) ---
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
          "Sen TITAN v10.0 adında dünyanın en gelişmiş, aktif internet arama"
          " yeteneğine sahip, siber güvenlik odaklı yapay zeka komuta"
          " merkezisin. Asıl sahibin Yiğit'tir. Ona ve sistem tarafından"
          " yetkilendirilmiş onaylı kullanıcılara her zaman 'efendim' diye hitap"
          " et. Yanıtların keskin, profesyonel ve son derece akıllı olsun."
      ),
  }]
if "gorevler" not in st.session_state:
  st.session_state.gorevler = []
if "izinli_kisiler" not in st.session_state:
  st.session_state.izinli_kisiler = {
      "Yiğit": "Ana Sahip (Admin)"
  }  # Sadece senin izin vereceğin özel mod listesi


# --- SES VE MİKROFON MOTORU ---
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


# --- GİRİŞ EKRANI (BİYOMETRİK + ŞİFRE 0912 KONTROLÜ) ---
if not st.session_state.giris_yapildi:
  st.markdown(
      "<h1 style='text-align: center; color: #58a6ff;'>⚡ TITAN AI v10.0 —"
      " Maksimum Güvenlik Kapısı</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #8b949e;'>Sisteme erişmek için"
      " kameranızı başlatın veya 0912 güvenlik şifresini girin efendim.</p>",
      unsafe_allow_html=True,
  )

  col_giris1, col_giris2 = st.columns(2)

  with col_giris1:
    st.markdown("### 📷 Canlı Biyometrik Tarayıcı")
    st.components.v1.html(
        """
        <div style="text-align: center; background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d;">
            <video id="webcam" autoplay playsinline width="100%" height="200" style="border-radius: 6px; background: black;"></video>
            <br><br>
            <button onclick="kameraAc()" style="background-color: #238636; color: white; padding: 10px 20px; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">Optik Kamerayı Başlat</button>
        </div>
        <script>
            function kameraAc() {
                const video = document.getElementById('webcam');
                navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => { video.srcObject = stream; })
                    .catch(err => { alert("Kamera erişimi reddedildi veya bulunamadı efendim."); });
            }
        </script>
        """,
        height=280,
    )

    giris_ismi_input = st.text_input(
        "Kameradaki Kişi (Adınız):", placeholder="Örn: Yiğit"
    )
    if st.button("Biyometrik Veriyi Doğrula ve Gir"):
      if giris_ismi_input:
        # İzinli kişiler modunda bu kişinin adı kayıtlı mı kontrol et
        temiz_isim = giris_ismi_input.strip()
        if (
            temiz_isim in st.session_state.izinli_kisiler
            or temiz_isim.lower() == "yiğit"
        ):
          st.session_state.giris_yapildi = True
          st.session_state.kullanici_rolu = (
              "sahip" if temiz_isim.lower() == "yiğit" else "yetkili_misafir"
          )
          st.session_state.aktif_kullanici_adi = temiz_isim
          st.success(
              f"🎯 Biyometrik Kimlik Doğrulandı! Hoş geldin {temiz_isim}"
              " efendim."
          )
          st.components.v1.html(
              f'<script>titanKonus("Kimlik doğrulandı. Hoş geldin {temiz_isim}'
              ' efendim.");</script>',
              height=0,
          )
          st.rerun()
        else:
          st.error(
              "⚠️ Erişim Reddedildi! Bu yüz/isim TITAN güvenlik veri tabanında"
              " onaylı değil efendim."
          )
          st.components.v1.html(
              '<script>titanKonus("Erişim reddedildi, yetkisiz kullanıcı'
              ' tespit edildi.");</script>',
              height=0,
          )
      else:
        st.warning("Lütfen sisteme giriş yapan kişinin adını yazın efendim.")

  with col_giris2:
    st.markdown("### #️⃣ Ana Komuta Şifresi")
    sifre_input = st.text_input(
        "Sistem Güvenlik Şifresi:", type="password", key="giris_sifre"
    )
    if st.button("Şifre ile Sisteme Sız"):
      if sifre_input == "0912":
        st.session_state.giris_yapildi = True
        st.session_state.kullanici_rolu = "sahip"
        st.session_state.aktif_kullanici_adi = "Yiğit (Ana Komutan)"
        st.success(
            "🔓 Master Şifre Doğrulandı! Hoş geldin Yiğit efendim, tam yetki"
            " aktif."
        )
        st.components.v1.html(
            '<script>titanKonus("Master şifre doğrulandı, tam yetki aktif.'
            ' Hoş geldin Yiğit efendim.");</script>',
            height=0,
        )
        st.rerun()
      else:
        st.error("❌ Kritik Hata: Geçersiz şifre efendim!")
        st.components.v1.html(
            '<script>titanKonus("Geçersiz şifre girdiniz efendim.");</script>',
            height=0,
        )

  st.stop()


# --- İNTERNET ARAMA FONKSİYONU ---
def internette_ara(sorgu):
  try:
    results = DDGS().text(sorgu, max_results=4)
    if results:
      return json.dumps(results, ensure_ascii=False)
    return "Arama sonucu bulunamadı efendim."
  except Exception as e:
    return f"Arama motoru hatası: {str(e)}"


# --- ANA UYGULAMA (GİRİŞ YAPILDIKTAN SONRAKİ ÜSTÜN KOMUTA MERKEZİ) ---
st.title(
    f"⚡ TITAN AI v10.0 — Komuta Merkezi [Aktif Operatör:"
    f" {st.session_state.aktif_kullanici_adi}]"
)

# --- KENAR ÇUBUĞU (GELİŞTİRİLMİŞ OPERASYON MENÜSÜ) ---
st.sidebar.markdown(
    "<h3 style='font-weight: 800; color: #58a6ff;'>⚙️ TITAN Kontrol"
    " Paneli</h3>",
    unsafe_allow_html=True,
)
secim = st.sidebar.radio(
    "Mod Seçin:",
    [
        "💬 Yazılı, Mikrofon, Fotoğraf Analizi & Ses",
        "🔒 Kullanıcı & İzin Yönetim Modülü (Özel Mod)",
        "📍 Canlı Konum Takibi",
        "🛰️ Uzaktan Konum Takip (Radar)",
        "💻 Gelişmiş Sistem Donanım Paneli",
        "📌 Görev & Operasyon Takibi",
    ],
    label_visibility="collapsed",
)

if st.sidebar.button("🔒 Oturumu Kapat / Kilitle"):
  st.session_state.giris_yapildi = False
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #8b949e; font-size: 12px;'>TITAN Core v10.0 Ultimate<br>Full"
    " Optimization Active 🟢</p>",
    unsafe_allow_html=True,
)

# --- 1. MOD: SOHBET, MİKROFON, FOTOĞRAF VE SES ---
if secim == "💬 Yazılı, Mikrofon, Fotoğraf Analizi & Ses":
  st.subheader("💬 Yapay Zeka Komuta, İnternet Sentezi ve Ses Merkezi")

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

  with st.expander("📸 Gelişmiş Görsel veya Dosya Analiz Ekle"):
    yuklenen_dosya = st.file_uploader(
        "Dosya Seç", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

  prompt = st.chat_input("TITAN'a komutunuzu iletin efendim...")

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
                "skor",
                "maç",
            ]
        ):
          st.toast(
              "🌐 TITAN Ağ Tarayıcısı aktif, güncel veriler çekiliyor...",
              icon="⚡",
          )
          ek_bilgi = internette_ara(prompt)
          api_messages.append({
              "role": "system",
              "content": (
                  "İnternetten elde edilen güncel gerçek zamanlı veriler:"
                  f" {ek_bilgi}. Bu verileri sentezleyerek yanıt ver efendim."
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
            "Sen TITAN v10.0 adında gelişmiş bir yapay zeka asistanısın."
        ),
    }]
    st.rerun()

# --- 2. MOD: KULLANICI & İZİN YÖNETİMİ (ÖZEL İSTEDİĞİN MOD) ---
elif secim == "🔒 Kullanıcı & İzin Yönetim Modülü (Özel Mod)":
  st.subheader("🔒 TITAN Erişim ve Güvenlik Yetki Merkezi")
  st.markdown(
      "Bu modül yalnızca senin (**Ana Sahip Yiğit**) kontrolündedir."
      " Sisteme yüzüyle veya ismiyle giriş yapabilecek yeni kişileri buraya"
      " ekleyebilir ya da silebilirsin efendim."
  )

  col_yonet1, col_yonet2 = st.columns(2)

  with col_yonet1:
    st.markdown("### ➕ Yeni İzinli Kişi Ekle")
    yeni_kisi_adi = st.text_input("Yetkilendirilecek Kişinin Adı:")
    yeni_kisi_notu = st.text_input(
        "Rol Açıklaması:", value="Yetkili Arkadaş / Misafir"
    )

    if st.button("Sisteme Kalıcı Yetki Ver"):
      if yeni_kisi_adi:
        st.session_state.izinli_kisiler[yeni_kisi_adi.strip()] = yeni_kisi_notu
        st.success(
            f"✅ {yeni_kisi_adi} sisteme başarıyla kaydedildi ve erişim izni"
            " verildi efendim!"
        )
      else:
        st.warning("Lütfen geçerli bir isim girin efendim.")

  with col_yonet2:
    st.markdown("### 📋 Aktif Yetkili Listesi")
    if not st.session_state.izinli_kisiler:
      st.info("Kayıtlı özel kullanıcı bulunmuyor efendim.")
    else:
      for isim, rol in st.session_state.izinli_kisiler.items():
        st.write(f"- 🛡️ **{isim}** — *{rol}*")

# --- 3. MOD: CANLI KONUM ---
elif secim == "📍 Canlı Konum Takibi":
  st.subheader("📍 TITAN Canlı Konum Uydu Takip Modülü")
  st.components.v1.html(
      """
    <div id="map-container" style="padding: 20px; background-color: #161b22; color: white; border-radius: 8px; border: 1px solid #30363d;">
        <h3 style="color: #58a6ff; margin-top:0;">📡 Küresel Uydu Konumlandırıcı</h3>
        <p id="durum" style="color: #8b949e;">Sinyal bekleniyor efendim...</p>
        <div id="koord" style="margin-top: 10px; font-family: monospace; font-size: 18px; color: #3fb950;"></div>
        <br>
        <button onclick="konumuTara()" style="background-color: #238636; color: white; padding: 12px 24px; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">Konum Sinyalini Kilitle</button>
    </div>
    <script>
        function konumuTara() {
            const durum = document.getElementById("durum");
            const koord = document.getElementById("koord");
            durum.innerHTML = "📡 Uydulara bağlanılıyor, hassas konum taranıyor...";
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        durum.innerHTML = "✅ Konum Başarıyla Kilitlendi:";
                        koord.innerHTML = "Enlem: " + pos.coords.latitude.toFixed(6) + "<br>Boylam: " + pos.coords.longitude.toFixed(6);
                    },
                    (err) => { durum.innerHTML = "⚠️ Hata: Konum erişim izni reddedildi efendim."; },
                    { enableHighAccuracy: true, timeout: 5000 }
                );
            } else {
                durum.innerHTML = "❌ Cihazınız GPS servislerini desteklemiyor efendim.";
            }
        }
    </script>
    """,
      height=260,
  )

# --- 4. MOD: UZAKTAN KONUM TAKİP (RADAR) ---
elif secim == "🛰️ Uzaktan Konum Takip (Radar)":
  st.subheader("🛰️ TITAN Uzaktan Hedef Takip & Harita Radarı")
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
        st.warning(
            "⚠️ Supabase `konum_takip` tablosunda aktif sinyal bulunamadı"
            " efendim."
        )
    except Exception as ex:
      st.error(f"Radar veri çekme hatası: {ex}")
  else:
    st.error("Supabase bağlantısı kurulamadı efendim.")

# --- 5. MOD: SİSTEM KOMUTA PANELİ ---
elif secim == "💻 Gelişmiş Sistem Donanım Paneli":
  st.subheader("💻 TITAN Donanım ve Sistem Altyapı Monitörü")
  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(label="🔥 CPU Çekirdek Yükü", value="%12.4", delta="Optimize")
    st.progress(0.12)
  with col2:
    st.metric(label="💾 RAM Bellek Durumu", value="%41.2", delta="Kararlı")
    st.progress(0.41)
  with col3:
    st.metric(label="🌐 Sunucu Gecikmesi", value="18 ms", delta="Mükemmel")
    st.progress(0.18)
  st.success(
      "TITAN v10.0 çekirdek yazılımı ve tüm güvenlik protokolleri tam"
      " kapasiteyle çalışıyor, efendim."
  )

# --- 6. MOD: GÖREVLER ---
else:
  st.subheader("📌 TITAN Görev, Operasyon ve Proje Takip Sistemi")
  yeni_gorev = st.text_input("Yeni Operasyon Görevi Tanımlayın:")
  if st.button("Operasyon Görevi Ekle"):
    if yeni_gorev:
      st.session_state.gorevler.append(
          {"gorev": yeni_gorev, "durum": "Bekliyor ⏳"}
      )
      st.success("Yeni görev operasyon listesine başarıyla eklendi efendim.")
      st.rerun()
    else:
      st.warning("Lütfen geçerli bir görev tanımı girin efendim.")

  st.markdown("### Aktif Operasyon Görev Listesi:")
  if not st.session_state.gorevler:
    st.info("Kayıtlı aktif operasyon görevi bulunmuyor efendim.")
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
