from module_package import *


if __name__ == '__main__':
    file_name = os.path.basename(__file__).rstrip('.py')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    url = 'https://www.flinnsci.com/'
    base_url = 'https://www.flinnsci.com'
    soup = get_soup(url, headers)
    data = soup.find_all('li', class_='b-main-nav-inner-content__hidden-content__links-list-item_first-level')
    for single_data in data:
        content = single_data.find('a')
        if 'new-science-products' not in str(content):
            if 'http' not in str(content):
                main_url = f'{base_url}{content['href']}'
            else:
                main_url = content['href']
            print(f'main_url------------->{main_url}')
            product_category = content.text.strip()
            if main_url in read_log_file():
                continue
            inner_req = get_soup(main_url, headers)
            if inner_req.find('a', class_='b-categories__category__link'):
                inner_category = inner_req.find_all('a', class_='b-categories__category__link')
                for category in inner_category:
                    category_url = f'{base_url}{category["href"]}'
                    product_sub_category = category.find('h3', class_='b-categories__category__name').text.strip()
                    category_req = get_soup(category_url, headers)
                    if category_req.find('div', id='FilteredListList'):
                        content_id = category_req.find('div', id='FilteredListList')['data-category']
                        page_nav_number = category_req.find('h3', class_='hidden-lg hidden-xs b-filtered-list__nav-heading__current-category').text.split('(', 1)[-1].replace(')', '').strip()
                        page_data = math.ceil(int(page_nav_number) / int(6))
                        for i in range(0, int(page_data)):
                            json_url = f'https://www.flinnsci.com/api/Search/{content_id}/{i}?type=All&srt=d'
                            json_soup = get_json_response(json_url, headers)
                            content_json = json_soup['Items']
                            for single_contents in content_json:
                                product_url = f'{base_url}{single_contents['Url']}'
                                print(product_url)
                                response = requests.get(product_url, headers=headers)
                                product_request = BeautifulSoup(response.text, 'html.parser')
                                if product_request is None:
                                    continue
                                if not product_request.find('ul', class_='product-page__info--options list'):
                                    '''PRODUCT NAME AND PRODUCT QUANTITY'''
                                    product_name = single_contents['Name']
                                    if re.search('Pkg. of \d+', str(product_name)):
                                        product_quantity = re.search('Pkg. of \d+', str(product_name)).group().replace('Pkg. of', '').strip()
                                    else:
                                        product_quantity = 1
                                    '''PRODUCT ID'''
                                    try:
                                        if product_request.find('div', styel='display: flex; align-items: center;'):
                                            product_id = strip_it(product_request.find('div', styel='display: flex; align-items: center;').text.replace('Item #:', '').strip())
                                        else:
                                            product_id = str(single_contents['SKUNumbers']).replace("['", '').replace("']", '').strip()
                                    except:
                                        product_id = ''
                                    '''PRODUCT PRICE'''
                                    product_price = f'${single_contents['PriceMax']}'
                                    if product_url in read_log_file():
                                        continue
                                    print('current datetime------>', datetime.now())
                                    dictionary = get_dictionary(product_category=product_category, product_sub_category=product_sub_category, product_ids=product_id, product_names=product_name, product_quantities=product_quantity, product_prices=product_price, product_urls=product_url)
                                    articles_df = pd.DataFrame([dictionary])
                                    articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first',
                                                                inplace=True)
                                    if os.path.isfile(f'{file_name}.csv'):
                                        articles_df.to_csv(f'{file_name}.csv', index=False, header=False, mode='a')
                                    else:
                                        articles_df.to_csv(f'{file_name}.csv', index=False)
                                    write_visited_log(product_url)
                                else:
                                    sub_product = product_request.find('ul', class_='product-page__info--options list').find_all('li')
                                    for single_product in sub_product:
                                        product_url = f'{base_url}{single_product.find('a', class_='option-link col-xs-12 col-sm-6')['href']}'
                                        '''PRODUCT NAME AND PRODUCT ID'''
                                        try:
                                            inner_data = single_product.find('div', class_='product-page__info--item list col-xs-8')
                                            product_id = inner_data.find('span', class_='code').extract().text.replace('(', '').replace(')', '').strip()
                                            product_names = strip_it(inner_data.text.strip())
                                            product_name = product_names
                                            if re.search('Pkg. of \d+', str(product_name)):
                                                product_quantity = re.search('Pkg. of \d+',
                                                                             str(product_name)).group().replace(
                                                    'Pkg. of', '').strip()
                                            else:
                                                product_quantity = 1
                                        except:
                                            product_name = ''
                                            product_id = ''
                                        '''PRODUCT PRICE'''
                                        try:
                                            if single_product.find('span', class_='product-page__price'):
                                                product_price = strip_it(single_product.find('span', class_='product-page__price').text.strip())
                                            elif single_product.find('div', class_='product-page__price'):
                                                product_data = single_product.find('div', class_='product-page__price')
                                                if product_data.find('span', class_='product-page__original-price'):
                                                    extract_tag = product_data.find('span', class_='product-page__original-price').extract()
                                                    product_price = strip_it(product_data.text.strip())
                                                else:
                                                    product_price = strip_it(product_data.text.strip())
                                            else:
                                                product_price = ''
                                        except:
                                            product_price = ''
                                        '''PRODUCT QUANTITY'''
                                        product_quantity = 1
                                        if product_url in read_log_file():
                                            continue
                                        print('current datetime------>', datetime.now())
                                        dictionary_1 = get_dictionary(product_category=product_category, product_sub_category=product_sub_category, product_ids=product_id, product_names=product_name, product_quantities=product_quantity, product_prices=product_price, product_urls=product_url)
                                        articles_df = pd.DataFrame([dictionary_1])
                                        articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first',
                                                                    inplace=True)
                                        if os.path.isfile(f'{file_name}.csv'):
                                            articles_df.to_csv(f'{file_name}.csv', index=False, header=False, mode='a')
                                        else:
                                            articles_df.to_csv(f'{file_name}.csv', index=False)
                                        write_visited_log(product_url)
                    else:
                        inner_category = category_req.find_all('a', class_='b-categories__category__link')
                        for categories in inner_category:
                            category_url = f'{base_url}{categories["href"]}'
                            product_sub_category = category.find('h3', class_='b-categories__category__name').text.strip()
                            category_reqs = get_soup(category_url, headers)
                            content_id = category_reqs.find('div', id='FilteredListList')['data-category']
                            page_nav = category_reqs.find('h3',
                                                          class_='hidden-lg hidden-xs b-filtered-list__nav-heading__current-category').text.split(
                                '(', 1)[-1].replace(')', '').strip()
                            page_data = math.ceil(int(page_nav) / int(6))
                            for i in range(0, int(page_data)):
                                json_url = f'https://www.flinnsci.com/api/Search/{content_id}/{i}?type=All&srt=d'
                                json_soup = get_json_response(json_url, headers)
                                content_json = json_soup['Items']
                                for single_contents in content_json:
                                    product_url = f'{base_url}{single_contents['Url']}'
                                    print(product_url)
                                    response = requests.get(product_url, headers=headers)
                                    product_request = BeautifulSoup(response.text, 'html.parser')
                                    if product_request is None:
                                        continue
                                    if not product_request.find('ul', class_='product-page__info--options list'):
                                        '''PRODUCT NAME AND PRODUCT QUANTITY'''
                                        product_name = single_contents['Name']
                                        if re.search('Pkg. of \d+', str(product_name)):
                                            product_quantity = re.search('Pkg. of \d+', str(product_name)).group().replace('Pkg. of', '').strip()
                                        else:
                                            product_quantity = 1
                                        '''PRODUCT ID'''
                                        try:
                                            if product_request.find('div', styel='display: flex; align-items: center;'):
                                                product_id = strip_it(product_request.find('div',
                                                                                           styel='display: flex; align-items: center;').text.replace(
                                                    'Item #:', '').strip())
                                            else:
                                                product_id = str(single_contents['SKUNumbers']).replace("['", '').replace("']", '').strip()
                                        except:
                                            product_id = ''
                                        '''PRODUCT PRICE'''
                                        product_price = f'${single_contents['PriceMax']}'
                                        if product_url in read_log_file():
                                            continue
                                        print('current datetime------>', datetime.now())
                                        dictionary_2 = get_dictionary(product_category=product_category, product_sub_category=product_sub_category, product_ids=product_id, product_names=product_name, product_quantities=product_quantity, product_prices=product_price, product_urls=product_url)
                                        articles_df = pd.DataFrame([dictionary_2])
                                        articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first',
                                                                    inplace=True)
                                        if os.path.isfile(f'{file_name}.csv'):
                                            articles_df.to_csv(f'{file_name}.csv', index=False, header=False, mode='a')
                                        else:
                                            articles_df.to_csv(f'{file_name}.csv', index=False)
                                        write_visited_log(product_url)
                                    else:
                                        sub_product = product_request.find('ul', class_='product-page__info--options list').find_all('li')
                                        for single_product in sub_product:
                                            product_url = f'{base_url}{single_product.find('a', class_='option-link col-xs-12 col-sm-6')['href']}'
                                            '''PRODUCT NAME AND PRODUCT ID'''
                                            try:
                                                inner_data = single_product.find('div', class_='product-page__info--item list col-xs-8')
                                                product_id = inner_data.find('span', class_='code').extract().text.replace('(', '').replace(')', '').strip()
                                                product_names = strip_it(inner_data.text.strip())
                                                product_name = product_names
                                                if re.search('Pkg. of \d+', str(product_name)):
                                                    product_quantity = re.search('Pkg. of \d+', str(product_name)).group().replace(
                                                        'Pkg. of', '').strip()
                                                else:
                                                    product_quantity = 1
                                            except:
                                                product_name = ''
                                                product_id = ''
                                            '''PRODUCT PRICE'''
                                            try:
                                                if single_product.find('span', class_='product-page__price'):
                                                    product_price = strip_it(single_product.find('span', class_='product-page__price').text.strip())
                                                elif single_product.find('div', class_='product-page__price'):
                                                    product_data = single_product.find('div', class_='product-page__price')
                                                    if product_data.find('span', class_='product-page__original-price'):
                                                        extract_tag = product_data.find('span', class_='product-page__original-price').extract()
                                                        product_price = strip_it(product_data.text.strip())
                                                    else:
                                                        product_price = strip_it(product_data.text.strip())
                                                else:
                                                    product_price = ''
                                            except:
                                                product_price = ''
                                            '''PRODUCT QUANTITY'''
                                            product_quantity = 1
                                            if product_url in read_log_file():
                                                continue
                                            print('current datetime------>', datetime.now())
                                            dictionary_3 = get_dictionary(product_category=product_category, product_sub_category=product_sub_category, product_ids=product_id, product_names=product_name, product_quantities=product_quantity, product_prices=product_price, product_urls=product_url)
                                            articles_df = pd.DataFrame([dictionary_3])
                                            articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first', inplace=True)
                                            if os.path.isfile(f'{file_name}.csv'):
                                                articles_df.to_csv(f'{file_name}.csv', index=False, header=False,
                                                                   mode='a')
                                            else:
                                                articles_df.to_csv(f'{file_name}.csv', index=False)
                                            write_visited_log(product_url)
            elif inner_req.find('div', id='FilteredListList'):
                content_id = inner_req.find('div', id='FilteredListList')['data-category']
                page_nav_number = inner_req.find('h3', class_='hidden-lg hidden-xs b-filtered-list__nav-heading__current-category').text.split('(', 1)[-1].replace(')', '').strip()
                page_data = math.ceil(int(page_nav_number) / int(6))
                for i in range(0, int(page_data)):
                    json_url = f'https://www.flinnsci.com/api/Search/{content_id}/{i}?type=All&srt=d'
                    json_soup = get_json_response(json_url, headers)
                    content_json = json_soup['Items']
                    for single_contents in content_json:
                        product_name = single_contents['Name']
                        product_url = f'{base_url}{single_contents['Url']}'
                        print(product_url)
                        response = requests.get(product_url, headers=headers)
                        product_request = BeautifulSoup(response.text, 'html.parser')
                        if product_request is None:
                            continue
                        if not product_request.find('ul', class_='product-page__info--options list'):
                            '''PRODUCT NAME AND PRODUCT QUANTITY'''
                            product_name = single_contents['Name']
                            if re.search('Pkg. of \d+', str(product_name)):
                                product_quantity = re.search('Pkg. of \d+', str(product_name)).group().replace('Pkg. of', '').strip()
                            else:
                                product_quantity = 1
                            '''PRODUCT ID'''
                            try:
                                if product_request.find('div', styel='display: flex; align-items: center;'):
                                    product_id = strip_it(product_request.find('div', styel='display: flex; align-items: center;').text.replace('Item #:', '').strip())
                                else:
                                    product_id = str(single_contents['SKUNumbers']).replace("['", '').replace("']", '').strip()
                            except:
                                product_id = ''
                            '''PRODUCT PRICE'''
                            product_price = f'${single_contents['PriceMax']}'
                            if product_url in read_log_file():
                                continue
                            print('current datetime------>', datetime.now())
                            dictionary_4 = get_dictionary(product_category=product_category, product_sub_category='NA', product_ids=product_id, product_names=product_name, product_quantities=product_quantity, product_prices=product_price, product_urls=product_url)
                            articles_df = pd.DataFrame([dictionary_4])
                            articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first',
                                                        inplace=True)
                            if os.path.isfile(f'{file_name}.csv'):
                                articles_df.to_csv(f'{file_name}.csv', index=False, header=False, mode='a')
                            else:
                                articles_df.to_csv(f'{file_name}.csv', index=False)
                            write_visited_log(product_url)
                        else:
                            sub_product = product_request.find('ul', class_='product-page__info--options list').find_all('li')
                            for single_product in sub_product:
                                product_url = f'{base_url}{single_product.find('a', class_='option-link col-xs-12 col-sm-6')['href']}'
                                '''PRODUCT NAME AND PRODUCT ID'''
                                try:
                                    inner_data = single_product.find('div', class_='product-page__info--item list col-xs-8')
                                    product_id = inner_data.find('span', class_='code').extract().text.replace('(','').replace(')', '').strip()
                                    product_names = strip_it(inner_data.text.strip())
                                    product_name = product_names
                                    if re.search('Pkg. of \d+', str(product_name)):
                                        product_quantity = re.search('Pkg. of \d+', str(product_name)).group().replace(
                                            'Pkg. of', '').strip()
                                    else:
                                        product_quantity = 1
                                except:
                                    product_name = ''
                                    product_id = ''
                                '''PRODUCT PRICE'''
                                try:
                                    if single_product.find('span', class_='product-page__price'):
                                        product_price = strip_it(single_product.find('span', class_='product-page__price').text.strip())
                                    elif single_product.find('div', class_='product-page__price'):
                                        product_data = single_product.find('div', class_='product-page__price')
                                        if product_data.find('span', class_='product-page__original-price'):
                                            extract_tag = product_data.find('span', class_='product-page__original-price').extract()
                                            product_price = strip_it(product_data.text.strip())
                                        else:
                                            product_price = strip_it(product_data.text.strip())
                                    else:
                                        product_price = ''
                                except:
                                    product_price = ''
                                '''PRODUCT QUANTITY'''
                                product_quantity = 1
                                if product_url in read_log_file():
                                    continue
                                print('current datetime------>', datetime.now())
                                dictionary_5 = get_dictionary(product_category=product_category, product_sub_category='NA', product_ids=product_id, product_names=product_name, product_quantities=product_quantity, product_prices=product_price, product_urls=product_url)
                                articles_df = pd.DataFrame([dictionary_5])
                                articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first', inplace=True)
                                if os.path.isfile(f'{file_name}.csv'):
                                    articles_df.to_csv(f'{file_name}.csv', index=False, header=False, mode='a')
                                else:
                                    articles_df.to_csv(f'{file_name}.csv', index=False)
                                write_visited_log(product_url)
            write_visited_log(main_url)
