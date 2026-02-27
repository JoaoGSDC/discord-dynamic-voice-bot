# 🎙 Bot de Salas de Voz Dinâmicas

Um bot para Discord que permite que qualquer usuário crie automaticamente uma sala de voz temporária ao entrar em um canal específico.

## 📋 O que é o projeto

Este bot cria **salas de voz dinâmicas** no seu servidor Discord. Quando um usuário entra no canal **➕ Criar Sala**, o bot:

1. Cria automaticamente uma nova sala chamada **🎮 Sala do [nome do usuário]**
2. Move o usuário para essa sala
3. Dá permissões de administrador da sala ao criador (mutar, ensurdecer, gerenciar)
4. Remove a sala automaticamente quando ela fica vazia

## 🚀 Como instalar

### Pré-requisitos

- Python 3.8 ou superior
- Conta no Discord

### Passo a passo

1. **Clone ou baixe o projeto**

```bash
cd discord-dynamic-voice-bot
```

2. **Crie um ambiente virtual (recomendado)**

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# ou: source venv/bin/activate   # Linux/Mac
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure o token**

Crie um arquivo `.env` na raiz do projeto com o conteúdo:

```
DISCORD_TOKEN=seu_token_aqui
```

Se existir o arquivo `env.example`, copie-o para `.env`:

```bash
copy env.example .env   # Windows
# ou: cp env.example .env   # Linux/Mac
```

Depois edite o `.env` e substitua `seu_token_aqui` pelo token real do seu bot.

## ▶️ Como executar

```bash
python main.py
```

Alternativamente, você pode usar:

```bash
python -m src.bot
```

Se tudo estiver correto, você verá no console:

```
Bot conectado como NomeDoBot#1234 (ID: 123456789)
Conectado em 1 servidor(es)
Task de limpeza preventiva iniciada (intervalo: 1 hora)
```

## 🔧 Como criar o bot no Discord Developer Portal

1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em **"New Application"** e dê um nome ao seu bot
3. No menu lateral, clique em **"Bot"**
4. Clique em **"Add Bot"**
5. Em **"Token"**, clique em **"Reset Token"** ou **"Copy"** para obter o token
6. **Importante:** Ative as opções em **Privileged Gateway Intents**:
   - **SERVER MEMBERS INTENT** (necessário para voice_states)
   - **MESSAGE CONTENT INTENT** (opcional, mas recomendado)

7. Para convidar o bot ao servidor:
   - Vá em **"OAuth2"** → **"URL Generator"**
   - Em **Scopes**, marque **"bot"**
   - Em **Bot Permissions**, marque:
     - View Channels
     - Connect (voice)
     - Move Members
     - Manage Channels
     - Mute Members
     - Deafen Members
   - Copie a URL gerada e abra no navegador para adicionar o bot

## 📁 Estrutura esperada no servidor

O bot trabalha com a seguinte estrutura:

| Elemento | Nome |
|----------|------|
| **Categoria** | 🎙 VOZ |
| **Canal gatilho** | ➕ Criar Sala |

### Configuração manual

1. Crie uma categoria chamada **🎙 VOZ** no seu servidor
2. O bot criará automaticamente o canal **➕ Criar Sala** dentro dela (se não existir)

Se a categoria não existir, o bot apenas registrará um aviso no console e continuará funcionando.

## ✨ Funcionalidades

- **Criação automática:** Ao entrar em ➕ Criar Sala, uma nova sala é criada com o nome do usuário
- **Permissões:** O dono da sala pode gerenciar o canal, mutar e ensurdecer membros
- **Remoção automática:** Salas vazias são deletadas após ~1 segundo
- **Limpeza preventiva:** A cada 1 hora, o bot remove salas vazias com mais de 24h de existência
- **Logs informativos:** Todas as ações são registradas no console

## 📂 Estrutura do projeto

```
discord-dynamic-voice-bot/
├── main.py
├── src/
│   ├── __init__.py
│   ├── bot.py
│   ├── dynamic_voice.py
│   └── config.py
├── requirements.txt
├── README.md
├── env.example
└── .gitignore
```

## ⚠️ Solução de problemas

**Bot não conecta:**
- Verifique se o token está correto no `.env`
- Confirme que o bot foi adicionado ao servidor com as permissões necessárias

**Canal não é criado:**
- Certifique-se de que a categoria **🎙 VOZ** existe
- O bot precisa da permissão "Manage Channels"

**Usuário não é movido:**
- O bot precisa da permissão "Move Members"

## 📄 Licença

Projeto educacional - livre para uso e modificação.
