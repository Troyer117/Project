import streamlit as st
import sqlite3
import datetime
from config import DB_PATH, TABLE_NAME, COLUMNS

# DB connection helper
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Fetch id -> name map from any table and columns
def fetch_id_name_map(table, id_col, name_col):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {id_col}, {name_col} FROM {table} ORDER BY {name_col}")
    return {row[id_col]: row[name_col] for row in cur.fetchall()}

# Fetch id -> card_name for special card tables joined with cards
def fetch_card_name_map(special_table, special_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT {special_table}.{special_id}, cards.card_name
        FROM {special_table}
        JOIN cards ON {special_table}.card_id = cards.card_id
        ORDER BY cards.card_name
    """)
    return {row[0]: row[1] for row in cur.fetchall()}

# Fetch all transactions ordered by date descending
def fetch_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY transaction_id ASC")
    return cur.fetchall()

# Helper: Find the lowest missing transaction_id
def get_lowest_missing_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT transaction_id FROM {TABLE_NAME} ORDER BY transaction_id")
    ids = [row["transaction_id"] for row in cur.fetchall()]
    expected_id = 1
    for id_ in ids:
        if id_ != expected_id:
            return expected_id
        expected_id += 1
    return expected_id  # if no gaps, return next after last

# Insert a row into transactions (with manual transaction_id)
def insert_row(data):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Assign the lowest missing id before insert
        lowest_missing_id = get_lowest_missing_id()
        data_with_id = {"transaction_id": lowest_missing_id, **data}

        placeholders = ', '.join(['?'] * len(data_with_id))
        query = f"INSERT INTO {TABLE_NAME} ({', '.join(data_with_id.keys())}) VALUES ({placeholders})"
        cur.execute(query, tuple(data_with_id.values()))
        conn.commit()
    except Exception as e:
        st.error(f"Error inserting data: {e}")

# Update a transaction row by transaction_id
def update_row(id_val, data):
    try:
        conn = get_connection()
        cur = conn.cursor()
        set_clause = ', '.join([f"{col}=?" for col in data])
        query = f"UPDATE {TABLE_NAME} SET {set_clause} WHERE transaction_id = ?"
        cur.execute(query, tuple(data.values()) + (id_val,))
        conn.commit()
    except Exception as e:
        st.error(f"Error updating data: {e}")

# Delete a transaction row by transaction_id
def delete_row(id_val):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {TABLE_NAME} WHERE transaction_id = ?", (id_val,))
        conn.commit()
    except Exception as e:
        st.error(f"Error deleting data: {e}")

# Transact between records
def transact_records(from_id, to_id, quantity):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Get source record
        cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE transaction_id = ?", (from_id,))
        from_record = cur.fetchone()
        
        if not from_record:
            st.error("Source record not found!")
            return False
            
        if from_record["quantity"] < quantity:
            st.error("Not enough quantity in source record!")
            return False
        
        # Get destination record
        cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE transaction_id = ?", (to_id,))
        to_record = cur.fetchone()
        
        if not to_record:
            st.error("Destination record not found!")
            return False
        
        # Update source record (subtract quantity)
        new_from_quantity = from_record["quantity"] - quantity
        if new_from_quantity == 0:
            # Delete the record if quantity becomes 0
            cur.execute(f"DELETE FROM {TABLE_NAME} WHERE transaction_id = ?", (from_id,))
        else:
            # Update with new quantity
            cur.execute(f"UPDATE {TABLE_NAME} SET quantity = ? WHERE transaction_id = ?", 
                       (new_from_quantity, from_id))
        
        # Update destination record (add quantity)
        new_to_quantity = to_record["quantity"] + quantity
        cur.execute(f"UPDATE {TABLE_NAME} SET quantity = ? WHERE transaction_id = ?", 
                   (new_to_quantity, to_id))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Error during transaction: {e}")
        return False

# Dropdown helpers
monsters = fetch_card_name_map("monster_cards", "monster_card_id")
spells = fetch_card_name_map("spell_cards", "spell_card_id")
traps = fetch_card_name_map("trap_cards", "trap_card_id")
card_names = fetch_id_name_map("cards", "card_id", "card_name")
sets = fetch_id_name_map("card_sets", "set_id", "set_name")
rarities = fetch_id_name_map("card_rarities", "rarity_id", "rarity_name")
archetypes = fetch_id_name_map("archetypes", "archetype_id", "archetype_name")

def select_fk(label, options_map, default_id=None):
    options = ["None"] + list(options_map.values())
    id_to_name = {k: v for k, v in options_map.items()}
    name_to_id = {v: k for k, v in options_map.items()}
    default_name = id_to_name.get(default_id, "None")
    choice = st.selectbox(label, options, index=options.index(default_name))
    return None if choice == "None" else name_to_id[choice]

# --- Streamlit UI ---
st.title(f"CRUD App for '{TABLE_NAME}' Table")

rows = fetch_all()

st.subheader("Existing Records")
st.dataframe(rows)

# --- Add New Record ---
st.subheader("Add New Record")
with st.form("add_form"):
    new_data = {}
    new_data["transaction_type"] = st.text_input("Transaction Type")
    new_data["transaction_date"] = st.date_input("Transaction Date")

    new_data["monster_card_id"] = select_fk("Monster Card", monsters)
    new_data["spell_card_id"] = select_fk("Spell Card", spells)
    new_data["trap_card_id"] = select_fk("Trap Card", traps)
    new_data["card_id"] = select_fk("Card", card_names)
    new_data["set_id"] = select_fk("Set", sets)
    new_data["rarity_id"] = select_fk("Rarity", rarities)
    new_data["archetype_id"] = select_fk("Archetype", archetypes)

    new_data["quantity"] = st.number_input("Quantity", min_value=1, value=1, step=1)
    new_data["details"] = st.text_area("Details")

    submitted = st.form_submit_button("Add")
    if submitted:
        new_data["transaction_date"] = new_data["transaction_date"].strftime("%Y-%m-%d")
        insert_row(new_data)
        st.success("Record added!")

# --- Update Existing Record ---
if rows:
    st.subheader("Update Existing Record")
    row_ids = [row["transaction_id"] for row in rows]
    selected_id = st.selectbox("Select ID to update", row_ids)
    selected_row = next((r for r in rows if r["transaction_id"] == selected_id), None)

    if selected_row:
        with st.form("update_form"):
            updated_data = {}
            updated_data["transaction_type"] = st.text_input("Transaction Type", value=selected_row["transaction_type"])
            try:
                default_date = datetime.datetime.strptime(selected_row["transaction_date"], "%Y-%m-%d").date()
            except Exception:
                default_date = None
            updated_data["transaction_date"] = st.date_input("Transaction Date", value=default_date)

            updated_data["monster_card_id"] = select_fk("Monster Card", monsters, selected_row["monster_card_id"])
            updated_data["spell_card_id"] = select_fk("Spell Card", spells, selected_row["spell_card_id"])
            updated_data["trap_card_id"] = select_fk("Trap Card", traps, selected_row["trap_card_id"])
            updated_data["card_id"] = select_fk("Card", card_names, selected_row["card_id"])
            updated_data["set_id"] = select_fk("Set", sets, selected_row["set_id"])
            updated_data["rarity_id"] = select_fk("Rarity", rarities, selected_row["rarity_id"])
            updated_data["archetype_id"] = select_fk("Archetype", archetypes, selected_row["archetype_id"])

            updated_data["quantity"] = st.number_input("Quantity", min_value=1, value=selected_row["quantity"] or 1, step=1)
            updated_data["details"] = st.text_area("Details", value=selected_row["details"] or "")

            updated = st.form_submit_button("Update")
            if updated:
                updated_data["transaction_date"] = updated_data["transaction_date"].strftime("%Y-%m-%d")
                update_row(selected_id, updated_data)
                st.success("Record updated!")

    # --- Delete Record ---
    st.subheader("Delete Record")
    delete_id = st.selectbox("Select ID to delete", row_ids, key="delete")
    if st.button("Delete"):
        delete_row(delete_id)
        st.warning("Record deleted.")

    # --- Transact a Record ---
    st.subheader("🔄 Transact a Record")
    st.write("Transfer quantity from one record to another record.")
    
    with st.form("transact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**From Record (Source):**")
            from_id = st.selectbox("Select Source Record ID", row_ids, key="from_record")
            from_record = next((r for r in rows if r["transaction_id"] == from_id), None)
            if from_record:
                st.info(f"Available quantity: {from_record['quantity']}")
                st.write(f"Card: {card_names.get(from_record['card_id'], 'Unknown')}")
        
        with col2:
            st.write("**To Record (Destination):**")
            to_id = st.selectbox("Select Destination Record ID", row_ids, key="to_record")
            to_record = next((r for r in rows if r["transaction_id"] == to_id), None)
            if to_record:
                st.info(f"Current quantity: {to_record['quantity']}")
                st.write(f"Card: {card_names.get(to_record['card_id'], 'Unknown')}")
        
        # Quantity to transfer
        max_quantity = from_record["quantity"] if from_record else 1
        transfer_quantity = st.number_input(
            "Quantity to Transfer", 
            min_value=1, 
            max_value=max_quantity, 
            value=1, 
            step=1
        )
        
        transact_submitted = st.form_submit_button("Execute Transaction")
        if transact_submitted:
            if from_id == to_id:
                st.error("Source and destination records cannot be the same!")
            else:
                if transact_records(from_id, to_id, transfer_quantity):
                    st.success(f"Successfully transferred {transfer_quantity} units from Record {from_id} to Record {to_id}!")
                    st.rerun()  # Refresh the page to show updated data