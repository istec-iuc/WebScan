import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import os
import urllib.parse
import aiohttp
import re

# Geçersiz karakterleri temizleyen fonksiyon
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)  # Geçersiz karakterleri alt çizgiyle değiştirir

# URL"den benzersiz HTML bir dosya ismi oluşturma fonksiyonu
def generate_filename(url, save_dir):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path.strip("/")  # Path"teki ön ve son "/" işaretlerini temizle
    filename = sanitize_filename(path)  # Geçersiz karakterleri temizle

    # Eğer dosya ismi boşsa, URL"nin netloc ve query kısımlarını kullanarak dosya ismi oluştur
    if not filename:
        filename = sanitize_filename(parsed_url.netloc + "_" + parsed_url.query)

    # HTML uzantısını kontrol et
    if not filename.endswith(".html"):
        filename += ".html"

    # Dosya adı çakışmasını önlemek için sonuna numara ekle
    original_filename = filename
    counter = 1

    # Aynı isimde dosya varsa, adın sonuna numara ekle
    while os.path.exists(os.path.join(save_dir, filename)):
        filename = f"{original_filename}-{counter}"
        counter += 1

    return filename
    

async def fetch_page(page, url, base_save_dir):
    # Sayfaya git
    await page.goto(url, {"waitUntil": "networkidle2"})
    
    # Sayfa içeriğini çeker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    
    # URL"den dosya adını ve dizin yolunu oluştur
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path.strip("/")
    dir_path = os.path.join(base_save_dir, path)
    
    # Ana dizini oluştur
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    # Dosya adını oluştur
    file_name = generate_filename(url, dir_path) if path else "index.html" 
    file_path = os.path.join(dir_path, file_name)
    
    # Sayfa HTML"ini dosyaya kaydeder
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html)


    # CSS ve JS dosyalarını bulur ve kaydeder
    for tag_name in ["link", "script"]:
        for tag in soup.find_all(tag_name):
            if tag_name == "link" and tag.get("rel") == ["stylesheet"]:  # CSS dosyaları
                href = tag.get("href")  
                if href:
                    full_url = urllib.parse.urljoin(url, href)
                    await save_resource(full_url, dir_path)
            elif tag_name == "script" and tag.get("src"):  # JS dosyaları
                src = tag.get("src")
                if src:
                    full_url = urllib.parse.urljoin(url, src)
                    await save_resource(full_url, dir_path)
                    
    # IMG dosyalarını bul ve kaydet
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if src:
            full_url = urllib.parse.urljoin(url, src)
            await save_resource(full_url, dir_path)

# Her alt sayfayı ziyaret eden fonksiyon
async def fetch_all_links(url, save_dir):
    browser = await launch()
    page = await browser.newPage() 
    
    await page.goto(url, {"waitUntil": "networkidle2"})  
    
    # Sayfa içeriğini çeker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    
    # Ana sayfayı kaydet
    await fetch_page(page, url, save_dir)
    
    # Tüm linkleri bulur ve her birini ziyaret eder
    links = set()
    for a_tag in soup.find_all("a", href=True):  # a=anchor (url)
        link = urllib.parse.urljoin(url, a_tag["href"])
        if link not in links and urllib.parse.urlparse(link).netloc == urllib.parse.urlparse(url).netloc:  # Netloc = urldomain + port
            links.add(link)  
            await fetch_page(page, link, save_dir)  # Alt sayfaları kaydeder
            
    await browser.close()  # Tarayıcıyı kapat

# Kayıt dizini ve dosya isimlerini oluşturan ve kaydeden fonksiyon
async def save_resource(url, save_dir):
    # URL"yi ayrıştır
    parsed_url = urllib.parse.urlsplit(url)
    path = parsed_url.path.strip("/")
    query = parsed_url.query
    
    # Dosya adını oluştur ve geçersiz karakterleri temizle
    file_name = sanitize_filename(os.path.basename(path))
    
    # Eğer dosya adı yoksa, URL"nin query kısmını dosya adı olarak kullan
    if not file_name:
        query_string = sanitize_filename(query)
        file_name += f"_{query_string}"
    
    
    # Tam dosya yolunu oluştur
    full_path = os.path.join(save_dir, file_name)
    
    # Dosyanın bulunduğu dizini oluştur
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Kaynağı indirip kaydet
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(full_path, "wb") as file:
                    file.write(await response.read())


# Ana işlev (asenkron görevleri başlatır)
async def main():
    url = "http://www.scrapethissite.com/pages/"  # Hedef URL
    save_dir = "C:/Users/erngu/Desktop/Code/WebAppSecSnDAnalyzeTool/SS"  # Kaydedilecek dosya

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    await fetch_all_links(url, save_dir)

asyncio.get_event_loop().run_until_complete(main())


