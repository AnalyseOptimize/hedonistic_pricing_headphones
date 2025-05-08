from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import random

# Настройка драйвера
service = Service('/opt/homebrew/bin/chromedriver')
options = Options()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=service, options=options)

def get_product_links():
    base_url = "https://doctorhead.ru/catalog/personal-audio/naushniki/"
    page = 1
    links = []
    
    while True:
        url = f"{base_url}?PAGEN_1={page}"
        print(f"Обрабатываю страницу {page}: {url}")
        
        try:
            driver.get(url)
            
            # Ожидание загрузки товаров
            WebDriverWait(driver, 0.1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.product-title'))
            )
            
            # Сбор ссылок
            products = driver.find_elements(By.CSS_SELECTOR, 'a.product-title')
            current_links = [p.get_attribute('href') for p in products]
            
            if not current_links:
                print(f"Страница {page} пустая, завершаю сбор")
                break
                
            links.extend(current_links)
            print(f"Найдено {len(current_links)} товаров на странице {page}")
            
            # Проверка последней страницы
            if page > 1 and links[-len(current_links):] == links[-2*len(current_links):-len(current_links)]:
                print("Обнаружена повторяющаяся страница, завершаю сбор")
                break
                
            page += 1
            time.sleep(random.uniform(0, 0.1))  # Случайная задержка
            
        except TimeoutException:
            print(f"Таймаут при загрузке страницы {page}")
            break
            
    return list(set(links))  # Удаление дубликатов

def parse_product(url):
    driver.get(url)
    product_data = {'URL': url}
    
    try:
        # Название
        product_data['Название'] = WebDriverWait(driver, 0.1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.product-main-info__title'))
        ).text.strip()
    except Exception as e:
        print(f"Ошибка названия {url}: {str(e)}")
        product_data['Название'] = None
    
    # Обработка цены с улучшенной логикой
    # Цена товара
    price = None
    try:
        # Основной вариант через data-атрибут
        price_element = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-price[data-price]'))
        )
        price = price_element.get_attribute('data-price')
    except:
        try:
            # Альтернативный вариант через текст
            price_element = WebDriverWait(driver, 0).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.price__value'))
            )
            price = price_element.text.replace(' ', '').replace('&nbsp;', '').strip()
        except Exception as e:
            print(f"Ошибка цен {url}: {str(e)}")
    
    product_data['Цена'] = int(price) if price and price.isdigit() else None
    
    try:
        # Количество отзывов
        reviews_element = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p.product-main-info__rating'))
        )
        reviews_text = reviews_element.text.strip()
        product_data['Отзывы'] = reviews_text.split()[0]
    except:
        product_data['Отзывы'] = 0
    
    # Сбор характеристик
    characteristics = {}
    try:
        # Раскрываем все характеристики
        try:
            show_more_button = WebDriverWait(driver, 0).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.link_more:not([style*="none"])'))
            )
            driver.execute_script("arguments[0].click();", show_more_button)
            time.sleep(0.1)
        except Exception as e:
            print(f"Ошибка характеристик_оснвоа {url}: {str(e)}")

        # Получаем все характеристики
        items = WebDriverWait(driver, 0).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.characteristic'))
        )
        
        for item in items:
            try:
                # Извлекаем название характеристики
                label = item.find_element(By.CSS_SELECTOR, '.characteristic__label span').text.strip()
                
                # Обрабатываем сложные значения
                value_element = item.find_element(By.CSS_SELECTOR, '.characteristic__value')
                
                # Удаляем вспомогательные элементы перед извлечением текста
                driver.execute_script("""
                    var elements = arguments[0].querySelectorAll('.tooltip, .tooltip-trigger, .tooltip-value');
                    for(var i=0; i < elements.length; i++){
                        elements[i].parentNode.removeChild(elements[i]);
                    }
                """, value_element)
                
                value = value_element.text.strip()
                
                # Обработка специальных случаев
                if label == 'Цвет':
                    color = item.find_element(By.CSS_SELECTOR, '.color__box').get_attribute('title')
                    characteristics[label] = color
                elif label == 'Бренд':
                    brand = item.find_element(By.CSS_SELECTOR, 'a.link_color').text.strip()
                    characteristics[label] = brand
                else:
                    characteristics[label] = value.replace('\n', ' ').replace('  ', ' ')
                    
            except Exception as e:
                print(f"Ошибка специальных случаев {url}: {str(e)}")
                
    except Exception as e:
        print(f"Ошибка характеристик {url}: {str(e)}")
    
    product_data.update(characteristics)
    
    return product_data

# Запуск парсера
try:
    product_links = get_product_links()
    print(f"Всего найдено уникальных товаров: {len(product_links)}")
    
    data = []
    for i, link in enumerate(product_links, 1):
        try:
            product = parse_product(link)
            data.append(product)
            print(f"Обработано: {i}/{len(product_links)}")
        except Exception as e:
            print(f"Ошибка при обработке {link}: {str(e)}")
            
    df = pd.DataFrame(data)
    df.to_csv('doctorhead_products.csv', index=False, encoding='utf-8-sig', sep=';')
    
finally:
    driver.quit()