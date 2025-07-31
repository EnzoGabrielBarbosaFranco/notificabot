from telethon import TelegramClient, events
import re
import requests
import time
import os

# Credenciais do Telegram API
api_id = 29179368
api_hash = '9b273c6920a8d79747866daeec6920c2'

# Palavras-chave para filtrar mensagens
palavras_chave = [
    's25', 's25 plus', 'buds 2 pro', 'buds 3 pro', 'buds fe',
    'playstation 5', 'ps5', 'mercado livre', 'nintendo switch'
]

# Dados do bot
bot_token = '8331984664:AAGXTs_Gzw_jGzGAt5HCFYj47kwcTNqyFPo'
chat_id = 621838467  # Seu ID pessoal

# Armazena links já notificados
mensagens_enviadas = set()

# Controle de taxa de envio
ultimo_envio = 0
intervalo_minimo = 2  # segundos

# Cria o cliente do Telethon
client = TelegramClient('sessao_enzo', api_id, api_hash)

def formatar_texto(texto):
    texto = re.sub(r'\br\$', 'R$', texto)
    texto = re.sub(r'\bde\b', 'De', texto)
    texto = re.sub(r'\bpor\b', 'Por', texto)
    return texto

def enviar_para_bot(mensagem, imagem_path=None):
    global ultimo_envio

    agora = time.time()
    if agora - ultimo_envio < intervalo_minimo:
        print('⏳ Aguardando intervalo mínimo...')
        return

    if imagem_path:
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        with open(imagem_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': mensagem,
                'parse_mode': 'Markdown'
            }
            resposta = requests.post(url, data=data, files=files)
    else:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': mensagem,
            'parse_mode': 'Markdown'
        }
        resposta = requests.post(url, data=data)

    if resposta.status_code == 200:
        ultimo_envio = agora
        print('✅ Mensagem enviada com sucesso!')
    else:
        print(f'Erro ao enviar mensagem: {resposta.text}')

@client.on(events.NewMessage)
async def handler(event):
    # Ignora mensagens enviadas pelo próprio bot
    if event.message.sender_id == (await client.get_me()).id:
        return

    texto_original = (event.message.message or "").strip()
    texto_tratado = texto_original.lower()

    if not texto_tratado:
        return

    # Verifica se contém uma das palavras-chave
    if not any(re.search(rf'\b{re.escape(palavra)}\b', texto_tratado) for palavra in palavras_chave):
        return

    # Extrai link principal para controle de duplicação
    link_match = re.search(r'(https?://[^\s]+)', texto_tratado)
    link = link_match.group(1) if link_match else texto_tratado

    if link in mensagens_enviadas:
        print('🔁 Link já enviado, ignorando...')
        return

    mensagens_enviadas.add(link)

    # Formata texto
    texto_formatado = formatar_texto(texto_original)
    mensagem_formatada = (
        "🚨 *Promoção Detectada!* 🚨\n\n"
        f"{texto_formatado}"
    )

    print(f'[🔔 ALERTA] Palavra-chave detectada: {texto_formatado[:60]}...')

    imagem_path = None
    if event.message.photo:
        try:
            imagem_path = await client.download_media(event.message.photo, file='imagem_temp.jpg')
        except Exception as e:
            print(f'⚠️ Erro ao baixar imagem: {e}')
            imagem_path = None

    enviar_para_bot(mensagem_formatada, imagem_path)

    if imagem_path and os.path.exists(imagem_path):
        os.remove(imagem_path)

# Inicia o cliente
client.start()
print('✅ Bot rodando e enviando pelo @NotificacaoPeloBot...')
client.run_until_disconnected()
