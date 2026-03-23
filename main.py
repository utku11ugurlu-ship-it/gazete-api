from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI(
    title="Gazete Hacettepe DCMI API",
    description="Gazete Hacettepe haberlerinin Dublin Core (DCMI) üst veri şemasına uygun API servisi."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/haberler")
def haberleri_getir():
    url = "https://gazete.hacettepe.edu.tr/tr/haberler/oduller-4"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    
    haberler_listesi = []
    makaleler = soup.find_all("div", class_="haber2")
    
    for makale in makaleler:
        try:
            baslik_div = makale.find("div", class_="haber2_baslik")
            baslik = "Başlık Yok"
            link = ""
            
            if baslik_div and baslik_div.find("a"):
                a_etiketi = baslik_div.find("a")
                baslik = a_etiketi.text.strip()
                link = a_etiketi["href"]
                if not link.startswith("http"):
                    link = f"https://gazete.hacettepe.edu.tr{link}"
            
            bilgi_div = makale.find("div", class_="haber_yazan")
            yazar, tarih = "Belirtilmemiş", "Tarih Yok"
            
            if bilgi_div:
                bilgi_metni = bilgi_div.text.strip()
                if "/" in bilgi_metni:
                    parcalar = bilgi_metni.split("/")
                    yazar = parcalar[0].strip()
                    tarih = parcalar[1].strip()
                else:
                    yazar = bilgi_metni

            ozet_div = makale.find("div", class_="haber2_ozet")
            ozet = ozet_div.text.strip() if ozet_div else "Özet bulunamadı."
            
            gorsel_div = makale.find("div", class_="haber2_resim")
            gorsel = None
            if gorsel_div and "style" in gorsel_div.attrs:
                style_metni = gorsel_div["style"]
                try:
                    url_kismi = style_metni.split("url(")[1].split(")")[0]
                    gorsel = url_kismi.replace("'", "").replace('"', "")
                    if not gorsel.startswith("http"):
                        gorsel = f"https://gazete.hacettepe.edu.tr{gorsel}"
                except:
                    pass
            
            haberler_listesi.append({
                "dc:title": baslik,
                "dc:creator": yazar,
                "dc:date": tarih,
                "dc:description": ozet,
                "dc:identifier": link,
                "dc:publisher": "Gazete Hacettepe",
                "dc:language": "tr",
                "dc:type": "Text",
                "image_url": gorsel
            })
            
        except Exception as e:
            continue

    return {
        "dataset_info": {
            "dc:title": "Gazete Hacettepe Haberleri",
            "total_records": len(haberler_listesi)
        },
        "records": haberler_listesi
    }