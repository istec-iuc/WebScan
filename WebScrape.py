import asyncio
from asyncio.windows_events import NULL
from operator import index
from pyppeteer import launch
from bs4 import BeautifulSoup
import os
import urllib.parse
import aiohttp
import re
from pathlib import Path
import json
import xmltodict
from semgrep_analyze import SemgrepAnalyzer
from nmap_scanner import NmapScan
from zap_scanner import ZapScan
from SQLmap import SQLScan
from json_parser import ZAPReportParser

# Her alt sayfayı ziyaret eden fonksiyon
async def fetch_all_links(url, save_dir):
    browser = await launch()
    page = await browser.newPage()

    await page.goto(url, {"waitUntil": "networkidle2"})
    
    # Ana sayfa içeriğini çeker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Tüm linkleri bulur ve her birini ziyaret eder
    links = set()
    for a_tag in soup.find_all("a", href=True):
        link = urllib.parse.urljoin(url, a_tag["href"])
        if link not in links and urllib.parse.urlparse(link).netloc == urllib.parse.urlparse(url).netloc:
            links.add(link)
            await fetch_page(page, link, save_dir)

    await browser.close()
    
async def fetch_page(page, url, save_dir):
    # Sayfaya git
    await page.goto(url, {"waitUntil": "networkidle2"})
    
    # Sayfa içeriğini çeker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    
    # URL'den dosya adını ve dizin yolunu oluştur
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path.strip("/")
    print(f"PAth: {path}")
    
    # Eğer path boşsa, 'index' dizini oluştur, boş olmayan path için klasörler oluştur
    if not path:
        path = 'index'
    

    # Ana dizin yapısı: Kayıt dizini + temizlenmiş yol
    dir_path = os.path.join(save_dir, path, f"main")
    dir_path = convert_path_separators(dir_path)
    print(f"dir path: {dir_path}")

    # Dosya adını oluştur
    file_name = generate_filename(os.path.basename(path), parsed_url, dir_path) if path else "index"
    file_path = os.path.join(dir_path, file_name)

    file_path = convert_path_separators(file_path)
    print(f"file_path: {file_path}")

    # Ana dizini oluştur (dizin yapısını oluştur)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        print(f"Dizin olusturuldu: {dir_path}")
 
    # Bütün kaynak dosyalarını kaydeder
    await download_all_resources(soup, url, dir_path)
    
    # Sayfa HTML'ini dosyaya kaydeder
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html)
        print(f"Dosya yazildi: {file_path}")
    

# Bütün source dosyalarını kaydeden fonksiyon
async def download_all_resources(soup, url, dir_path):
    resource_attrs = ['src', 'href', 'data']

    for tag in soup.find_all(True):
        for attr in resource_attrs:
            resource_url = tag.get(attr)
            if resource_url:
                full_url = urllib.parse.urljoin(url, resource_url)
                await save_resource(full_url, dir_path)
                
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
        file_name = f"_{query_string}" if query_string else 'default_filename'

    # Tam dosya yolunu oluştur
    full_path = os.path.join(save_dir, file_name)
    full_path = convert_path_separators(full_path)
    
    # Dosyanın bulunduğu dizini oluştur
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    except PermissionError as e:
        print(f"Permission error creating directory: {e}")
        return

    # Kaynağı indirip kaydet
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(full_path, "wb") as file:
                        file.write(await response.read())
                else:
                    print(f"Error {response.status}: {url}")
    except PermissionError as e:
        print(f"Permission error saving file: {e}")
    except Exception as e:
        print(f"Failed to save {url}: {e}")

def convert_path_separators(path):
    path = Path(path)
    normalized_path = path.as_posix()
    return normalized_path

# Geçersiz karakterleri temizleyen fonksiyon
def sanitize_filename(filename):
    return re.sub(r'[<>:"\\|?*]', '_', filename) # Geçersiz karakterleri alt çizgiyle değiştirir

# URL"den benzersiz HTML bir dosya ismi oluşturma fonksiyonu
def generate_filename(path, parsed_url, dir_path):
    #filename = sanitize_filename(path) # Geçersiz karakterleri temizle

    # HTML uzantısını kontrol et
    if not path.endswith(".html"):
        path += ".html"

    # Dosya adı çakışmasını önlemek için sonuna numara ekle
    original_filename = path
    counter = 1

    # Aynı isimde dosya varsa, adın sonuna numara ekle
    while os.path.exists(os.path.join(dir_path, path)):
        path = f"{original_filename}-{counter}"
        counter += 1

    return path

# JSON dosyasını okunaklı hale getiren fonksiyon
def pretty_json(scan_file):
    with open(scan_file, "r") as json_file:
        data = json.load(json_file)  # JSON içeriğini yükle
        

        # JSON dosyasını düzenli bir formatta geri yaz
    with open(scan_file, "w") as json_file:
        json.dump(data, json_file, indent=4)  # Düzgün format ile kaydet
        
def xml_to_json(xmlfile, jsonfile):
    with open(xmlfile, "r") as file:
        xml_content = file.read()
        
    # Converts XML to dictionary
    dict_data = xmltodict.parse(xml_content)
    
    # Converts dictionary to JSON
    json_data = json.dumps(dict_data, indent=4)

    # Saves JSON data to a file
    with open(jsonfile, "w") as json_file:
        json_file.write(json_data)
        
def create_report(source_file, destination_file, Header):
    try:
        # Open the source file and read its content
        with open(source_file, "r", encoding="utf-8", errors="replace") as src:
            content = src.read()

        # Open the destination file and write the content
        with open(destination_file, "a", encoding="utf-8", errors="replace") as dest:
            dest.write(f"{Header}")
            dest.write(content + "/n/n")

        print("Report successfully created!")
    except Exception as e:
        print(f"An error occurred: {e}")

# Ana işlev (asenkron görevleri başlatır)
async def main():
    # ---Fetch---
    # url = "http://www.scrapethissite.com/pages/" # Hedef URL
    # save_dir = "C:/Users/erngu/source/repos/WebScan/ScrapedFiles" # Source dosyaları bu klasöre kaydedilir
    
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)

    # await fetch_all_links(url, save_dir)
    # ---Fetch---

    # ---Semgrep---
    # directory="/mnt/c/Users/erngu/source/repos/WebScan/ScrapedFiles" # Semgreple scanlenecek dosya 
    # semgrep_config="" # Semgrep ayarları için kullanılacak dosya (Boş bırakırsan default configi kullanır)
    # output_file="/mnt/c/Users/erngu/source/repos/WebScan/SemgrepOutput/results.txt" # Semgrep scan sonucu
    # analyzer = SemgrepAnalyzer(directory, output_file)
    # analyzer.analyze()
    # scan_file="C:/Users/erngu/source/repos/WebScan/SemgrepOutput/results.json" # pretty_json fonksiyonu için dosya konumu
    # pretty_json(scan_file) # JSON dosyasını daha okunaklı hale getirir
    # Semgrep report
    source = "C:/Users/erngu/source/repos/WebScan/SemgrepOutput/results.txt"
    destination = "C:/Users/erngu/source/repos/WebScan/Report/report.txt"
    header = "---SEMGREP---" # Header for report
    create_report(source, destination, header)
    # ---Semgrep---

    # ---Nmap---
    # output_file = "C:/Users/erngu/source/repos/WebScan/NmapOutput/nmap_results.xml"  
    # nmap_target = "scanme.nmap.org"
    # nmap_analyzer = NmapScan(output_file, nmap_target)
    # nmap_analyzer.basic_scan()
    # xml_file = "C:/Users/erngu/source/repos/WebScan/NmapOutput/nmap_results.xml"
    # json_output = "C:/Users/erngu/source/repos/WebScan/NmapOutput/nmap_results.json"
    # xml_to_json(xml_file, json_output)
    # ---Nmap---

    # ---ZAP---
    # zap_dir = "C:/Program Files/ZAP/Zed Attack Proxy"
    # zap_target = "http://testphp.vulnweb.com/"
    # zap_output = "C:/Users/erngu/source/repos/WebScan/ZapOutput/zap_results.json"
    # zap_analyze = ZapScan(zap_target, zap_output, zap_dir)
    # zap_analyze.quick_scan()
    
    # Zap report file creation
    json_file_path = "C:/Users/erngu/source/repos/WebScan/ZapOutput/zap_results.json"

    # Read the JSON file
    with open(json_file_path, "r") as file:
        json_data = json.load(file)
     
    output_file_path = "C:/Users/erngu/source/repos/WebScan/ZapOutput/zap_report.txt" # Zap report file dir
    parser = ZAPReportParser(json_data)
    report = parser.parse_report()
    parser.print_report(report) # Prints report to the cmd
    parser.save_report_to_file(report, output_file_path) # Saves zap report as txt file

    # Saving zap report to the main report file
    source = "C:/Users/erngu/source/repos/WebScan/ZapOutput/zap_report.txt"
    destination = "C:/Users/erngu/source/repos/WebScan/Report/report.txt"
    header = "\n---ZAP---\n"
    create_report(source, destination, header)
    # ---ZAP---

    # ---SQLMAP---
    # sql_target = "http://testphp.vulnweb.com/artists.php?artist=1" 
    # sql_output_dir = "C:/Users/erngu/source/repos/WebScan/SqlOutput"
    # sql_dir = "C:/Users/erngu/AppData/Local/Programs/sqlmap/"
    # SQLmap = SQLScan(sql_target, sql_output_dir, sql_dir)
    # SQLmap.quick_sqlmap()
    # sql_xml = "C:/Users/erngu/source/repos/WebScan/SqlOutput/sql_results.xml"
    # sql_json = "C:/Users/erngu/source/repos/WebScan/SqlOutput/sql_results.json"
    # xml_to_json(sql_xml, sql_json)
    # ---SQLMAP---

    # ---JSON Parser---
    # Zap report file creation
    # json_file_path = "C:/Users/erngu/source/repos/WebScan/ZapOutput/zap_results.json"

    # # Read the JSON file
    # with open(json_file_path, "r") as file:
    #     json_data = json.load(file)
     
    # output_file_path = "C:/Users/erngu/source/repos/WebScan/ZapOutput/zap_report.txt" # Zap report file dir
    # parser = ZAPReportParser(json_data)
    # report = parser.parse_report()
    # parser.print_report(report) # Prints report to the cmd
    # parser.save_report_to_file(report, output_file_path) # Saves zap report as txt file
    # ---JSON Parser---
    
    # ---Report---
    # source = "C:/Users/erngu/source/repos/WebScan/SemgrepOutput/results.txt"
    # destination = "C:/Users/erngu/source/repos/WebScan/Report/report.txt"
    # header = "---SEMGREP---"
    # create_report(source, destination, header)
    # ---Report---
    
asyncio.get_event_loop().run_until_complete(main())
