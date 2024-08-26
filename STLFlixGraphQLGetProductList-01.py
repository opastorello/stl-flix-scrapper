import requests
import json

class Config:
    graphql_query = '''
        fragment mediaData on UploadFileEntityResponse {
          data {
            attributes {
              alternativeText
              url
              __typename
            }
            __typename
          }
          __typename
        }

        query GET_LIST_PRODUCTS(
          $filters: ProductFiltersInput
          $productsPage: Int
          $productsPageSize: Int
          $sort: [String]
        ) {
          products(
            filters: $filters
            pagination: { page: $productsPage, pageSize: $productsPageSize }
            sort: $sort
          ) {
            data {
              id
              attributes {
                name
                slug
                thumbnail {
                  ...mediaData
                  __typename
                }
                hover {
                  ...mediaData
                  __typename
                }
                categories {
                  data {
                    id
                    attributes {
                      slug
                      name
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                tags {
                  data {
                    id
                    attributes {
                      slug
                      name
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                __typename
              }
              __typename
            }
            __typename
          }
        }
    '''
    output_file = "lista-de-produtos.txt"
    max_retries = 3
    api_url = 'https://lb.stlflix.com/graphql'

    headers = {
        'authority': 'lb.stlflix.com',
        'accept': '*/*',
        'accept-language': 'es-419,es;q=0.9',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI5IkpXVCJ9.eyJpZCI6MzExNzYsImlhdCI6MTcwMjE1Mzc4OCwiZShwIjoxNzA0NzQ1Nzg4fQ.KGh1uOWfgSLW_F7ySceWk7oy72dOGUlfsWhLbL2MxKg',
        'content-type': 'application/json',
        'origin': 'https://platform.stlflix.com',
        'referer': 'https://platform.stlflix.com/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

class Downloader:
    def save_to_file(product, config):
        json_content = json.dumps(product)  # Serialize the product map to a JSON string
        with open(config.output_file, 'a') as file:
            file.write(json_content + '\n')

    def fetch_products(page, config):
        json_body = json.dumps({
            'operationName': 'GET_LIST_PRODUCTS',
            'variables': {
                'filters': {},
                'productsPage': page,
                'productsPageSize': 100,
                'sort': 'release_date:DESC'
            },
            'query': config.graphql_query
        })

        response = None
        retries = 0

        while retries < config.max_retries:
            try:
                response = requests.post(config.api_url, headers=config.headers, data=json_body)
                response.raise_for_status()
                break  # Sucesso, sair do loop de tentativas
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição: {e}. Tentativa {retries + 1}")
                retries += 1
                if retries == config.max_retries:
                    raise RuntimeError("Número máximo de tentativas alcançado. Abortando.")

        return response.text if response else None
        
def main(config):
    print("Iniciando processo de obtenção de dados...")
    current_page = 1
    has_more_data = True

    while has_more_data:
        print(f"Obtendo dados para a página {current_page}")
        response = Downloader.fetch_products(current_page, config)
        
        if response:
            parsed_response = json.loads(response)
            products = parsed_response.get('data', {}).get('products', {}).get('data', [])

            if products:
                print(f"Processando {len(products)} produtos...")
                for product in products:
                    Downloader.save_to_file(product, config)
                current_page += 1
            else:
                print("Não há mais dados disponíveis.")
                has_more_data = False
        else:
            print("Nenhuma resposta recebida. Interrompendo o processo de obtenção.")
            has_more_data = False

    print("Processo de obtenção de dados finalizado.")

if __name__ == "__main__":
    print("Inicializando configuração...")
    config = Config()
    print("Configuração inicializada. Iniciando método principal.")
    main(config)
    print("Execução do script concluída.")
