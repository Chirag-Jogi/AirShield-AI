import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

# Project tools
from src.data.cities import INDIAN_CITIES
from src.database.queries import get_or_create_user, update_user_city
from src.agent.advisor import AirShieldAgent

logger = logging.getLogger(__name__)

def validate_city(city_text: str):
    """Check if the provided text matches one of our known Indian cities."""
    search_term = city_text.strip().lower()
    for city in INDIAN_CITIES:
        if city.name.lower() == search_term:
            return city.name
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome user and handle onboarding."""
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    profile = get_or_create_user(user_id, first_name)
    
    if 'history' not in context.user_data:
        context.user_data['history'] = []

    if not profile.home_city:
        welcome_text = (
            f"Hi {first_name}! 🌟 Welcome to AirShield AI.\n\n"
            "My mission is to keep your lungs safe and help you breathe easy every day. 🌬️🛡️\n\n"
            "To get started, **which city should I keep an eye on for you?** 🏙️\n"
            "(e.g., Mumbai, Delhi, Pune, Bangalore...)"
        )
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
        context.user_data['waiting_for_city'] = True
    else:
        welcome_text = (
            f"Welcome back, {first_name}! 🤗 Great to see you again.\n\n"
            f"I'm currently protecting you in **{profile.home_city}**. 🛡️\n\n"
            "What can I do for you today? Ask me anything!"
        )
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages (onboarding or general chat)."""
    text = update.message.text
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    # --- ONBOARDING FLOW (City Validation) ---
    if context.user_data.get('waiting_for_city'):
        validated_city = validate_city(text)
        if validated_city:
            update_user_city(user_id, validated_city)
            context.user_data['waiting_for_city'] = False
            context.user_data['current_context_city'] = validated_city
            
            success_message = (
                f"Got it! 🏠 From now on, I've got your back in **{validated_city}**.\n\n"
                "Whenever there's a spike in pollution or a clear sky ahead, I'll be here. 🛡️🌟\n"
                "Try asking: *'Can I go for a run today?'*"
            )
            await update.message.reply_text(success_message, parse_mode="Markdown")
        else:
            options = ", ".join([c.name for c in INDIAN_CITIES[:5]]) + "..."
            error_message = (
                "🏙️ Hmm, I don't recognize that city yet! \n\n"
                f"Please tell me which major city you are in (e.g., **{options}**). "
                "I'm adding more cities soon!"
            )
            await update.message.reply_text(error_message, parse_mode="Markdown")
        return

    # --- GENERAL CHAT FLOW ---
    profile = get_or_create_user(user_id, first_name)
    target_city = None

    # Determine which city we are talking about
    for city in INDIAN_CITIES:
        if city.name.lower() in text.lower():
            target_city = city.name
            break
    
    if any(k in text.lower() for k in ["my city", "home", "mine"]):
        target_city = profile.home_city

    if not target_city:
        target_city = context.user_data.get('current_context_city', profile.home_city)

    # Show "Typing..." while processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.user_data['current_context_city'] = target_city 

    # Management of Chat History
    if 'history' not in context.user_data:
        context.user_data['history'] = []
    
    context.user_data['history'].append({"role": "user", "content": text})
    if len(context.user_data['history']) > 10:
        context.user_data['history'].pop(0)

    # --- ASYNC AGENT CALL ---
    agent = AirShieldAgent(target_city, home_city=profile.home_city)
    response = await agent.ask(text, history=context.user_data['history'][:-1]) 
    
    context.user_data['history'].append({"role": "assistant", "content": response})

    # Keyboard for Home City Swap
    keyboard = []
    if target_city != profile.home_city:
        keyboard = [[InlineKeyboardButton(f"🏠 Make {target_city} my Home", callback_data=f"set_{target_city}")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks for setting home city."""
    query = update.callback_query
    await query.answer()
    
    new_city = query.data.replace("set_", "")
    update_user_city(update.effective_user.id, new_city)
    
    # Update the message to remove the button
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"✅ Perfect! I'm now protecting you in **{new_city}**! 🛡️"
    )
