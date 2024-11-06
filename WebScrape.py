import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
import subprocess
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
from json_parser import JSONParser, ZAPParser, SemgrepParser

# Her alt sayfayı ziyaret eden fonksiyon
async def fetch_all_links(url, save_dir):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle")
        
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
    await page.goto(url, wait_until="networkidle")
    
    # Sayfa içeriğini çeker
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    
    # URL'den dosya adını ve dizin yolunu oluştur
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path.strip("/")
    print(f"Path: {path}")
    
    # Eğer path boşsa, 'index' dizini oluştur, boş olmayan path için klasörler oluştur
    if not path:
        path = 'index'
    
    # Ana dizin yapısı: Kayıt dizini + temizlenmiş yol
    dir_path = os.path.join(save_dir, path, "main")
    dir_path = convert_path_separators(dir_path)
    print(f"dir path: {dir_path}")

    # Dosya adını oluştur
    file_name = generate_filename(os.path.basename(path), parsed_url, dir_path) if path else "index.html"
    file_path = os.path.join(dir_path, file_name)
    file_path = convert_path_separators(file_path)
    print(f"file_path: {file_path}")

    # Ana dizini oluştur (dizin yapısını oluştur)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        print(f"Dizin oluşturuldu: {dir_path}")
 
    # Bütün kaynak dosyalarını kaydeder
    await download_all_resources(soup, url, dir_path)
    
    # Sayfa HTML'ini dosyaya kaydeder
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html)
        print(f"Dosya yazıldı: {file_path}")
    

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
    # Read the raw JSON file
    with open(scan_file, "r", encoding="utf-8") as json_file:
        raw_data = json_file.read()

    # Replace the problematic character
    raw_data = raw_data.replace("\\u2019", "'")

    # Parse the modified string back into JSON
    data = json.loads(raw_data)

    with open(scan_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)

    return data
 

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
        
def create_report(source_file, destination_file, Header, MainHeader=None, Description=None):
    try:
        # Open the source file and read its content
        with open(source_file, "r", encoding="utf-8", errors="replace") as src:
            content = src.read()

        # Checks if the destination file is empty
        is_empty = True
        try:
            with open(destination_file, "r", encoding="utf-8", errors="replace") as dest:
                is_empty = dest.readable() and dest.read().strip() == ""
        except FileNotFoundError:
            is_empty = True  # File does not exist, so it's empty

        # Open the destination file and write the content
        with open(destination_file, "a", encoding="utf-8", errors="replace") as dest:
            if is_empty and MainHeader is not None and Description is not None:
                dest.write(f"**{MainHeader}**\n\n")
                dest.write(f"*{Description}*\n\n")
            dest.write(f"{Header}\n")
            dest.write(content + "\n\n")

        print("Report successfully created!")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_default_tex_report(tex_report_dir):

        tex_report_path = tex_report_dir

        default_tex_content = r"""
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{float}
\usepackage{placeins}
\usepackage{hyperref}
\usepackage{longtable}
\geometry{margin=1in}


\title{\textbf{Static and Dynamic Analysis}}
\author{ISTEC-Cyber Security}
\date{\today} % Automatically insert today's date

\begin{document}

\maketitle

\section*{Description}
This report contains static and dynamic analysis of the target. It uses Semgrep for static analysis and OWASP ZAP, Nmap, and SQLMap for dynamic analysis.

\vspace{10cm} % Space to push the footer down

\begin{center}
\textbf{Provided by} \\[1em]
\includegraphics[width=0.1\textwidth]{logo75.png}
\end{center}

\newpage % Page break

\section{Static Analysis}
Details about static analysis...

\section{Analysis Report}

\subsection{Risk Summary}
\begin{table}[h!]
\centering
\renewcommand{\arraystretch}{1.5}
\begin{tabular}{|c|c|}
\hline
\textbf{Risk Level} & \textbf{Number of Findings} \\
\hline
Low Risk & lowcount \\ 
\hline
Medium Risk & mediumcount \\ 
\hline
High Risk & highcount \\ 
\hline
Critical Risk & criticalcount \\ 
\hline
\end{tabular}
\caption{Summary of Risk Findings}
\label{tab:risk_summary}
\end{table}

\subsection{Vulnerability Categories}
\begin{itemize}
\item Categories:
% Insert vulnerability categories here
\end{itemize}

\subsection{Vulnerabilities by Page}
%Vulnerabilities by Page:

%--------------------------------------------------------Dynamic Analysis-----------------------------------------------
\newpage
\section{Dynamic Analysis}
Details about dynamic analysis...

\section{Analysis Report}

\subsection{Risk Summary}
\begin{table}[h!]
\centering
\renewcommand{\arraystretch}{1.5}
\begin{tabular}{|c|c|}
\hline
\textbf{Risk Level} & \textbf{Number of Findings} \\
\hline
Low Risk & zaplc \\ 
\hline
Medium Risk & zapmc \\ 
\hline
High Risk & zaphc \\ 
\hline
Critical Risk & zapcc \\ 
\hline
\end{tabular}
\caption{Summary of Risk Findings}
\label{tab:risk_summary}
\end{table}

\subsection{Vulnerability Categories}
\begin{itemize}
\item ZapCategories:
% Insert vulnerability categories here
\end{itemize}

\subsection{Vulnerabilities by Page}
%ZapVulnerabilities by Page:
\end{document}
"""        
        
        with open(tex_report_path, "w") as tex_file:
            tex_file.write(default_tex_content)

        print(f"Default Tex report created at: {tex_report_path}")
    

# Ana işlev (asenkron görevleri başlatır)
async def main():
    # ---Fetch---
    url = "http://www.scrapethissite.com/pages/" # Hedef URL
    save_dir = "C:/Users/Administrator/source/repos/WebScan/ScrapedFiles" # Source dosyaları bu klasöre kaydedilir
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # await fetch_all_links(url, save_dir)
    # ---Fetch---

    # ---Semgrep---
    # directory="/mnt/c/Users/Administrator/source/repos/WebScan/ScrapedFiles" # Semgreple scanlenecek dosya 
    # semgrep_config="" # Semgrep ayarları için kullanılacak dosya (Boş bırakırsan default configi kullanır)
    # output_file="/mnt/c/Users/Administrator/source/repos/WebScan/SemgrepOutput/results.json" # Semgrep scan sonucu
    # analyzer = SemgrepAnalyzer(directory, output_file)
    # analyzer.analyze()
    # scan_file="C:/Users/Administrator/source/repos/WebScan/SemgrepOutput/results.json" # pretty_json fonksiyonu için dosya konumu
    #pretty_json(scan_file) # JSON dosyasını daha okunaklı hale getirir

    # Semgrep TEX report
    # Default TEX report


    with open("C:/Users/Administrator/source/repos/WebScan/SemgrepOutput/results.json", "r") as json_file:
        json_data = json.load(json_file)
    parser = SemgrepParser(json_data)
    parsed_report = parser.parse_report()
    impact_count = parser.risk_counter(parsed_report)
    latex_file_path = "C:/Users/Administrator/source/repos/WebScan/LatexReport.tex"
    create_default_tex_report(latex_file_path)
    parser.update_latex_with_risks(impact_count, latex_file_path)
    parser.update_latex_with_category(parsed_report, latex_file_path)
    parser.update_vuln_by_page(parsed_report, latex_file_path)
    print(f"Semgrep report processed, Latex file updated")

    # ---Semgrep---

    # ---Nmap---
    # output_file = "C:/Users/Administrator/source/repos/WebScan/NmapOutput/nmap_results.xml"  
    # nmap_target = "scanme.nmap.org"
    # nmap_analyzer = NmapScan(output_file, nmap_target)
    # nmap_analyzer.basic_scan()
    # xml_file = "C:/Users/Administrator/source/repos/WebScan/NmapOutput/nmap_results.xml"
    # json_output = "C:/Users/Administrator/source/repos/WebScan/NmapOutput/nmap_results.json"
    # xml_to_json(xml_file, json_output)
    # Nmap Report Creation
    # source = "C:/Users/Administrator/source/repos/WebScan/NmapOutput/nmap_results.xml"
    # destination = "C:/Users/Administrator/source/repos/WebScan/Report/report.txt"
    # header = "\n---Nmap---\n"
    # create_report(source, destination, header)
    # ---Nmap---

    # ---ZAP---
    # zap_dir = "C:/Program Files/ZAP/Zed Attack Proxy"
    # zap_target = "http://testphp.vulnweb.com/"
    # zap_output = "C:/Users/Administrator/source/repos/WebScan/ZapOutput/zap_results.json"
    # zap_analyze = ZapScan(zap_target, zap_output, zap_dir)
    # zap_analyze.quick_scan()
    
    # Zap report file creation
    # json_file_path = "C:/Users/Administrator/source/repos/WebScan/ZapOutput/zap_results.json"

    # Read the JSON file
    # with open(json_file_path, "r") as file:
    #     json_data = json.load(file)
     
    # Formats the JSON file
    # output_file_path = "C:/Users/Administrator/source/repos/WebScan/ZapOutput/zap_report.txt" # Zap report file dir
    # parser = ZAPParser(json_data)
    # report = parser.parse_report()
    # parser.print_report(report) # Prints report to the cmd
    # parser.save_report_to_file(report, output_file_path) # Saves zap report as txt file

    # Saving zap report to the main report file
    # source = "C:/Users/Administrator/source/repos/WebScan/ZapOutput/zap_report.txt"
    # destination = "C:/Users/Administrator/source/repos/WebScan/Report/report.txt"
    # header = "\n---ZAP---\n"
    # create_report(source, destination, header)

    # ---ZAP TEX Report---
    with open("C:/Users/Administrator/source/repos/WebScan/ZapOutput/zap_results.json", "r") as json_file:
        zap_json_data = json.load(json_file)

    zapparser = ZAPParser(zap_json_data)
    zap_parsed_report = zapparser.parse_zap_report(zap_json_data)
    latex_file_path = "C:/Users/Administrator/source/repos/WebScan/LatexReport.tex"
    zapparser.update_tex_report(zap_parsed_report, latex_file_path)
    # ---ZAP TEX Report---

    # ---ZAP---

    # ---SQLMAP---
    # sql_target = "http://testphp.vulnweb.com/artists.php?artist=1" 
    # sql_output_dir = "C:/Users/Administrator/source/repos/WebScan/SqlOutput"
    # sql_dir = "C:/Users/Administrator/Programs/sqlmap-dev/"
    # SQLmap = SQLScan(sql_target, sql_output_dir, sql_dir)
    # SQLmap.quick_sqlmap()
    # sql_xml = "C:/Users/Administrator/source/repos/WebScan/SqlOutput/sql_results.xml"  # Don't need this part 
    # sql_json = "C:/Users/Administrator/source/repos/WebScan/SqlOutput/sql_results.json" # Don't need this part
    # xml_to_json(sql_xml, sql_json) # Don't need this part
    # Report Creation
    # source = "C:/Users/Administrator/source/repos/WebScan/SqlOutput/testphp.vulnweb.com/log"
    # destination = "C:/Users/Administrator/source/repos/WebScan/Report/report.txt"
    # header = "\n---SQLMAP---\n"
    # create_report(source, destination, header)
    # ---SQLMAP---

    # ---JSON Parser---
    # Zap report file creation
    # json_file_path = "C:/Users/Administrator/source/repos/WebScan/ZapOutput/zap_results.json"

    # # Read the JSON file
    # with open(json_file_path, "r") as file:
    #     json_data = json.load(file)
     
    # output_file_path = "C:/Users/Administrator/source/repos/WebScan/ZapOutput/zap_report.txt" # Zap report file dir
    # parser = ZAPReportParser(json_data)
    # report = parser.parse_report()
    # parser.print_report(report) # Prints report to the cmd
    # parser.save_report_to_file(report, output_file_path) # Saves zap report as txt file
    # ---JSON Parser---
    
    # ---Report---

    # ---Report---
    
asyncio.get_event_loop().run_until_complete(main())
