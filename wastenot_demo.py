import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.title("WasteNot App Demo")
st.write("Reduce food waste by tracking your inventory and expiration dates!")

# ------------------------------
# Step 1: Add items to inventory
# ------------------------------
st.header("Add Food Item")

item_name = st.text_input("Food Item Name")
quantity = st.number_input("Quantity", min_value=1, value=1)
expiry_date = st.date_input("Expiration Date", value=datetime.today())

if st.button("Add Item"):
    if "inventory" not in st.session_state:
        st.session_state.inventory = pd.DataFrame(columns=["Item", "Quantity", "Expiry", "Days Left"])
    days_left = (expiry_date - datetime.today().date()).days
    st.session_state.inventory = pd.concat([
        st.session_state.inventory,
        pd.DataFrame([[item_name, quantity, expiry_date, days_left]],
                     columns=["Item", "Quantity", "Expiry", "Days Left"])
    ], ignore_index=True)

# ------------------------------
# Step 2: Display inventory
# ------------------------------
if "inventory" in st.session_state and not st.session_state.inventory.empty:
    st.header("Current Inventory")
    st.session_state.inventory["Days Left"] = (
                pd.to_datetime(st.session_state.inventory["Expiry"]) - pd.to_datetime(datetime.today().date())).dt.days
    st.dataframe(st.session_state.inventory.sort_values("Days Left"))

    # ------------------------------
    # Step 3: Show alerts
    # ------------------------------
    st.header("Alerts")
    expiring_soon = st.session_state.inventory[st.session_state.inventory["Days Left"] <= 3]
    if not expiring_soon.empty:
        for _, row in expiring_soon.iterrows():
            st.warning(
                f"{row['Item']} ({row['Quantity']}) is expiring in {row['Days Left']} day(s)! Consider eating soon or donating.")
    else:
        st.success("No items expiring in the next 3 days.")

    # ------------------------------
    # Step 4: Recommendation summary
    # ------------------------------
    st.header("Recommendations")


    def recommendation(days_left):
        if days_left <= 0:
            return "Compost"
        elif days_left <= 3:
            return "Eat soon / Donate"
        else:
            return "Keep"


    st.session_state.inventory["Recommendation"] = st.session_state.inventory["Days Left"].apply(recommendation)
    st.dataframe(st.session_state.inventory[["Item", "Quantity", "Days Left", "Recommendation"]])

    # ------------------------------
    # Optional: Waste-avoidance chart
    # ------------------------------
    st.header("Waste Avoidance Chart (Simulation)")
    fig, ax = plt.subplots()
    inventory_counts = st.session_state.inventory["Recommendation"].value_counts()
    ax.bar(inventory_counts.index, inventory_counts.values, color=["green", "orange", "red"])
    ax.set_ylabel("Number of Items")
    ax.set_title("Items by Recommended Action")
    st.pyplot(fig)
