from typing import Final, Dict
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from dotenv import load_dotenv
import json

with open('data.json', 'r', encoding='utf-8') as f:
    furia_data = json.load(f)

import os

load_dotenv()

TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = '@teste_furia_bot'

# Estados da conversa
NAME, ADDRESS, CPF = range(3)

# Banco de dados temporário em memória
users_db: Dict[int, Dict[str, str]] = {}

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    
    if user_id in users_db:
        await update.message.reply_text("Você já está registrado!")
        return ConversationHandler.END
    
    await update.message.reply_text("👋 Bem-vindo ao cadastro! Por favor, digite seu NOME COMPLETO:")
    return NAME

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in users_db:
        await update.message.reply_text("⚠️ Você precisa se registrar primeiro usando /start")
        return
    
    help_text = """
🎮 *FURIA CS:GO BOT* 🎮

Este é o bot oficial da FURIA Esports para acompanhar tudo sobre o time de Counter-Strike! 

📌 *COMANDOS DISPONÍVEIS*:

/start - Inicia o bot e faz seu cadastro (obrigatório)
/help - Mostra esta mensagem de ajuda
/elenco - Mostra o elenco completo de jogadores e staff
/partidas - Exibe os resultados das últimas 5 partidas
/proximas - Lista as próximas partidas agendadas
/torneios - Mostra os próximos torneios do time
/custom - Comando personalizado (em desenvolvimento)

⚡ *Como usar*:
1. Primeiro execute /start para se registrar
2. Depois use qualquer comando acima para obter informações

🔍 *Fonte dos dados*: 
Todos os dados são coletados do HLTV.org e atualizados regularmente

💛 *Siga a FURIA*:
Twitter: @FURIA
Site: furia.gg
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def roster_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in users_db:
        await update.message.reply_text("⚠️ Você precisa se registrar primeiro usando /start")
        return

    roster = furia_data['roster']
    response = "🏆 **ELENCO DA FURIA** 🏆\n\n"
    
    for member in roster:
        if member['role'] == 'coach':
            response += f"👔 **{member['name'].upper()}** (Treinador)\n"
        else:
            status = "⛔ Reserva" if member.get('status') == 'BENCHED' else "✅ Titular"
            response += f"🎮 {member['name']} - {status}\n"
    
    await update.message.reply_text(response)

async def recent_matches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in users_db:
        await update.message.reply_text("⚠️ Você precisa se registrar primeiro usando /start")
        return

    matches = furia_data['recent_matches'][:5]  # Mostrar 5 últimas
    response = "🔥 **ÚLTIMAS PARTIDAS** 🔥\n\n"
    
    for match in matches:
        result = "✅ VITÓRIA" if match['score1'] > match['score2'] else "❌ DERROTA"
        response += (
            f"📅 {match['date']}\n"
            f"{match['team1']} {match['score1']} x {match['score2']} {match['team2']}\n"
            f"{result}\n\n"
        )
    
    await update.message.reply_text(response)

async def upcoming_matches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in users_db:
        await update.message.reply_text("⚠️ Você precisa se registrar primeiro usando /start")
        return

    matches = furia_data['upcoming_matches']
    response = "🕒 **PRÓXIMAS PARTIDAS** 🕒\n\n"
    
    for match in matches:
        response += (
            f"📅 {match['date']}\n"
            f"⚔ {match['team1']} vs {match['team2']}\n\n"
        )
    
    await update.message.reply_text(response)

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in users_db:
        await update.message.reply_text("⚠️ Você precisa se registrar primeiro usando /start")
        return

    events = furia_data['events']
    response = "🏟️ **PRÓXIMOS TORNEIOS** 🏟️\n\n"
    
    for event in events:
        response += (
            f"🏆 **{event['name']}**\n"
            f"📅 {event['start_date']} - {event['end_date']}\n\n"
        )
    
    await update.message.reply_text(response)

# Handlers do cadastro
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    users_db[user_id] = {"name": update.message.text}
    await update.message.reply_text("📌 Agora digite seu ENDEREÇO COMPLETO:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    users_db[user_id]["address"] = update.message.text
    await update.message.reply_text("🔢 Por favor, digite seu CPF (apenas números):")
    return CPF

async def get_cpf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    cpf = update.message.text
    
    if not cpf.isdigit() or len(cpf) != 11:
        await update.message.reply_text("❌ CPF inválido! Digite 11 números sem pontuação:")
        return CPF
    
    users_db[user_id]["cpf"] = cpf
    await update.message.reply_text("✅ Cadastro concluído! Agora você pode usar todos os comandos.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id in users_db:
        del users_db[user_id]
    await update.message.reply_text("❌ Cadastro cancelado")
    return ConversationHandler.END

# Responses
def handle_response(text: str) -> str:
    if 'teste' in text.lower():
        return 'TESTANDO'
    return "Comando não reconhecido"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in users_db:
        await update.message.reply_text("⚠️ Você precisa se registrar primeiro usando /start")
        return

    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User {user_id} in {message_type}: {text}')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print('BOT:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused by {context.error}')

if __name__ == '__main__':
    print('Starting Bot')
    app = Application.builder().token(TOKEN).build()

    # Conversation Handler para cadastro
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            CPF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cpf)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Comandos
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('elenco', roster_command))
    app.add_handler(CommandHandler('partidas', recent_matches_command))
    app.add_handler(CommandHandler('proximas', upcoming_matches_command))
    app.add_handler(CommandHandler('torneios', events_command))

    # Mensagens
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)