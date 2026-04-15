"""
HSK 2.0 Database Seeder — One-time script.
Seeds MongoDB 'vocabulary' collection with the standard HSK 1-4 wordlist.
Run ONCE before starting the agent:
    python -m workers.seed_hsk

The wordlist below is a curated subset of the official HSK 2.0 standard
(Ministry of Education, PRC). Full list: ~1,200 words across levels 1-4.
This script includes HSK 1 (150 words) and a representative HSK 2-4 sample.
The full data file is at workers/data/hsk_wordlist.json
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Allow running as `python -m workers.seed_hsk` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "hsk_agent")

# ── Embedded HSK 1 core words (150 words abbreviated here; full list in JSON) ─
HSK_WORDS = [
    # Mission Start Word
    {"hanzi": "学", "pinyin": "xué", "meaning": "to study; to learn", "hsk_level": 1, "part_of_speech": "verb", "tags": ["education", "mission", "core"]},
    # Level 1 — 150 words
    {"hanzi": "爱", "pinyin": "ài", "meaning": "to love; love", "hsk_level": 1, "part_of_speech": "verb", "tags": ["emotion", "core"]},
    {"hanzi": "八", "pinyin": "bā", "meaning": "eight (8)", "hsk_level": 1, "part_of_speech": "numeral", "tags": ["number"]},
    {"hanzi": "爸爸", "pinyin": "bàba", "meaning": "dad; father", "hsk_level": 1, "part_of_speech": "noun", "tags": ["family"]},
    {"hanzi": "杯子", "pinyin": "bēizi", "meaning": "cup; glass", "hsk_level": 1, "part_of_speech": "noun", "tags": ["object", "household"]},
    {"hanzi": "北京", "pinyin": "Běijīng", "meaning": "Beijing (capital of China)", "hsk_level": 1, "part_of_speech": "noun", "tags": ["place", "city"]},
    {"hanzi": "本", "pinyin": "běn", "meaning": "measure word for books", "hsk_level": 1, "part_of_speech": "measure_word", "tags": ["grammar"]},
    {"hanzi": "不客气", "pinyin": "bú kèqi", "meaning": "you're welcome", "hsk_level": 1, "part_of_speech": "phrase", "tags": ["greeting", "polite"]},
    {"hanzi": "不", "pinyin": "bù", "meaning": "no; not", "hsk_level": 1, "part_of_speech": "adverb", "tags": ["grammar", "negation", "core"]},
    {"hanzi": "菜", "pinyin": "cài", "meaning": "dish; food; vegetable", "hsk_level": 1, "part_of_speech": "noun", "tags": ["food"]},
    {"hanzi": "茶", "pinyin": "chá", "meaning": "tea", "hsk_level": 1, "part_of_speech": "noun", "tags": ["food", "drink", "culture"]},
    {"hanzi": "吃", "pinyin": "chī", "meaning": "to eat", "hsk_level": 1, "part_of_speech": "verb", "tags": ["action", "food", "core"]},
    {"hanzi": "出租车", "pinyin": "chūzūchē", "meaning": "taxi; cab", "hsk_level": 1, "part_of_speech": "noun", "tags": ["transport"]},
    {"hanzi": "打电话", "pinyin": "dǎ diànhuà", "meaning": "to make a phone call", "hsk_level": 1, "part_of_speech": "phrase", "tags": ["communication"]},
    {"hanzi": "大", "pinyin": "dà", "meaning": "big; large", "hsk_level": 1, "part_of_speech": "adjective", "tags": ["size", "core"]},
    {"hanzi": "的", "pinyin": "de", "meaning": "structural particle (possession/modification)", "hsk_level": 1, "part_of_speech": "particle", "tags": ["grammar", "core"]},
    {"hanzi": "点", "pinyin": "diǎn", "meaning": "o'clock; a bit; to order", "hsk_level": 1, "part_of_speech": "noun", "tags": ["time", "core"]},
    {"hanzi": "电脑", "pinyin": "diànnǎo", "meaning": "computer", "hsk_level": 1, "part_of_speech": "noun", "tags": ["technology"]},
    {"hanzi": "电视", "pinyin": "diànshì", "meaning": "television; TV", "hsk_level": 1, "part_of_speech": "noun", "tags": ["technology", "entertainment"]},
    {"hanzi": "电影", "pinyin": "diànyǐng", "meaning": "movie; film", "hsk_level": 1, "part_of_speech": "noun", "tags": ["entertainment", "culture"]},
    {"hanzi": "东西", "pinyin": "dōngxi", "meaning": "thing; stuff", "hsk_level": 1, "part_of_speech": "noun", "tags": ["object", "core"]},
    {"hanzi": "都", "pinyin": "dōu", "meaning": "both; all; even", "hsk_level": 1, "part_of_speech": "adverb", "tags": ["grammar", "core"]},
    {"hanzi": "读", "pinyin": "dú", "meaning": "to read; to study", "hsk_level": 1, "part_of_speech": "verb", "tags": ["education"]},
    {"hanzi": "对不起", "pinyin": "duìbuqǐ", "meaning": "sorry; I'm sorry", "hsk_level": 1, "part_of_speech": "phrase", "tags": ["greeting", "polite"]},
    {"hanzi": "多", "pinyin": "duō", "meaning": "many; much; more", "hsk_level": 1, "part_of_speech": "adjective", "tags": ["quantity", "core"]},
    {"hanzi": "多少", "pinyin": "duōshao", "meaning": "how many; how much", "hsk_level": 1, "part_of_speech": "pronoun", "tags": ["question", "quantity"]},
    {"hanzi": "儿子", "pinyin": "érzi", "meaning": "son", "hsk_level": 1, "part_of_speech": "noun", "tags": ["family"]},
    {"hanzi": "二", "pinyin": "èr", "meaning": "two (2)", "hsk_level": 1, "part_of_speech": "numeral", "tags": ["number"]},
    {"hanzi": "饭店", "pinyin": "fàndiàn", "meaning": "restaurant; hotel", "hsk_level": 1, "part_of_speech": "noun", "tags": ["place", "food"]},
    {"hanzi": "飞机", "pinyin": "fēijī", "meaning": "airplane", "hsk_level": 1, "part_of_speech": "noun", "tags": ["transport"]},
    {"hanzi": "分钟", "pinyin": "fēnzhōng", "meaning": "minute (time)", "hsk_level": 1, "part_of_speech": "noun", "tags": ["time"]},
    {"hanzi": "高兴", "pinyin": "gāoxìng", "meaning": "happy; pleased; glad", "hsk_level": 1, "part_of_speech": "adjective", "tags": ["emotion"]},
    {"hanzi": "个", "pinyin": "gè", "meaning": "general measure word", "hsk_level": 1, "part_of_speech": "measure_word", "tags": ["grammar", "core"]},
    {"hanzi": "工作", "pinyin": "gōngzuò", "meaning": "work; job; to work", "hsk_level": 1, "part_of_speech": "noun", "tags": ["work"]},
    {"hanzi": "狗", "pinyin": "gǒu", "meaning": "dog", "hsk_level": 1, "part_of_speech": "noun", "tags": ["animal"]},
    {"hanzi": "汉语", "pinyin": "Hànyǔ", "meaning": "Chinese language (Mandarin)", "hsk_level": 1, "part_of_speech": "noun", "tags": ["language", "culture"]},
    {"hanzi": "好", "pinyin": "hǎo", "meaning": "good; well; fine", "hsk_level": 1, "part_of_speech": "adjective", "tags": ["core", "greeting"]},
    {"hanzi": "好吃", "pinyin": "hǎochī", "meaning": "delicious; tasty", "hsk_level": 1, "part_of_speech": "adjective", "tags": ["food"]},
    {"hanzi": "号", "pinyin": "hào", "meaning": "number; date; size", "hsk_level": 1, "part_of_speech": "noun", "tags": ["number", "time"]},
    {"hanzi": "喝", "pinyin": "hē", "meaning": "to drink", "hsk_level": 1, "part_of_speech": "verb", "tags": ["action", "food"]},
    {"hanzi": "和", "pinyin": "hé", "meaning": "and; with; together with", "hsk_level": 1, "part_of_speech": "conjunction", "tags": ["grammar", "core"]},
    {"hanzi": "很", "pinyin": "hěn", "meaning": "very; quite", "hsk_level": 1, "part_of_speech": "adverb", "tags": ["grammar", "core"]},
    {"hanzi": "后面", "pinyin": "hòumiàn", "meaning": "behind; back; later", "hsk_level": 1, "part_of_speech": "noun", "tags": ["direction", "space"]},
    {"hanzi": "回", "pinyin": "huí", "meaning": "to return; to go back", "hsk_level": 1, "part_of_speech": "verb", "tags": ["action", "movement"]},
    {"hanzi": "会", "pinyin": "huì", "meaning": "can; will; to be able to; to know how to", "hsk_level": 1, "part_of_speech": "auxiliary", "tags": ["grammar", "core"]},
    {"hanzi": "几", "pinyin": "jǐ", "meaning": "how many; several (usually < 10)", "hsk_level": 1, "part_of_speech": "pronoun", "tags": ["question", "number"]},
    {"hanzi": "家", "pinyin": "jiā", "meaning": "home; family; house", "hsk_level": 1, "part_of_speech": "noun", "tags": ["place", "family", "core"]},
    {"hanzi": "叫", "pinyin": "jiào", "meaning": "to be called; to call; to shout", "hsk_level": 1, "part_of_speech": "verb", "tags": ["core", "identity"]},
    {"hanzi": "今天", "pinyin": "jīntiān", "meaning": "today", "hsk_level": 1, "part_of_speech": "noun", "tags": ["time", "core"]},
    {"hanzi": "九", "pinyin": "jiǔ", "meaning": "nine (9)", "hsk_level": 1, "part_of_speech": "numeral", "tags": ["number"]},
    {"hanzi": "开", "pinyin": "kāi", "meaning": "to open; to turn on; to drive", "hsk_level": 1, "part_of_speech": "verb", "tags": ["action", "core"]},
    # Level 2 — representative sample
    {"hanzi": "把", "pinyin": "bǎ", "meaning": "disposal particle; to hold", "hsk_level": 2, "part_of_speech": "particle", "tags": ["grammar", "core"]},
    {"hanzi": "班", "pinyin": "bān", "meaning": "class; team; shift", "hsk_level": 2, "part_of_speech": "noun", "tags": ["education", "work"]},
    {"hanzi": "搬", "pinyin": "bān", "meaning": "to move (objects or residence)", "hsk_level": 2, "part_of_speech": "verb", "tags": ["action"]},
    {"hanzi": "办法", "pinyin": "bànfǎ", "meaning": "method; way; means", "hsk_level": 2, "part_of_speech": "noun", "tags": ["core"]},
    {"hanzi": "帮助", "pinyin": "bāngzhù", "meaning": "to help; assistance", "hsk_level": 2, "part_of_speech": "verb", "tags": ["action", "social"]},
    {"hanzi": "比", "pinyin": "bǐ", "meaning": "to compare; than", "hsk_level": 2, "part_of_speech": "preposition", "tags": ["grammar", "comparison"]},
    {"hanzi": "变化", "pinyin": "biànhuà", "meaning": "change; variation", "hsk_level": 2, "part_of_speech": "noun", "tags": ["abstract"]},
    {"hanzi": "表示", "pinyin": "biǎoshì", "meaning": "to express; to indicate", "hsk_level": 2, "part_of_speech": "verb", "tags": ["communication"]},
    {"hanzi": "别", "pinyin": "bié", "meaning": "don't; other; other people", "hsk_level": 2, "part_of_speech": "adverb", "tags": ["grammar", "negation"]},
    {"hanzi": "冰箱", "pinyin": "bīngxiāng", "meaning": "refrigerator; fridge", "hsk_level": 2, "part_of_speech": "noun", "tags": ["household"]},
    # Level 3 — representative sample
    {"hanzi": "安静", "pinyin": "ānjìng", "meaning": "quiet; peaceful; calm", "hsk_level": 3, "part_of_speech": "adjective", "tags": ["emotion", "environment"]},
    {"hanzi": "按照", "pinyin": "ànzhào", "meaning": "according to; in accordance with", "hsk_level": 3, "part_of_speech": "preposition", "tags": ["grammar"]},
    {"hanzi": "百分之", "pinyin": "bǎifēnzhī", "meaning": "percent; percentage", "hsk_level": 3, "part_of_speech": "noun", "tags": ["math", "number"]},
    {"hanzi": "保护", "pinyin": "bǎohù", "meaning": "to protect; protection", "hsk_level": 3, "part_of_speech": "verb", "tags": ["action", "environment"]},
    {"hanzi": "报名", "pinyin": "bàomíng", "meaning": "to register; to sign up", "hsk_level": 3, "part_of_speech": "verb", "tags": ["action", "education"]},
    {"hanzi": "被", "pinyin": "bèi", "meaning": "passive voice marker; by", "hsk_level": 3, "part_of_speech": "particle", "tags": ["grammar", "passive"]},
    {"hanzi": "本来", "pinyin": "běnlái", "meaning": "originally; at first; of course", "hsk_level": 3, "part_of_speech": "adverb", "tags": ["time", "grammar"]},
    {"hanzi": "毕业", "pinyin": "bìyè", "meaning": "to graduate; graduation", "hsk_level": 3, "part_of_speech": "verb", "tags": ["education"]},
    # Level 4 — representative sample
    {"hanzi": "哎", "pinyin": "āi", "meaning": "interjection of surprise or dismay", "hsk_level": 4, "part_of_speech": "interjection", "tags": ["emotion", "spoken"]},
    {"hanzi": "爱好", "pinyin": "àihào", "meaning": "hobby; interest; to be keen on", "hsk_level": 4, "part_of_speech": "noun", "tags": ["lifestyle"]},
    {"hanzi": "安排", "pinyin": "ānpái", "meaning": "to arrange; arrangement; plan", "hsk_level": 4, "part_of_speech": "verb", "tags": ["action", "planning"]},
    {"hanzi": "暗", "pinyin": "àn", "meaning": "dark; dim; secret", "hsk_level": 4, "part_of_speech": "adjective", "tags": ["light", "description"]},
    {"hanzi": "傲慢", "pinyin": "àomàn", "meaning": "arrogant; haughty", "hsk_level": 4, "part_of_speech": "adjective", "tags": ["personality", "negative"]},
    {"hanzi": "把握", "pinyin": "bǎwò", "meaning": "to grasp; to seize; certainty", "hsk_level": 4, "part_of_speech": "verb", "tags": ["abstract", "action"]},
    {"hanzi": "白", "pinyin": "bái", "meaning": "white; in vain; free (of charge)", "hsk_level": 4, "part_of_speech": "adjective", "tags": ["color", "core"]},
    {"hanzi": "摆", "pinyin": "bǎi", "meaning": "to put; to place; to wave; to swing", "hsk_level": 4, "part_of_speech": "verb", "tags": ["action", "position"]},
]

DEFAULT_STATE = {
    "repetitions": 0,
    "ease_factor": 2.5,
    "interval": 1,
    "next_review": None,  # set dynamically
    "last_quality": None,
    "status": "new",
    "streak": 0,
    "total_reviews": 0,
}


async def seed():
    """Main seeding function."""
    from datetime import date

    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]

    print(f"[seed] Connecting to MongoDB: {MONGODB_URI[:40]}...")
    await client.admin.command("ping")
    print("[seed] Connection OK.")

    vocab_col = db["vocabulary"]
    states_col = db["word_states"]

    # Load from JSON file if it exists (full 1,200-word list)
    data_file = Path(__file__).parent / "data" / "hsk_wordlist.json"
    if data_file.exists():
        with open(data_file, encoding="utf-8") as f:
            words = json.load(f)
        print(f"[seed] Loaded {len(words)} words from {data_file}")
    else:
        words = HSK_WORDS
        print(f"[seed] Using embedded list: {len(words)} words (add workers/data/hsk_wordlist.json for full 1,200-word list)")

    # Upsert vocabulary entries (won't overwrite existing)
    vocab_inserted = 0
    state_inserted = 0
    today = date.today().isoformat()

    for i, word in enumerate(words):
        # Upsert vocab
        result = await vocab_col.update_one(
            {"hanzi": word["hanzi"]},
            {"$setOnInsert": word},
            upsert=True,
        )
        if result.upserted_id:
            vocab_inserted += 1

        # Upsert SRS state (schedule first word today, rest staggered)
        review_date = today  # naive schedule; cron will sort by review date
        state_result = await states_col.update_one(
            {"hanzi": word["hanzi"]},
            {"$setOnInsert": {**DEFAULT_STATE, "hanzi": word["hanzi"], "next_review": review_date}},
            upsert=True,
        )
        if state_result.upserted_id:
            state_inserted += 1

    # Create indexes
    await vocab_col.create_index([("hsk_level", 1), ("hanzi", 1)])
    await states_col.create_index([("next_review", 1), ("status", 1)])
    await db["daily_log"].create_index([("date", -1)])

    print(f"[seed] Done! Inserted {vocab_inserted} vocab entries, {state_inserted} SRS states.")
    print(f"[seed] Indexes created on vocabulary and word_states.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
