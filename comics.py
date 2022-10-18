# It is necessary to parse information on comics from the site https://www.webtoons.com/en/genre
# The final result should be presented in csv and excel files
# Columns in files: title, url, genre, subscriptions, views, number of authors
# Необходимо спарсить информацию по комиксам с сайта https://www.webtoons.com/en/genre
# Конечный результат должен быть представлен в csv и excel файлах
# Столбцы в файлах: название, url, genre, подписки, просмотры, количество авторов



import os
import csv

import requests
import lxml
import pandas as pd

from myheaders import headers, path
from time import sleep
from bs4 import BeautifulSoup


def get_list_of_urls(html_code: str) -> list:
    # получение списка ссылок на комиксы
    # getting a list of links to comics
    list = []
    soup = BeautifulSoup(html_code, 'lxml')
    genres = soup.find_all('h2', class_='sub_title')

    for item in genres:
        block_of_urls = item.find_next_sibling('ul', class_="card_lst").find_all('li')
        for i in block_of_urls:
            url = i.find('a', class_='card_item').get('href')
            list.append(url)

    return list


def create_csv_file(file_name: str) -> None:
    # creating a csv file
    # создание csv файл
    cells = [
        'название',
        'url',
        'genre',
        'подписки',
        'просмотры',
        'количество авторов'
    ]

    with open(file_name, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            cells
        )


def get_regular_number(number: str) -> int:
    # conversion to a regular number
    # перевод в обычное число
    if 'M' in number:
        new_number = number.replace('M', '')
        if '.' in new_number:
            return int(new_number.replace('.', '')) * 100000
        else:
            return int(new_number) * 1000000
    elif 'B' in number:
        new_number = number.replace('B', '')
        if '.' in new_number:
            return int(new_number.replace('.', '')) * 100000000
        else:
            return int(new_number) * 1000000000
    else:
        if ',' in number:
            return int(number.replace(',', ''))
        else:
            return int(number)


def add_info_to_csv(filename: str, url: str) -> None:
    # adding a line to a file
    # добавление строки в файл
    req = requests.get(url=url, headers=headers)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(req.text)

    with open(filename, 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    name = soup.find('h1', class_='subj').text
    genre = soup.find('h2', class_='genre').text
    subscriptions = get_regular_number(
        soup.find('ul', class_='grade_area').find('span', class_='ico_subscribe').find_next_sibling('em').text
    )
    views = get_regular_number(
        soup.find('ul', class_='grade_area').find('span', class_='ico_view').find_next_sibling('em').text
    )
    authors = soup.find('div', class_='ly_box ly_creator').find_all('h3', class_='title')
    number_of_authors = len([i.text.strip() for i in authors])

    with open(r'data\result_csv.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            (
                name,
                url,
                genre,
                subscriptions,
                views,
                number_of_authors
            )
        )


def create_excel(filename_csv: str, filename_excel: str) -> None:
    # conversion to excel file
    # конвертация в excel файл
    csv = pd.read_csv(
        filename_csv,
        encoding='utf-8',
        delimiter=';'
    )
    excel_writer = pd.ExcelWriter(filename_excel)
    csv.to_excel(
        excel_writer,
        encoding='utf-8',
        index=False,
        sheet_name='Sheet1',
        na_rep='NaN'
    )

    for column in csv:
        column_width = max(csv[column].astype(str).map(len).max(), len(column))
        col_idx = csv.columns.get_loc(column)
        excel_writer.sheets['Sheet1'].set_column(col_idx, col_idx, column_width)

    excel_writer.save()


def get_data() -> None:
    # getting data about comics
    # получение данных о комиксах
    req = requests.get(
        url='https://www.webtoons.com/en/genre',
        headers=headers
    )

    with open('data\index.html', 'w', encoding='utf-8') as file:
        file.write(req.text)

    with open(r'data\index.html', 'r', encoding='utf-8') as file:
        src = file.read()

    list_of_urls = get_list_of_urls(src)

    create_csv_file(r'data\result_csv.csv')

    count = 0
    for url in list_of_urls:
        try:
            count += 1
            add_info_to_csv(url=url, filename=fr'data\comics\number_{count}.html')
        except Exception as error:
            print(error)
        else:
            print(f'[INFO] Iteration {count} is completed')
        finally:
            sleep(1)

    try:
        create_excel(r'data\result_csv.csv', r'data\result_excel.xlsx')
    except Exception as error:
        print(error)
    else:
        print('Excel file is recorded')

    print('Parsing completed')


def main():
    os.chdir(path)
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data/comics'):
        os.mkdir('data/comics')
    get_data()


if __name__ == '__main__':
    main()