# Import python packages
import pandas as pd 
import streamlit as st
import requests


# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
    """Choose The Fruits you Want in your Custom Smoothie!
    """
)


name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on smoothie will be:", name_on_order)

from snowflake.snowpark.functions import col 

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_ON'))
#, col('SEARCH_ON')
st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Converting the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function 
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect("Choose up to 5 ingredients:",my_dataframe,max_selections=5)

if ingredients_list:

       ingredients_string = " "
       for fruit_chosen in ingredients_list:
                ingredients_string += fruit_chosen + ' '

                search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen,'SEARCH_ON'].iloc[0]
                st.write('The search value for ', fruit_chosen,' is ', search_on,'.')
           
                #st.dataframe(fruit_chosen)
                st.subheader(fruit_chosen ,'SEARCH_ON' + 'Nutrition Information')
                #formatted_fruit = fruit_chosen.lower()
                #st.formatted_fruit
           
                Search_result=st.SEARCH_ON
              
                fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + SEARCH_ON)
                fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)  
              


                st.write(ingredients_string)
my_insert_stmt = ( """ insert into smoothies.public.orders(ingredients,name_on_order)values ('""" + ingredients_string + """','""" +name_on_order+ """')""")

    #st.write(my_insert_stmt)
    #st.stop()
time_to_insert = st.button("Submit Order")
         #try:
            # Execute the SQL insert query
            #session.sql(my_insert_stmt).collect()


if time_to_insert:
                session.sql(my_insert_stmt).collect()
                st.success(f" Woollah ! {name_on_order} You Just Ordered your Smoothie!", icon="✅")


