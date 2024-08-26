import requests
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class Downloader:
    cliente_http = requests.Session()
    total_pastas_processadas = 0

    @classmethod
    def processar_arquivos_de_produto(cls, diretorio_produto):
        print(f"Processando arquivos de produto em {diretorio_produto}")
        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                for arquivo_produto in diretorio_produto.glob('product_*.json'):
                    print(f"Processando arquivo de produto: {arquivo_produto.name}")
                    executor.submit(cls.processar_produto, arquivo_produto)
        except Exception as e:
            print(f"Erro ao processar arquivos de produto em {diretorio_produto}: {e}")
        finally:
            cls.total_pastas_processadas += 1
            print(f"Finalizado o processamento da pasta: {diretorio_produto.name} (Total de pastas processadas: {cls.total_pastas_processadas})")

    @classmethod
    def processar_produto(cls, arquivo_produto):
        try:
            with arquivo_produto.open('r', encoding='utf-8-sig') as f:
                dados_produto = json.load(f)
                dados_galeria = dados_produto.get('attributes', {}).get('gallery', {}).get('data', [])

                for item in dados_galeria:
                    if 'attributes' in item and 'url' in item['attributes']:
                        url_arquivo = item['attributes']['url']
                        destino = arquivo_produto.parent / (item['id'] + cls.pegar_extensao(url_arquivo))

                        # Verificar se o arquivo já existe antes de baixar
                        if not destino.exists():
                            cls.baixar_arquivo(url_arquivo, destino)
                        else:
                            print(f"O arquivo {destino.name} já existe. Pulando o download.")
        except json.JSONDecodeError as json_error:
            print(f"Erro ao decodificar JSON no arquivo {arquivo_produto.name}: {json_error}")
        except Exception as e:
            print(f"Erro ao processar arquivo de produto {arquivo_produto.name}: {e}")

    @classmethod
    def processar_arquivos_de_arquivo(cls, diretorio_produto):
        print(f"Processando arquivos de arquivo em {diretorio_produto}")
        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                for arquivo_arquivo in diretorio_produto.glob('file_*.json'):
                    print(f"Processando arquivo: {arquivo_arquivo.name}")
                    executor.submit(cls.processar_arquivo, arquivo_arquivo)
        except Exception as e:
            print(f"Erro ao processar arquivos de arquivo em {diretorio_produto}: {e}")
        finally:
            cls.total_pastas_processadas += 1
            print(f"Finalizado o processamento da pasta: {diretorio_produto.name} (Total de pastas processadas: {cls.total_pastas_processadas})")

    @classmethod
    def processar_arquivo(cls, arquivo_arquivo):
        try:
            with arquivo_arquivo.open('r', encoding='utf-8-sig') as f:
                dados_arquivo = json.load(f)
                url_arquivo = dados_arquivo.get('url', '')
                if url_arquivo:
                    destino = arquivo_arquivo.parent / dados_arquivo['name']

                    # Verificar se o arquivo já existe antes de baixar
                    if not destino.exists():
                        cls.baixar_arquivo(url_arquivo, destino)
                    else:
                        print(f"O arquivo {destino.name} já existe. Pulando o download.")
        except json.JSONDecodeError as json_error:
            print(f"Erro ao decodificar JSON no arquivo {arquivo_arquivo.name}: {json_error}")
        except Exception as e:
            print(f"Erro ao processar arquivo {arquivo_arquivo.name}: {e}")

    @staticmethod
    def baixar_arquivo(url_arquivo, arquivo_destino):
        print(f"Baixando arquivo da URL: {url_arquivo}")
        try:
            with Downloader.cliente_http.get(url_arquivo, stream=True) as resposta:
                resposta.raise_for_status()

                with arquivo_destino.open('wb') as f:
                    for chunk in resposta.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.RequestException as req_error:
            print(f"Erro na solicitação HTTP ao baixar arquivo: {req_error}")
        except Exception as e:
            print(f"Erro ao baixar arquivo: {e}")
        else:
            print(f"Arquivo baixado com sucesso: {arquivo_destino.name}")

    @staticmethod
    def pegar_extensao(nome_arquivo):
        return Path(nome_arquivo).suffix

# Iniciando o processamento do diretório 'stls'
print("Iniciando o processamento do diretório 'stls'...")
try:
    for pasta_produto in Path('stls').iterdir():
        if pasta_produto.is_dir():
            Downloader.processar_arquivos_de_produto(pasta_produto)
            Downloader.processar_arquivos_de_arquivo(pasta_produto)
except Exception as e:
    print(f"Erro ao processar o diretório 'stls': {e}")
finally:
    # Fechando a sessão HTTP
    Downloader.cliente_http.close()

print(f"Processamento completo. Total de pastas processadas: {Downloader.total_pastas_processadas}")
