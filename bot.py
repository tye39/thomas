import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import os
TOKEN = os.getenv("TOKEN")

users = {}

questions = {
    "maths": {
        "easy": [
            {"q": "2 + 2 = ?", "options": ["3", "4", "5"], "answer": "4"},
            {"q": "5 - 3 = ?", "options": ["1", "2", "3"], "answer": "2"},
            {"q": "10 / 2 = ?", "options": ["2", "5", "10"], "answer": "5"},
            {"q": "3 × 3 = ?", "options": ["6", "9", "12"], "answer": "9"},
            {"q": "7 + 1 = ?", "options": ["6", "8", "9"], "answer": "8"},
        ],
        "medium": [
            {"q": "12 × 3 = ?", "options": ["36", "30", "33"], "answer": "36"},
            {"q": "15 + 27 = ?", "options": ["42", "40", "45"], "answer": "42"},
            {"q": "9 × 8 = ?", "options": ["72", "70", "74"], "answer": "72"},
            {"q": "100 / 4 = ?", "options": ["25", "20", "30"], "answer": "25"},
            {"q": "50 - 18 = ?", "options": ["32", "30", "35"], "answer": "32"},
        ],
        "hard": [
            {"q": "Derivative of x²?", "options": ["2x", "x", "x²"], "answer": "2x"},
            {"q": "√49 = ?", "options": ["6", "7", "8"], "answer": "7"},
            {"q": "5² = ?", "options": ["10", "20", "25"], "answer": "25"},
            {"q": "x² = 16, x = ?", "options": ["4", "-4", "±4"], "answer": "±4"},
            {"q": "Integral of 1 dx?", "options": ["x", "1", "0"], "answer": "x"},
        ],
    },
    "physics": {
        "easy": [
            {"q": "Unit of force?", "options": ["Newton", "Joule", "Watt"], "answer": "Newton"},
            {"q": "Gravity?", "options": ["9.8 m/s²", "10 m/s²", "8 m/s²"], "answer": "9.8 m/s²"},
            {"q": "Unit of energy?", "options": ["Joule", "Newton", "Pascal"], "answer": "Joule"},
            {"q": "Speed unit?", "options": ["m/s", "kg", "N"], "answer": "m/s"},
            {"q": "Light speed?", "options": ["3×10⁸ m/s", "3×10⁶ m/s", "3×10⁵ m/s"], "answer": "3×10⁸ m/s"},
        ],
        "medium": [
            {"q": "Speed formula?", "options": ["d/t", "t/d", "d×t"], "answer": "d/t"},
            {"q": "Work = ?", "options": ["F×d", "m×v", "p×v"], "answer": "F×d"},
            {"q": "Power = ?", "options": ["W/t", "t/W", "W×t"], "answer": "W/t"},
            {"q": "Force = ?", "options": ["m×a", "m/a", "a/m"], "answer": "m×a"},
            {"q": "Energy formula?", "options": ["mgh", "mv", "ma"], "answer": "mgh"},
        ],
        "hard": [
            {"q": "Einstein formula?", "options": ["mc²", "mv", "mgh"], "answer": "mc²"},
            {"q": "Momentum?", "options": ["mv", "m/a", "v/m"], "answer": "mv"},
            {"q": "Voltage unit?", "options": ["Volt", "Ampere", "Ohm"], "answer": "Volt"},
            {"q": "Resistance unit?", "options": ["Ohm", "Volt", "Ampere"], "answer": "Ohm"},
            {"q": "Current unit?", "options": ["Ampere", "Volt", "Ohm"], "answer": "Ampere"},
        ],
    },
    "biology": {
        "easy": [
            {"q": "Blood color?", "options": ["Red", "Blue", "Green"], "answer": "Red"},
            {"q": "Humans breathe?", "options": ["Oxygen", "CO2", "Nitrogen"], "answer": "Oxygen"},
            {"q": "Heart pumps?", "options": ["Blood", "Water", "Air"], "answer": "Blood"},
            {"q": "Plants need?", "options": ["Sunlight", "Milk", "Sand"], "answer": "Sunlight"},
            {"q": "Largest organ?", "options": ["Skin", "Heart", "Brain"], "answer": "Skin"},
        ],
        "medium": [
            {"q": "Powerhouse of cell?", "options": ["Nucleus", "Mitochondria", "Ribosome"], "answer": "Mitochondria"},
            {"q": "DNA location?", "options": ["Nucleus", "Skin", "Blood"], "answer": "Nucleus"},
            {"q": "Photosynthesis uses?", "options": ["CO2", "O2", "H2"], "answer": "CO2"},
            {"q": "Plants release?", "options": ["Oxygen", "CO2", "Nitrogen"], "answer": "Oxygen"},
            {"q": "Brain part?", "options": ["Cerebrum", "Liver", "Kidney"], "answer": "Cerebrum"},
        ],
        "hard": [
            {"q": "DNA stands for?", "options": ["Deoxyribonucleic Acid", "Ribonucleic Acid", "None"], "answer": "Deoxyribonucleic Acid"},
            {"q": "Cell division?", "options": ["Mitosis", "Fusion", "Growth"], "answer": "Mitosis"},
            {"q": "Gene is?", "options": ["DNA unit", "Cell", "Organ"], "answer": "DNA unit"},
            {"q": "Protein made in?", "options": ["Ribosome", "Nucleus", "Heart"], "answer": "Ribosome"},
            {"q": "Blood made in?", "options": ["Bone marrow", "Heart", "Brain"], "answer": "Bone marrow"},
        ],
    },
}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {
        "score": 0,
        "asked": 0,
        "total": 5
    }

    keyboard = [
        [InlineKeyboardButton("Maths", callback_data="maths")],
        [InlineKeyboardButton("Physics", callback_data="physics")],
        [InlineKeyboardButton("Biology", callback_data="biology")],
    ]

    await update.message.reply_text(
        "📚 Choose a subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# SUBJECT
async def subject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in users:
        await query.edit_message_text("⚠️ Please type /start first.")
        return

    users[query.from_user.id]["subject"] = query.data

    keyboard = [
        [InlineKeyboardButton("Easy", callback_data="easy")],
        [InlineKeyboardButton("Medium", callback_data="medium")],
        [InlineKeyboardButton("Hard", callback_data="hard")],
    ]

    await query.edit_message_text(
        "🎯 Choose difficulty:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# DIFFICULTY
async def difficulty_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in users:
        await query.edit_message_text("⚠️ Please type /start first.")
        return

    users[query.from_user.id]["difficulty"] = query.data
    users[query.from_user.id]["asked"] = 0
    users[query.from_user.id]["score"] = 0

    await send_question(query, query.from_user.id)

# SEND QUESTION
async def send_question(query, user_id):
    user = users.get(user_id)

    if not user:
        return

    if user["asked"] >= user["total"]:
        await show_result(query, user_id)
        return

    q = random.choice(questions[user["subject"]][user["difficulty"]])
    user["current"] = q
    user["asked"] += 1

    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in q["options"]]

    await query.edit_message_text(
        f"Q{user['asked']}/5\n❓ {q['q']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ANSWER
async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = users.get(query.from_user.id)

    if not user:
        await query.edit_message_text("⚠️ Please type /start first.")
        return

    correct = user["current"]["answer"]

    if query.data == correct:
        user["score"] += 1
        text = f"✅ Correct!\nAnswer: {correct}"
    else:
        text = f"❌ Wrong!\nCorrect Answer: {correct}"

    await query.edit_message_text(text)

    await asyncio.sleep(1.5)

    await send_question(query, query.from_user.id)

# RESULT ANALYSIS
async def show_result(query, user_id):
    user = users[user_id]
    score = user["score"]

    if score == 5:
        level = "🔥 Excellent"
    elif score >= 3:
        level = "👍 Good"
    else:
        level = "📚 Needs Improvement"

    await query.edit_message_text(
        f"🎉 Quiz Finished!\n\n"
        f"Score: {score}/5\n"
        f"Performance: {level}"
    )

# APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(subject_handler, pattern="^(maths|physics|biology)$"))
app.add_handler(CallbackQueryHandler(difficulty_handler, pattern="^(easy|medium|hard)$"))
app.add_handler(CallbackQueryHandler(answer_handler))

print("Bot running...")
app.run_polling()
