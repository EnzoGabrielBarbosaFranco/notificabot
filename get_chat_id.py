import requests

# Seu token do Bot (não compartilhe com ninguém!)
TOKEN = '8331984664:AAGXTs_Gzw_jGzGAt5HCFYj47kwcTNqyFPo'

# Faz requisição para pegar as atualizações
url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'

resposta = requests.get(url)
dados = resposta.json()

# Mostra a estrutura (vai incluir seu chat_id)
print(dados)
