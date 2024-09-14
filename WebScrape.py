import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import os
import urllib.parse
import aiohttp

async def fetch_page(url, save_dir):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    await page.waitFor(500)  # Sayfan�n y�klenmesi i�in 0,5sn delay

    # Sayfa i�eri�ini �eker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Sayfa HTML'ini dosyaya kaydeder
    file_path = os.path.join(save_dir, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)

    # CSS ve JavaScript dosyalar�n� bul ve kaydet
    for tag_name in ['link', 'script']:
        for tag in soup.find_all(tag_name):
            if tag_name == 'link' and tag.get('rel') == 'stylesheet': # Link etiketleri i�in rel �zelli�i stylesheet olanlar se�ilir yani CSS dosyalar�
                href = tag.get('href') #href CSS dosyas�n�n URL'i
                if href:
                    full_url = urllib.parse.urljoin(url, href) # URL ve hrefi birle�tirerek tam url olu�turduk
                    await save_resource(full_url, save_dir)
            elif tag_name == 'script' and tag.get('src'): # script etiketine sahip olan ve src �zelli�i bulunan etiketleri kontrol ettik yani JS dosyalar�n�
                src = tag.get('src')
                if src: # if src not null
                    full_url = urllib.parse.urljoin(url, src) # js dosyalar�n�n full url'i
                    await save_resource(full_url, save_dir)

    await browser.close()


async def fetch_all_links(url, save_dir):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    await page.waitFor(500)

    # Sayfa i�eri�ini �eker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Sayfa HTML'ini dosyaya kaydeder
    file_path = os.path.join(save_dir, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)

    # T�m linkleri bulur ve her birini ziyaret eeder
    links = set()
    for a_tag in soup.find_all('a', href=True):
        link = urllib.parse.urljoin(url, a_tag['href'])
        if link not in links:
            links.add(link)
            await fetch_page(link, save_dir)

    await browser.close()




async def save_resource(url, save_dir):


    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            file_name = os.path.basename(url)
            file_path = os.path.join(save_dir, file_name)
            with open(file_path, 'wb') as file: #hata var bak!
                file.write(await response.read())
                s
# Kay�t dizini
save_dir = 'C:/Users/erngu/Desktop/Code/WebAppSecSnDAnalyzeTool/SS'
os.makedirs(save_dir, exist_ok=True)

#asyncio.get_event_loop().run_until_complete(fetch_all_links("https://books.toscrape.com/", save_dir)) #�al��m�yor??

asyncio.get_event_loop().run_until_complete(fetch_page("https://crawler-test.com/", save_dir))
#asyncio.get_event_loop().run_until_complete(fetch_page("https://httpbin.org/", save_dir)) #burada cssleri �ekmiyor??

