import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurações do Selenium
options = Options()
options.headless = False  # Defina como True se não precisar ver a interface gráfica do Firefox

# Defina o caminho para o GeckoDriver
service = Service('C:/Users/emersonn/Desktop/Drivers/geckodriver.exe')  # Use o caminho absoluto

# Inicialize o WebDriver do Firefox
driver = webdriver.Firefox(service=service, options=options)

url = "https://www.nogueiranetoimoveis.com.br/imoveis/a-venda/teresina"
driver.get(url)
time.sleep(5)

# Função para fechar o banner de cookies
def close_cookie_banner():
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'cookies-component'))
        )
        driver.execute_script("arguments[0].click();", cookie_button)
        print("Banner de cookies fechado.")
    except Exception as e:
        print(f"Banner de cookies não encontrado ou não pode ser fechado: {e}")

# Fechar o banner de cookies antes de continuar
close_cookie_banner()

def scrape_page(existing_codes):
    headings = driver.find_elements(By.CSS_SELECTOR, 'h2.card-with-buttons__heading')
    code_divs = driver.find_elements(By.CSS_SELECTOR, 'p.card-with-buttons__code')
    title_paragraphs = driver.find_elements(By.CSS_SELECTOR, 'p.card-with-buttons__title')
    offer_types = driver.find_elements(By.CSS_SELECTOR, 'p.card-with-buttons__value-title')
    prices = driver.find_elements(By.CSS_SELECTOR, 'p.card-with-buttons__value')
    footer_divs = driver.find_elements(By.CSS_SELECTOR, 'div.card-with-buttons__footer')
    links = driver.find_elements(By.CSS_SELECTOR, 'a.card-with-buttons.borderHover')  # Encontrar links com a classe especificada

    labels = {
        'Área': None,
        'Quarto': None,
        'Suíte': None,
        'Banheiro': None,
        'Vaga': None
    }

    def format_price(price_text):
        return price_text.replace('A partir de ', '').strip()

    def parse_footer_items(footer_items):
        footer_data = {}
        for item in footer_items:
            item = item.strip()
            if 'm²' in item:
                footer_data['Área'] = item.replace('m²', '').strip() + " m²"
            elif 'Quarto' in item:
                footer_data['Quarto'] = item.replace('Quarto', '').strip().replace('s', '')
            elif 'Suíte' in item:
                footer_data['Suíte'] = item.replace('Suíte', '').strip().replace('s', '')
            elif 'Banheiro' in item:
                footer_data['Banheiro'] = item.replace('Banheiro', '').strip().replace('s', '')
            elif 'Vaga' in item:
                footer_data['Vaga'] = item.replace('Vaga', '').strip().replace('s', '')
        return footer_data

    footer_items_list = []
    for footer_div in footer_divs:
        ul = footer_div.find_element(By.TAG_NAME, 'ul')
        if ul:
            list_items = ul.find_elements(By.TAG_NAME, 'li')
            footer_items_list.append([li.text.strip() for li in list_items])

    max_items = min(len(headings), len(code_divs), len(title_paragraphs), len(offer_types), len(prices), len(footer_items_list), len(links))

    data = []  # Lista para armazenar os dados

    if max_items > 0:
        for i in range(max_items):
            code = code_divs[i].text.strip()

            # Ignorar o imóvel com o código específico
            if code == "14702931-NOGW":
                continue

            # Verificar se o código já foi capturado
            if code not in existing_codes:
                location = headings[i].text.strip().split(',')[0]
                title = title_paragraphs[i].text.strip()
                offer_type = offer_types[i].text.strip()
                price = format_price(prices[i].text.strip())
                footer_items = footer_items_list[i] if i < len(footer_items_list) else []
                link = links[i].get_attribute('href') if i < len(links) else ''

                footer_data = parse_footer_items(footer_items)

                # Adicionando os dados capturados à lista `data`
                data.append({
                    'Código': code,
                    'Localização': location,
                    'Título': title,
                    'Tipo de Oferta': offer_type,
                    'Preço': price,
                    'Área': footer_data.get('Área', ''),
                    'Quarto': footer_data.get('Quarto', ''),
                    'Suíte': footer_data.get('Suíte', ''),
                    'Banheiro': footer_data.get('Banheiro', ''),
                    'Vaga': footer_data.get('Vaga', ''),
                    'Link': link  # Adicionando o link extraído
                })

                # Adicionar o código à lista de códigos já capturados
                existing_codes.add(code)
    else:
        print("Nenhum par de código, localização, título, tipo de oferta e preço encontrado.")
    
    return data


def scroll_to_element(element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)

# Função para clicar na div de paginação
def click_pagination():
    all_data = []
    existing_codes = set()  # Conjunto para armazenar códigos únicos de imóveis

    for _ in range(22):  # Tentar clicar 2 vezes
        try:
            # Encontrar todos os elementos de paginação
            pagination_cells = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.pagination-cell'))
            )
            
            # Verificar se há elementos de paginação
            if pagination_cells:
                # Rolagem até o primeiro elemento de paginação
                scroll_to_element(pagination_cells[0])
                
                # Clicar no primeiro elemento de paginação
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(pagination_cells[0])
                ).click()
                time.sleep(3)  # Espera o carregamento da nova página
                
                # Extrair dados da página
                page_data = scrape_page(existing_codes)
                all_data.extend(page_data)
                
        except Exception as e:
            print(f"Erro ao clicar na paginação: {e}")
            break

    return all_data

# Capturar os dados e clicar na paginação
data = click_pagination()

# Salvar os dados em um arquivo Excel
df = pd.DataFrame(data)
df.to_excel('./Planilhas/imoveis_nogueira_neto.xlsx', index=False) 

# Fechar o navegador
driver.quit()
