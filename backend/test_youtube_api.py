import aiohttp
import asyncio

async def test_youtube_api(api_key: str, channel_url: str):
    """
    Testa a API do YouTube fazendo uma requisição simples.
    """
    # Extrai o ID do canal da URL
    channel_id = None
    if "youtube.com/channel/" in channel_url:
        channel_id = channel_url.split("youtube.com/channel/")[1].split("/")[0]
    elif "youtube.com/@" in channel_url:
        handle = channel_url.split("youtube.com/@")[1].split("/")[0]
        # Primeiro busca o ID do canal usando o handle
        async with aiohttp.ClientSession() as session:
            params = {
                "part": "id",
                "q": handle,
                "type": "channel",
                "key": api_key
            }
            async with session.get("https://www.googleapis.com/youtube/v3/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("items"):
                        channel_id = data["items"][0]["id"]["channelId"]
                else:
                    error_data = await response.json()
                    print(f"Erro ao buscar canal: {error_data}")
                    return

    if not channel_id:
        print("Não foi possível extrair o ID do canal da URL")
        return

    # Testa obtendo informações do canal
    async with aiohttp.ClientSession() as session:
        params = {
            "part": "snippet,statistics",
            "id": channel_id,
            "key": api_key
        }
        async with session.get("https://www.googleapis.com/youtube/v3/channels", params=params) as response:
            print(f"Status da resposta: {response.status}")
            data = await response.json()
            
            if response.status == 200:
                if data.get("items"):
                    channel = data["items"][0]
                    print("\nInformações do canal:")
                    print(f"Título: {channel['snippet']['title']}")
                    print(f"Inscritos: {channel['statistics'].get('subscriberCount', 'N/A')}")
                    print(f"Total de vídeos: {channel['statistics'].get('videoCount', 'N/A')}")
                else:
                    print("Canal não encontrado")
            else:
                print("\nErro na resposta:")
                print(data)

# Execute o teste
if __name__ == "__main__":
    # Substitua com sua chave da API e URL do canal
    API_KEY = input("Digite sua chave da API do YouTube: ")
    CHANNEL_URL = input("Digite a URL do canal do YouTube: ")
    
    asyncio.run(test_youtube_api(API_KEY, CHANNEL_URL)) 