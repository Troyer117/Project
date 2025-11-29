# Path to the SQLite database file
DB_PATH = r"C:\Users\Troy\Documents\SQL\220\mydb.db"

# Table name to interact with
TABLE_NAME = "transactions"

# Columns to manage (excluding ID)
COLUMNS = {
    "transaction_type": "TEXT",
    "transaction_date": "TEXT",
    "monster_card_id": "INTEGER",
    "spell_card_id": "INTEGER",
    "trap_card_id": "INTEGER",
    "card_id": "INTEGER",
    "set_id": "INTEGER",
    "rarity_id": "INTEGER",
    "archetype_id": "INTEGER",
    "quantity": "INTEGER",
    "details": "TEXT"
}