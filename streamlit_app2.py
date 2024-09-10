# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothie Orders! :cup_with_straw:")
st.write(
    """Orders That Need to be Filled.
    """
)
session = get_active_session()
#Name_on_order = st.text_input('Name on Smoothie:')
#st.write('The Name on smoothie will be:', Name_on_order)
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()

if my_dataframe:
     editable_df = st.data_editor(my_dataframe)   

     submitted = st.button('Submit')
if submitted:
    st.success('Someone clicked the button', icon = '👍')
    og_dataset = session.table("smoothies.public.orders")
    edited_dataset = session.create_dataframe(editable_df)

try:
            og_dataset.merge(edited_dataset
                     , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                     , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]) 
            st.success("Order(s) Updated!", icon="👍")

except:
              st.write('something went wrong.')
    
