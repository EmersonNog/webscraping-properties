from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import openpyxl
import time

# Configurar opções do Firefox
firefox_options = Options()
# firefox_options.add_argument("--headless")  # Execute o Firefox em modo headless, se necessário
firefox_service = Service('C:/Users/emersonn/Desktop/Drivers/geckodriver.exe')  # Use o caminho absoluto

# Iniciar o navegador Firefox
driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

# URL base do site
base_url = "https://www.rochaerocha.com.br/imoveis/comprar/?pg="
start_page = 1  # Página inicial
end_page = 138  # Ajuste o número total de páginas conforme necessário
current_page = start_page

# Criar um novo arquivo Excel e uma planilha
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Imóveis"

# Adicionar o cabeçalho
sheet.append(["Código", "Preço", "Bairro", "Endereço", "Tipo", "Área", "Quartos", "Banheiros", "Garagem", "Sala de Estar", "Sala de Visita", "Links"])

# Usar WebDriverWait para aguardar elementos quando necessário
wait = WebDriverWait(driver, 10)

try:
    while current_page <= end_page:
        # Construa a URL para a página atual
        url = f"{base_url}{current_page}"
        driver.get(url)

        # Esperar o tempo necessário para a página carregar
        time.sleep(5)  # Ajuste conforme necessário

        # Obter o HTML da página atual
        page_html = driver.page_source

        # Usar BeautifulSoup para parsear o HTML
        soup = BeautifulSoup(page_html, "html.parser")

        # Encontrar todos os contêineres de imóveis
        property_cards = soup.find_all("div", class_="property")  # Ajuste a classe conforme necessário

        for card in property_cards:
            # Inicializa variáveis com valores padrão
            codigo = ""
            preco = ""
            bairro = ""
            endereco = ""
            tipo = ""
            area = ""
            quartos = ""
            banheiros = ""
            garagem = ""
            sala_estar = ""
            sala_visita = ""
            links = []

            # Encontra o título
            h2 = card.find("h2", class_="title")
            # Encontra a tag <span> com a classe "properties-cod"
            span = h2.find("span", class_="properties-cod") if h2 else None
            # Encontra todas as tags <a> dentro do <h2>
            a_tags = h2.find_all("a") if h2 else []
            # Encontra a div com a classe "property-price" dentro do cartão do imóvel
            price_div = card.find("div", class_="property-price")  # Ajuste conforme necessário
            # Encontra a div com a classe "property-tag button alt bairro"
            bairro_div = card.find("div", class_="property-tag button alt bairro")
            # Encontra a tag <h3> com a classe "property-address"
            address_h3 = card.find("h3", class_="property-address")
            # Encontra a div com a classe "property-tipo" e o conteúdo <strong> dentro dela
            tipo_div = card.find("div", class_="property-tipo")
            tipo_strong = tipo_div.find("strong") if tipo_div else None
            # Encontra a lista de facilidades
            facilities_ul = card.find("ul", class_="facilities-list clearfix")
            facilities_list = facilities_ul.find_all("li") if facilities_ul else []

            bairro = bairro_div.text.strip() if bairro_div else ""
            endereco = address_h3.text.strip() if address_h3 else ""
            tipo = tipo_strong.text.strip() if tipo_strong else ""

            if span:
                codigo = span.text.strip()

            if price_div:
                preco = price_div.text.strip()

            # Impressão das facilidades
            if facilities_list:
                for li in facilities_list:
                    li_text = li.text.strip()
                    if "m²" in li_text:
                        area = li_text
                    elif "Quarto" in li_text or "Quartos" in li_text:
                        quartos = li_text
                    elif "Banheiro" in li_text or "Banheiros" in li_text:
                        banheiros = li_text
                    elif "Garagem" in li_text or "Garagens" in li_text:
                        garagem = li_text
                    elif "Sala de estar" in li_text:
                        sala_estar = li_text
                    elif "Sala de visita" in li_text:
                        sala_visita = li_text

            # Adiciona links encontrados
            for a in a_tags:
                links.append(a.get("href"))

            # Adiciona os dados extraídos à planilha
            sheet.append([codigo, preco, bairro, endereco, tipo, area, quartos, banheiros, garagem, sala_estar, sala_visita, ", ".join(links)])

            # Exibição dos dados no console (opcional)
            print(f'Código: {codigo}')
            print(f'Preço: {preco}')
            print(f'Bairro: {bairro}')
            print(f'Endereço: {endereco}')
            print(f'Tipo: {tipo}')
            print(f'Área: {area}')
            print(f'Quartos: {quartos}')
            print(f'Banheiros: {banheiros}')
            print(f'Garagem: {garagem}')
            print(f'Sala de estar: {sala_estar}')
            print(f'Sala de visita: {sala_visita}')
            for link in links:
                print(f'Link: {link}')
            print('-------------')

        # Avançar para a próxima página
        current_page += 1

except Exception as e:
    print(f'Erro: {e}')

# Salvar o arquivo Excel
workbook.save("./Planilhas/imoveis_rocha_erocha.xlsx")

# Fechar o navegador
driver.quit()
