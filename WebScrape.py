import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import os
import urllib.parse
import aiohttp
import re

# Geçersiz karakterleri temizlemeyen fonksiyon
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)  # Geçersiz karakterleri alt çizgiyle değiştirir

# URL'den benzersiz bir dosya ismi oluşturma fonksiyonu
def generate_filename(url):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path if parsed_url.path != '/' else 'index'
    filename = sanitize_filename(path.strip('/'))
    return filename + '.html' if not filename.endswith('.html') else filename

async def fetch_page(url, save_dir):
    browser = await launch()
    page = await browser.newPage()

    await page.goto(url, {'waitUntil': 'networkidle2'}) #!BUG! Too many redirect

    # Sayfa içeriğini çeker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # URL'den dosya adını oluştur
    file_name = generate_filename(url)
    file_path = os.path.join(save_dir, file_name)

    # Sayfa HTML'ini dosyaya kaydeder
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)

    # CSS ve JavaScript dosyalarını bulur ve kaydeder
    for tag_name in ['link', 'script']:
        for tag in soup.find_all(tag_name):
            if tag_name == 'link' and tag.get('rel') == ['stylesheet']:  # CSS dosyaları
                href = tag.get('href')
                if href:
                    full_url = urllib.parse.urljoin(url, href)
                    await save_resource(full_url, save_dir)
            elif tag_name == 'script' and tag.get('src'):  # JS dosyaları
                src = tag.get('src')
                if src:
                    full_url = urllib.parse.urljoin(url, src)
                    await save_resource(full_url, save_dir)

    # Tüm img dosyalarını bul ve kaydet
    for img_tag in soup.find_all('img'):
        src = img_tag.get('src')
        if src:
            full_url = urllib.parse.urljoin(url, src)
            await save_resource(full_url, save_dir)

    await browser.close()

async def fetch_all_links(url, save_dir):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})

    # Sayfa içeriğini çeker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Tüm linkleri bulur ve her birini ziyaret eder
    links = set()
    for a_tag in soup.find_all('a', href=True):  # a=anchor (urls)
        link = urllib.parse.urljoin(url, a_tag['href'])
        if link not in links and urllib.parse.urlparse(link).netloc == urllib.parse.urlparse(url).netloc:  # Netloc = urldomain + port
            links.add(link)
            await fetch_page(link, save_dir)

    await browser.close()

async def save_resource(url, save_dir):
    # Dosya adını temizler
    file_name = sanitize_filename(os.path.basename(urllib.parse.urlsplit(url).path))

    if not file_name:  # Eğer dosya ismi yoksa index.html yap
        file_name = 'index.html'

    file_path = os.path.join(save_dir, file_name)

    # Kaynağı indirip kaydet
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(file_path, 'wb') as file:
                    file.write(await response.read())

# Ana işlev (asenkron görevleri başlatır)
async def main():
    url = 'https://books.toscrape.com/'  #Hedef URL
    save_dir = 'C:/Users/erngu/Desktop/Code/WebAppSecSnDAnalyzeTool/SS'  # Kaydedilecek dosya

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    await fetch_all_links(url, save_dir)

asyncio.get_event_loop().run_until_complete(main())

