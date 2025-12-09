import streamlit as st 
import requests
import pandas as pd

# ----------------------------------
# CONFIG
# ----------------------------------

# While you're running FastAPI locally:
YOUNG_DRIVER_API_URL = "http://127.0.0.1:8001/young-driver-products"
# Later, when hosted: e.g. "https://api.yourdomain.com/young_driver_products"

st.set_page_config(page_title="Young Driver Insurance Helper", layout="centered")

st.title("🚗 Young Driver Insurance Helper")
st.write(
    "Choose a young driver product and what you'd like to know more about. "
    "We'll explain it in simple terms."
)


# ----------------------------------
# DATA FETCHING
# ----------------------------------
@st.cache_data(ttl=3600)
def fetch_products():
    resp = requests.get(YOUNG_DRIVER_API_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # Expecting a list of objects like:
    # { "id": "...", "name": "...", "faqs": { ... } }
    return pd.DataFrame(data)


try:
    df_products = fetch_products()
except Exception as e:
    st.error(f"Sorry, we can't load product information right now: {e}")
    st.stop()

if df_products.empty:
    st.error("No young driver products are available at the moment.")
    st.stop()

# ----------------------------------
# UI: STEP 1 – CHOOSE PRODUCT
# ----------------------------------
product_options = df_products["name"].tolist()

selected_product_name = st.selectbox(
    "Which young driver product would you like to know more about?",
    options=product_options,
    index=None,
    placeholder="Select a product..."
)

selected_product_row = None
if selected_product_name:
    selected_product_row = df_products[df_products["name"] == selected_product_name].iloc[0]

# ----------------------------------
# UI: STEP 2 – WHAT DO YOU WANT TO KNOW?
# ----------------------------------
info_map = {
    "Policy benefits": "policy_benefits",
    "What you need to get a quote": "quote_requirements",
    "How to make a claim": "claims_process",
    "What add-ons are available": "add_ons"
}

if selected_product_row is not None:
    st.markdown(f"### Great, let's look at **{selected_product_name}**")

    info_choice = st.radio(
        "What would you like to know?",
        list(info_map.keys())
    )

    if st.button("Show information"):
        faqs = selected_product_row.get("faqs", {})

        # If faqs came through as a stringified dict for some reason, try to normalise
        if isinstance(faqs, str):
            # Optional: you can parse JSON here if needed
            # import json; faqs = json.loads(faqs)
            pass

        field_key = info_map[info_choice]
        answer_text = ""
        if isinstance(faqs, dict):
            answer_text = faqs.get(field_key, "")
        if not answer_text:
            answer_text = "Sorry, we don't have information for this yet."

        st.markdown(f"#### {info_choice}")
        st.write(answer_text)

        st.caption(
            "This information is a guide only and does not form part of your policy terms. "
            "Please refer to your policy documents for full details."
        )
else:
    st.info("Select a product above to continue.")
