import streamlit as st
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from PIL import Image
import time

st.title("Exibir QR Code do WhatsApp Web")

# Configuração do Firefox para o Streamlit Cloud
firefox_options = Options()
firefox_options.add_argument("--headless")  # Executa em modo headless
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--disable-dev-shm-usage")
firefox_options.add_argument("--window-size=1024,768")

if st.button("Abrir WhatsApp Web e Exibir QR Code"):
    # Inicializa o driver com o caminho do GeckoDriver no Streamlit Cloud
    service = Service("/usr/bin/geckodriver")
    driver = webdriver.Firefox(service=service, options=firefox_options)
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
