from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import openpyxl  

# Configurar opções do Firefox
firefox_options = Options()
# firefox_options.add_argument("--headless")  
firefox_service = Service('C:/Users/emersonn/Desktop/Drivers/geckodriver.exe')  # Use o caminho absoluto

# Iniciar o navegador Firefox
driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

# URL do site
url = "https://www.rochafilho.com.br/imoveis/a-venda/teresina"
driver.get(url)

# Esperar um tempo para a página carregar
time.sleep(10)

# Definir o número de vezes que o botão deve ser clicado 
max_clicks = 76
clicks = 0

while clicks < max_clicks:
    try:
        # Tentar encontrar o botão "Carregar mais"
        load_more_button = driver.find_element(By.CSS_SELECTOR, ".pagination-cell")  # Substitua pelo seletor correto
        
        # Rolar a página até o botão e ajustar a rolagem para garantir a visibilidade
        driver.execute_script("arguments[0].scrollIntoView(true); window.scrollBy(0, -200);", load_more_button)
        time.sleep(1)  # Esperar um pouco após a rolagem

        # Se o botão for encontrado, clicar e esperar
        load_more_button.click()
        clicks += 1
        print(f"Clicou no botão 'Carregar mais' {clicks} vez(es).")
        time.sleep(10)  # Esperar o carregamento
    except Exception as e:
        print(f"Erro: {e}")
        print("Botão de carregar mais não encontrado ou não há mais páginas.")
        break

# Extrair o HTML da página
page_html = driver.page_source

# Usar BeautifulSoup para parsear o HTML
soup = BeautifulSoup(page_html, "html.parser")

# Encontrar todas as divs com a classe 'card-with-buttons__code'
codes = soup.find_all("p", class_="card-with-buttons__code")

# Encontrar todas as divs com a classe 'card-with-buttons__baseboard'
baseboards = soup.find_all("div", class_="card-with-buttons__baseboard")

# Encontrar os elementos <h2> com a classe 'card-with-buttons__heading'
headings = soup.find_all("h2", class_="card-with-buttons__heading")

# Encontrar as divs com a classe 'card-with-buttons__footer'
footers = soup.find_all("div", class_="card-with-buttons__footer")

# Encontrar todos os links com a classe 'card-with-buttons borderHover'
property_links = soup.find_all("a", class_="card-with-buttons borderHover")

# Função para verificar qual campo preencher com base no conteúdo do <li>
def verificar_campo(li_text):
    if "m²" in li_text:
        return "Área"
    elif "Quarto" in li_text or "Quartos" in li_text:
        return "Quarto"
    elif "Suíte" in li_text or "Suítes" in li_text:
        return "Suíte"
    elif "Banheiro" in li_text or "Banheiros" in li_text:
        return "Banheiro"
    elif "Vaga" in li_text or "Vagas" in li_text:
        return "Vaga"
    return None

# Criar um novo arquivo Excel e uma planilha
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Imóveis"

# Adicionar o cabeçalho
sheet.append(["Código", "Localização", "Imóvel", "Tipo de Oferta", "Valor", "Área", "Quarto", "Suíte", "Banheiro", "Vaga", "Link"])

print("Informações extraídas:")

# Iterar sobre as divs e headings
for idx, baseboard in enumerate(baseboards):
    # Dados que serão adicionados ao Excel
    row_data = []

    # Código (p com a classe 'card-with-buttons__code')
    if idx < len(codes):
        code_text = codes[idx].get_text(strip=True)
        row_data.append(code_text) 
    else:
        row_data.append("Código não disponível")

    # Localização (h2)
    if idx < len(headings):
        heading_text = headings[idx].get_text(strip=True)
        row_data.append(heading_text)
    else:
        row_data.append("Localização não disponível")

    # Imóvel (p com a classe 'card-with-buttons__title' dentro do footer)
    if idx < len(footers):
        footer = footers[idx]
        title_p = footer.find("p", class_="card-with-buttons__title")
        if title_p:
            title_text = title_p.get_text(strip=True)
            row_data.append(title_text)
        else:
            row_data.append("Imóvel não disponível")
    else:
        row_data.append("Imóvel não disponível")

    first_div = baseboard.find("div")
    if first_div:
        value_title = first_div.find("p", class_="card-with-buttons__value-title")
        value = first_div.find("p", class_="card-with-buttons__value")

        if value_title:
            row_data.append(value_title.get_text(strip=True))  # Tipo de Oferta
        else:
            row_data.append("Tipo de Oferta não disponível")

        if value:
            row_data.append(value.get_text(strip=True))  # Valor
        else:
            row_data.append("Valor não disponível")
    else:
        row_data.append("Tipo de Oferta não disponível")
        row_data.append("Valor não disponível")

    # Campos de Área, Quarto, Suíte, Banheiro e Vaga
    if idx < len(footers):
        ul_element = footers[idx].find("ul")
        if ul_element:
            li_items = ul_element.find_all("li")
            imovel_info = {
                "Área": None,
                "Quarto": None,
                "Suíte": None,
                "Banheiro": None,
                "Vaga": None
            }
            for li in li_items:
                li_text = li.get_text(strip=True)
                campo = verificar_campo(li_text)
                if campo and not imovel_info[campo]:
                    imovel_info[campo] = li_text
            
            # Preencher os campos no Excel
            row_data.append(imovel_info.get("Área", "Não disponível"))
            row_data.append(imovel_info.get("Quarto", "Não disponível"))
            row_data.append(imovel_info.get("Suíte", "Não disponível"))
            row_data.append(imovel_info.get("Banheiro", "Não disponível"))
            row_data.append(imovel_info.get("Vaga", "Não disponível"))
        else:
            row_data.extend(["Não disponível"] * 5)  # Preencher com 'Não disponível' se não houver dados
    else:
        row_data.extend(["Não disponível"] * 5)

    # Capturar o link (href) da tag 'a' com a classe 'card-with-buttons borderHover'
    if idx < len(property_links):
        property_link = property_links[idx].get("href", "Link não disponível")
        full_link = f"https://www.rochafilho.com.br{property_link}" if "http" not in property_link else property_link
        row_data.append(full_link) 
    else:
        row_data.append("Link não disponível")

    # Adicionar a linha na planilha
    sheet.append(row_data)

# Salvar o arquivo Excel
workbook.save("./Planilhas/imoveis_rocha_filho.xlsx")

# Fechar o navegador
driver.quit() 
