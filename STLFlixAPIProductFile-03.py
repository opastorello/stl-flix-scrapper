import json
import os
import requests

# Função para enviar solicitação HTTP e obter dados do arquivo do produto
def obter_dados_arquivo_produto(fid):
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI5IkpXVCJ9.eyJpZCI6MzExNzYsImlhdCI6MTcwMjE1Mzc4OCwiZShwIjoxNzA0NzQ1Nzg4fQ.KGh1uOWfgSLW_F7ySceWk7oy72dOGUlfsWhLbL2MxKg"
    json_payload = json.dumps({
        "jwt": jwt_token,
        "fid": fid,
        "uid": 31176
    })

    headers = {
        "authority": "lb.stlflix.com",
        "accept": "*/*",
        "accept-language": "es-419,es;q=0.9",
        "authorization": f"Bearer {jwt_token}",
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

    url = "https://lb.stlflix.com/api/product/product-file"
    print(f"Enviando solicitação para fid: {fid}")
    resposta = requests.post(url, headers=headers, data=json_payload)
    print(f"Resposta recebida para fid: {fid}")
    return resposta.text

# Substitua pelo caminho real para o seu arquivo de configuração
caminho_arquivo_configuracao = "lista-completa-de-produtos.json"
caminho_destino = "stls"

print(f"Lendo o arquivo de configuração: {caminho_arquivo_configuracao}")

# Leia o arquivo de configuração
with open(caminho_arquivo_configuracao, "r") as arquivo:
    for linha in arquivo:
        dados_json = json.loads(linha)

        try:
            # Extraia o slug e o fid
            slug = dados_json["attributes"]["slug"]
            fids = [arquivo["file"]["data"]["id"] for arquivo in dados_json["attributes"]["files"] if arquivo["file"]["data"]["id"] is not None]

            print(f"Processando slug: {slug} com fids: {fids}")

            # Crie o diretório para o slug
            caminho_dir = os.path.join(caminho_destino, slug)
            os.makedirs(caminho_dir, exist_ok=True)

            # Salve o objeto JSON original
            caminho_arquivo_produto = os.path.join(caminho_dir, f"product_{slug}.json")
            print(f"Salvando dados originais do produto em: {caminho_arquivo_produto}")
            with open(caminho_arquivo_produto, "w") as arquivo_produto:
                arquivo_produto.write(linha)

            # Para cada fid, obtenha os dados do arquivo e salve-os
            for fid in fids:
                print(f"Obtendo dados para fid: {fid}")
                dados_arquivo = obter_dados_arquivo_produto(fid)
                caminho_arquivo_fid = os.path.join(caminho_dir, f"file_{fid}.json")
                print(f"Salvando dados do arquivo em: {caminho_arquivo_fid}")
                with open(caminho_arquivo_fid, "w") as arquivo_fid:
                    arquivo_fid.write(dados_arquivo)
        except:
            pass

print("Processamento concluído.")
