import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

product_info = []

def SearchProducListPrado(product):
    productSearch = urllib.parse.quote(product)
    url = "https://www.prado.com.sv/catalogsearch/result/?q={}".format(productSearch)
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.100.0"}
    res = requests.get(url, headers=headers)
    return url

def GetContentListPrado(url, n):
    iSnull = 1
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)
    store = "Prado"
    try:
        product_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ais-Hits'))
        )
        productItems = product_section.find_elements(By.CLASS_NAME, 'ais-Hits-item')
        if productItems:
            iSnull = 2;
            for i in range(min(n, len(productItems))):
                productName = productItems[i].find_element(By.CSS_SELECTOR, 'h3.result-title').text.strip()
                try:
                    price_element = productItems[i].find_element(By.CLASS_NAME, 'price')
                    newPrice = price_element.find_element(By.CLASS_NAME, 'after_special').text.strip()
                    oldPrice = price_element.find_element(By.CLASS_NAME, 'before_special').text.strip()
                except NoSuchElementException:
                    newPrice = "none"
                    oldPrice = "none"

                product_info.append({"name": productName, "newPrice": newPrice, "oldPrice": oldPrice, "store": store})

            return product_info
        else:
                return FillEmptyProdut(n, store)
    finally:
            if iSnull == 1:
                return FillEmptyProdut(n, store)
            else:
                driver.quit()

def searchProductCuracao(product):
    product_search = urllib.parse.quote(product)
    url = f"https://www.lacuracaonline.com/elsalvador/catalogsearch/result/?q={product_search}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.100.0"
    }
    res = requests.get(url, headers=headers)
    return res.text

def getContentCuracao(html, n):
    soup = BeautifulSoup(html, 'html.parser')
    productItems = soup.select('.product-item')
    store = "Curacao"
    f = 3
    for i in range(1, min(n + 1, len(productItems))):  
        producNameElement = productItems[i].select_one('.product-item-link')
        newPriceElement = productItems[i].select_one('.special-price .price')
        oldPriceElement = productItems[i].select_one('.old-price .price')
        if producNameElement and newPriceElement and oldPriceElement:
            productName = producNameElement.text.strip()
            newPrice = newPriceElement.text.strip()
            oldPrice = oldPriceElement.text.strip()
            f -=1
        else:
            f =3
        
        product_info.append({"name": productName, "oldPrice": oldPrice, "newPrice": newPrice, "store": store})

    if f == 3:
        return FillEmptyProdut(n, store)
    else:
        return product_info

def searchProductTropigas(product):
    product_search = urllib.parse.quote(product)
    url = f"https://www.almacenestropigas.com/elsalvador/catalogsearch/result/index/?q={product_search}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.100.0"
    }
    res = requests.get(url, headers=headers)
    return res.text

def getContentTropigas(url, n):
    soup = BeautifulSoup(url, 'html.parser')
    productItems = soup.select('.item.product.product-item')
    store = "Almacenes Tropigas"
    if not productItems:
        print("No se encontraron productos en la página.")
        return FillEmptyProdut(n, store)
    else:
        for i in range(min(n, len(productItems))):
            productName = productItems[i].select_one('.product-item-link').text.strip()
            newPriceElement = productItems[i].select_one('.special-price .price')
            newPrice = newPriceElement.text.strip() if newPriceElement else None
            oldPriceElement = productItems[i].select_one('.old-price .price')
            oldPrice = oldPriceElement.text.strip() if oldPriceElement else None
            product_info.append({"name": productName, "oldPrice": oldPrice, "newPrice": newPrice, "store": store})

    return product_info

def CreateJson(product_info):
    json_file_path = "productData.json"
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(product_info, json_file, indent=2, ensure_ascii=False)

def FillEmptyProdut(n, store):
    for i in range(n):
        product_info.append({"name": "none", "newPrice": "none", "oldPrice": "none", "store": store})
    return product_info

#search = "lavadora"
quantity = 3
product_info = []
store = " "

# Prado
linkPrado = SearchProducListPrado(search)
GetContentListPrado(linkPrado, quantity)

# Curacao
htmlCuracao = searchProductCuracao(search)
getContentCuracao(htmlCuracao, n=3)

# AlmacenTropigas
htmlTropigas = searchProductTropigas(search)
getContentTropigas(htmlTropigas, n=3)

# Create JSON
CreateJson(product_info)
