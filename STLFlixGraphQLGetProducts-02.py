import json
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Define sua consulta GraphQL aqui como uma string de várias linhas
def get_graphql_query():
    return '''
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

        fragment CommentFragment on Comment {
          users_permissions_user {
            data {
              attributes {
                username
                __typename
              }
              __typename
            }
            __typename
          }
          text
          createdAt
          __typename
        }

        fragment ProductComments on Product {
          comments(pagination: { pageSize: 50 }, sort: "createdAt:asc") {
            data {
              attributes {
                ...CommentFragment
                reply_comments {
                  data {
                    attributes {
                      ...CommentFragment
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
          __typename
        }

        fragment seoData on ComponentSharedSeo {
          metaTitle
          metaDescription
          metaImage {
            ...mediaData
            __typename
          }
          metaSocial {
            socialNetwork
            title
            description
            image {
              ...mediaData
              __typename
            }
            __typename
          }
          keywords
          metaRobots
          structuredData
          metaViewport
          canonicalURL
          __typename
        }

        query GET_PRODUCTS($slug: String) {
          products(filters: { slug: { eq: $slug } }) {
            data {
              __typename
              id
              attributes {
                name
                slug
                description
                iframe
                updatedAt
                bambu_file {
                  data {
                    id
                    __typename
                  }
                  __typename
                }
                stl_preview {
                  ...mediaData
                  __typename
                }
                release_date
                ...ProductComments
                thumbnail {
                  ...mediaData
                  __typename
                }
                hover {
                  ...mediaData
                  __typename
                }
                gallery(pagination: { pageSize: 50 }) {
                  data {
                    id
                    attributes {
                      alternativeText
                      url
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                keywords
                files(pagination: { pageSize: 50 }) {
                  text
                  commercial_only
                  file {
                    data {
                      id
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                categories {
                  data {
                    id
                    attributes {
                      name
                      slug
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                tags {
                  data {
                    attributes {
                      name
                      parent_tag {
                        data {
                          attributes {
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
                related_products {
                  data {
                    id
                    attributes {
                      ...productsData
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                products_related {
                  data {
                    id
                    attributes {
                      ...productsData
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                seo {
                  ...seoData
                  __typename
                }
                __typename
              }
            }
            __typename
          }
        }

        fragment productsData on Product {
          name
          slug
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
          thumbnail {
            ...mediaData
            __typename
          }
          hover {
            ...mediaData
            __typename
          }
          __typename
        }

   '''

# Função para ler slugs de um arquivo e retornar como uma lista
def read_slugs_from_file(file_path):
    slugs = []

    if not os.path.exists(file_path):
        print(f"O arquivo não existe: {file_path}")
        return slugs

    with open(file_path, "r") as file:
        for line in file:
            try:
                json_data = json.loads(line)
                slug = json_data["attributes"]["slug"]
                slugs.append(slug)
            except Exception as e:
                print(f"Erro ao analisar linha para JSON: {line}")
                print(f"Exceção: {str(e)}")

    return slugs

# Função para fazer uma consulta GraphQL e retornar a resposta
def fetch_graphql_data(http_client, slug, token, max_retries):
    print(f"Obtendo dados para slug: {slug}")
    media_type = "application/json"
    content = {
        "operationName": "GET_PRODUCTS",
        "variables": {"slug": slug},
        "query": get_graphql_query()
    }

    headers = {
        "authority": "lb.stlflix.com",
        "accept": "*/*",
        "accept-language": "es-419,es;q=0.9",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "origin": "https://platform.stlflix.com",
        "referer": "https://platform.stlflix.com/",
        "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    url = "https://lb.stlflix.com/graphql"
    response = None
    attempt = 0

    while attempt < max_retries:
        try:
            #print(f"Tentativa {attempt} para slug: {slug}")
            response = http_client.post(url, json=content, headers=headers)
            print(f"Dados obtidos com sucesso para slug: {slug}")
            break  # Interrompe o loop se bem-sucedido
        except requests.exceptions.RequestException as e:
            print(f"Timeout ocorreu para slug: {slug} na tentativa {attempt}")
            attempt += 1
            if attempt >= max_retries:
                print(f"Máximo de tentativas atingido para slug: {slug}")
                raise e  # Rethrow exceção se máximo de tentativas atingido

    return response.json()

# Função para escrever dados em arquivo
def write_data_to_file(data, file_path):
    with open(file_path, "a") as file:
        json.dump(data, file)
        file.write('\n')  # Adiciona uma quebra de linha para separar os dumps

# Função de execução principal
def main(config_file_path, output_file_path, token, max_retries):
    print("Iniciando execução principal")
    http_client = requests.Session()
    retries = Retry(total=max_retries, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    http_client.mount("https://", HTTPAdapter(max_retries=retries))
    slugs = read_slugs_from_file(config_file_path)

    for slug in slugs:

        try:
            response = fetch_graphql_data(http_client, slug, token, max_retries)
            products_data = response.get('data', {}).get('products', {}).get('data', [])
            if products_data:
                print(f"Dados encontrados para slug: {slug}")
                write_data_to_file(response["data"]["products"]["data"][0], output_file_path)
            else:
                print(f"Nenhum dado encontrado para slug: {slug}")

        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")

    print("Execução principal concluída")

# Parâmetros configuráveis
config_file_path = "lista-de-produtos.txt"
output_file_path = "lista-completa-de-produtos.json"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI5IkpXVCJ9.eyJpZCI6MzExNzYsImlhdCI6MTcwMjE1Mzc4OCwiZShwIjoxNzA0NzQ1Nzg4fQ.KGh1uOWfgSLW_F7ySceWk7oy72dOGUlfsWhLbL2MxKg"
max_retries = 3  # Configure o número máximo de tentativas

# Substitua 'caminho_para_arquivo_de_slug.txt' pelo caminho real para o arquivo de slug
# Substitua 'caminho_para_arquivo_de_saida.json' pelo caminho real para o arquivo de saída
# Substitua 'seu_token_bearer_aqui' pelo token de autenticação real
# Configure max_retries para o número de vezes que deseja tentar a solicitação após um timeout

# Execute o script
main(config_file_path, output_file_path, token, max_retries)
