from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random

TOKEN = "8783602062:AAHAYVlSEnEMIzuPDD67PAwQ-OqGLdcrwx4"

users = {}

# Questions
questions = {
    "maths": {
        "easy": [
            {"q": "2+2=?", "opts": ["2","4","6"], "ans": "4"},
            {"q": "3+1=?", "opts": ["4","5","6"], "ans": "4"},
            {"q": "5-2=?", "opts": ["2","3","4"], "ans": "3"},
            {"q": "10/2=?", "opts": ["5","2","10"], "ans": "5"},
            {"q": "6+1=?", "opts": ["7","8","9"], "ans": "7"},
        ],
        "medium": [
            {"q": "5×6=?", "opts": ["30","20","25"], "ans": "30"},
            {"q": "12÷3=?", "opts": ["4","3","6"], "ans": "4"},
            {"q": "9×3=?", "opts": ["27","18","21"], "ans": "27"},
            {"q": "15-7=?", "opts": ["8","6","7"], "ans": "8"},
            {"q": "8×4=?", "opts": ["32","24","28"], "ans": "32"},
        ]
    },
    "chemistry": {
        "easy": [
            {"q": "H2O is?", "opts": ["Water","Oxygen","Hydrogen"], "ans": "Water"},
            {"q": "O2 is?", "opts": ["Oxygen","Hydrogen","Water"], "ans": "Oxygen"},
            {"q": "NaCl is?", "opts": ["Salt","Sugar","Water"], "ans": "Salt"},
            {"q": "CO2 is?", "opts": ["Carbon dioxide","Oxygen","Nitrogen"], "ans": "Carbon dioxide"},
            {"q": "H is?", "opts": ["Hydrogen","Helium","Oxygen"], "ans": "Hydrogen"},
        ],
        "medium": [
            {"q": "Atomic number of C?", "opts": ["6","8","12"], "ans": "6"},
            {"q": "Atomic number of O?", "opts": ["8","6","10"], "ans": "8"},
            {"q": "pH < 7 means?", "opts": ["Acid","Base","Neutral"], "ans": "Acid"},
            {"q": "Na is?", "opts": ["Sodium","Nitrogen","Neon"], "ans": "Sodium"},
            {"q": "HCl is?", "opts": ["Acid","Base","Salt"], "ans": "Acid"},
        ]
    },
    "biology": {
        "easy": [
            {"q": "Heart pumps?", "opts": ["Blood","Air","Water"], "ans": "Blood"},
            {"q": "We breathe?", "opts": ["Oxygen","Carbon","Water"], "ans": "Oxygen"},
            {"q": "Brain controls?", "opts": ["Body","Food","Water"], "ans": "Body"},
            {"q": "Plants need?", "opts": ["Sunlight","Plastic","Metal"], "ans": "Sunlight"},
            {"q": "Eye is for?", "opts": ["Seeing","Hearing","Eating"], "ans": "Seeing"},
        ],
        "medium": [
            {"q": "Cell is?", "opts": ["Basic unit","Organ","Tissue"], "ans": "Basic unit"},
            {"q": "DNA carries?", "opts": ["Genetic info","Water","Energy"], "ans": "Genetic info"},
            {"q": "Lungs help?", "opts": ["Breathing","Eating","Walking"], "ans": "Breathing"},
            {"q": "Blood carries?", "opts": ["Oxygen","Plastic","Stone"], "ans": "Oxygen"},
            {"q": "Skeleton gives?", "opts": ["Support","Food","Air"], "ans": "Support"},
        ]
    }
}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Maths", callback_data="sub_maths")],
        [InlineKeyboardButton("Chemistry", callback_data="sub_chemistry")],
        [InlineKeyboardButton("Biology", callback_data="sub_biology")]
    ]
    await update.message.reply_text("Choose subject:", reply_markup=InlineKeyboardMarkup(keyboard))


# SUBJECT HANDLER
async def subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subject = query.data.split("_")[1]

    users[query.from_user.id] = {
        "subject": subject,
        "score": 0,
        "wrong": 0,
        "index": 0
    }

    keyboard = [
        [InlineKeyboardButton("Easy", callback_data="diff_easy")],
        [InlineKeyboardButton("Medium", callback_data="diff_medium")]
    ]

    await query.edit_message_text("Choose difficulty:", reply_markup=InlineKeyboardMarkup(keyboard))


# DIFFICULTY HANDLER
async def difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    difficulty = query.data.split("_")[1]
    user = users[query.from_user.id]

    user["questions"] = random.sample(
        questions[user["subject"]][difficulty], 5
    )

    await send_question(update, context)


# SEND QUESTION
async def send_question(update, context):
    user = users[update.effective_user.id]

    if user["index"] >= 5:
        total = user["score"] + user["wrong"]
        percent = (user["score"] / total) * 100

        await update.effective_chat.send_message(
            f"🎯 Quiz Finished!\n\n"
            f"✅ Correct: {user['score']}\n"
            f"❌ Wrong: {user['wrong']}\n"
            f"📊 Score: {percent:.1f}%"
        )
        return

    q = user["questions"][user["index"]]
    user["current"] = q

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{opt}")] for opt in q["opts"]]

    await update.effective_chat.send_message(
        f"Q{user['index']+1}: {q['q']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ANSWER HANDLER
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = users[query.from_user.id]
    selected = query.data.split("_", 1)[1]
    correct = user["current"]["ans"]

    if selected == correct:
        user["score"] += 1
        text = f"✅ Correct!\nAnswer: {correct}"
    else:
        user["wrong"] += 1
        text = f"❌ Wrong!\nYour answer: {selected}\nCorrect answer: {correct}"

    user["index"] += 1

    await query.edit_message_text(text)

    await send_question(update, context)


# MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(subject, pattern="^sub_"))
app.add_handler(CallbackQueryHandler(difficulty, pattern="^diff_"))
app.add_handler(CallbackQueryHandler(answer, pattern="^ans_"))

app.run_polling()