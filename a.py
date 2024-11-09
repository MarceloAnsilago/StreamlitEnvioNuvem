import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time

st.title("Exibir QR Code do WhatsApp Web")

# Configuração do ChromeDriver para o Streamlit Cloud
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executa em modo headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1024,768")

if st.button("Abrir WhatsApp Web e Exibir QR Code"):
    # Inicializa o driver com o caminho do ChromeDriver no Streamlit Cloud
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    whatsapp_url = "https://web.whatsapp.com/"
    
    # Acessa o WhatsApp Web
    driver.get(whatsapp_url)
    
    # Aguardar alguns segundos para carregar o QR code
    time.sleep(5)
    
    # Captura uma captura de tela da página inteira
    screenshot_path = "whatsapp_qr.png"
    driver.save_screenshot(screenshot_path)
    
    # Exibe a captura de tela (QR code incluído) no Streamlit
    image = Image.open(screenshot_path)
    st.image(image, caption="Escaneie o QR Code para entrar no WhatsApp Web", use_column_width=True)
    
    # Encerra o driver
    driver.quit()
