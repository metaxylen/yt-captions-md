# YT Captions MD

YouTube videolarının altyazılarını (captions) tek komutla **Markdown** dosyasına dönüştüren küçük bir CLI aracı.

API anahtarı gerekmez. Altyazılar `youtube-transcript-api` ile, video başlığı ve kanal adı `yt-dlp` ile (yalnızca metadata, video indirilmez) alınır.

## Özellikler

- **Çoklu URL formatı:** `youtube.com/watch`, `youtu.be`, `shorts`, ek query parametreleri (`&t=`, `&list=` …)
- **Altyazı seçimi:** Önce elle yüklenen altyazılar, yoksa otomatik üretilen; `--lang` ile dil önceliği
- **Okunabilir metin:** Parçalar birleştirilir, otomatik altyazıdaki tekrarlar temizlenir
- **Markdown çıktı:** Başlık, URL, kanal, dil ve altyazı tipi üst bilgide
- **Güvenli dosya adı:** Başlıktan türetilir; çakışmada dosya adına video ID eklenir (üzerine yazılmaz)
- **Dayanıklılık:** Geçersiz URL veya altyazı yoksa atlanır; ağ hatalarında 3 denemeye kadar exponential backoff

## Gereksinimler

- Python **3.10+**
- İnternet bağlantısı

## Kurulum

```bash
git clone https://github.com/metaxylen/yt-captions-md.git
cd yt-captions-md

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Kullanım

```bash
# Tek video
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Birden fazla video
python main.py URL1 URL2

# Dosyadan (satır başına bir URL; # ile başlayanlar ve boş satırlar yok sayılır)
python main.py --file urls.txt

# Dil önceliği, paragraf zaman damgası, çıktı klasörü
python main.py --lang tr,en --timestamps --out ./output URL
```

### Seçenekler

| Seçenek | Açıklama |
|--------|----------|
| `--lang tr,en` | Dil kodları (virgülle); önce manuel, sonra otomatik altyazı |
| `--timestamps` | Her paragrafın başına `[mm:ss]` ekle |
| `--out <klasör>` | Çıktı dizini (varsayılan: `output/`) |
| `--file`, `-f` | URL listesi dosyası |

## Örnek çıktı

```markdown
# Video Başlığı

- URL: https://www.youtube.com/watch?v=...
- Channel: Kanal Adı
- Language: tr
- Type: manual

---

Transkript metni burada, paragraflar arasında boş satır olmadan...
```

## Proje yapısı

```
├── main.py                 # CLI giriş noktası
├── youtube_transcript/
│   ├── urls.py             # Video ID çıkarma
│   ├── transcript.py       # Altyazı indirme ve yeniden deneme
│   ├── metadata.py         # Başlık / kanal (yt-dlp)
│   ├── markdown.py         # Birleştirme ve .md biçimi
│   └── files.py            # Dosya adı ve yazma
├── tests/
└── requirements.txt
```

## Testler

```bash
python -m unittest discover -s tests -v
```

## Lisans

[MIT](LICENSE)

## Not

Bu araç yalnızca YouTube’un herkese açık altyazı verisini kullanır. İçeriğin telif ve kullanım koşullarına uygun kullanım sizin sorumluluğunuzdadır.
