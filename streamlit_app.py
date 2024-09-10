import pandas as pd
import requests
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from urllib.parse import quote_plus
from requests.exceptions import RequestException
import time

# Function to handle API request with retry mechanism
def fetch_fruit_data(fruit_name, retries=3, delay=2):
    url = f"https://www.fruityvice.com/api/fruit/{quote_plus(fruit_name)}"
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except RequestException as e:
            st.error(f"Error fetching data for {fruit_name}: {e}")
            if attempt < retries - 1:
                st.write(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # Wait before retrying
            else:
                st.error("Failed to fetch data after multiple retries.")
                # Fallback or alternative action can be handled here
                return None

# Example alternative API (if you choose to implement a fallback)
def fetch_fruit_data_alternative(fruit_name):
    # This is a placeholder for an alternative API
    alternative_url = f"https://api.example.com/fruit/{quote_plus(fruit_name)}"
    try:
        response = requests.get(alternative_url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"Alternative API error for {fruit_name}: {e}")
        return None

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
    """Choose The Fruits you Want in your Custom Smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on smoothie will be:", name_on_order)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch data from Snowflake and display
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col('SEARCH_ON'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert Snowpark DataFrame to Pandas DataFrame for easier manipulation
pd_df = my_dataframe.to_pandas()

# Allow user to select up to 5 ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df['FRUIT_NAME'].tolist(), max_selections=5)

if ingredients_list:
    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        # Get the search value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        search_value = search_on if pd.notna(search_on) else fruit_chosen
        st.write('The search value for ', fruit_chosen, ' is ', search_value, '.')
        
        # Fetch and display nutrition data
        fv_data = fetch_fruit_data(search_value)
        if not fv_data:
            fv_data = fetch_fruit_data_alternative(search_value)  # Try alternative API if the primary fails
        
        if fv_data:
            fv_df = pd.DataFrame([fv_data])
            st.subheader(f'{fruit_chosen} Nutrition Information')
            st.dataframe(data=fv_df, use_container_width=True)
        else:
            st.error(f"Could not fetch data for {fruit_chosen}. Please try again later.")
        
        # Append ingredient to the string
        ingredients_string += fruit_chosen + ' '

    # Insert statement for SQL
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    
    # Button to submit the order
    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"Woollah! {name_on_order}, you just ordered your smoothie!", icon="✅")
        except Exception as e:
            st.error(f"Error submitting order: {e}")


