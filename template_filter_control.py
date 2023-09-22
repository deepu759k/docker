import streamlit as st
import mysql.connector
import pandas as pd
from Utils import Utils  # Import the Utils class from your code
import datetime

# Set the Streamlit theme to "wide"
st.set_page_config(
    page_title="Filter & Theme Mapping",
    page_icon="🌟",
    layout="wide",  # For a wider layout
)

# Apply custom CSS to style the app with your preferred colors
st.markdown(
    """
    <style>
    /* Main app container */
    .stApp {
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem;
        text-align: left; /* Align text to the left */
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Background color for the header */
    .header {
        background-color: #00213C; /* Change background color here */
        color: white;
        padding: 1rem;
        font-size: 24px;
        font-weight: bold;
    }

    /* Section header */
    .section-header {
        background-color: #00213C; /* Change background color here */
        color: white;
        padding: 0.5rem 1rem;
        font-size: 18px;
        font-weight: bold;
        border-radius: 5px;
    }

    /* Radio buttons with labels */
    .radio-container {
        display: flex;
        align-items: center;
        margin-top: 1rem;
    }

    .radio-container label {
        margin-right: 1rem;
    }

    /* Select boxes */
    .select-box {
        width: 100%;
        padding: 0.5rem;
        font-size: 16px;
    }

    /* Multiselect */
    .multiselect {
        width: 100%;
        padding: 0.5rem;
        font-size: 16px;
    }

    /* Button */
    .save-button {
        background-color: #00213C; /* Change background color here */
        color: white;
        padding: 0.5rem 1rem;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    /* Dataframe */
    .dataframe {
        font-size: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# Header section
st.markdown('<div class="header">Theme and Filter Mapping Subscription</div>', unsafe_allow_html=True)

# Description
st.markdown('<div class="section-header">Please select Theme or Filter</div>', unsafe_allow_html=True)

# Sidebar section for selecting mapping type
mapping_type = st.sidebar.radio("Select Mapping Type", ["Theme Mapping", "Filter Mapping"])

# Connect to the database
shopify_db, template_db = Utils.connect_to_db()

if mapping_type == "Filter Mapping":
    # Define your SQL query to select unique themes, genders, and shop_ids
    query = "SELECT DISTINCT theme FROM template_metadata.template;"
    cursor = template_db.cursor()
    cursor.execute(query)
    themes = [row[0] for row in cursor.fetchall()]
    cursor.close()

    query = "SELECT DISTINCT gender FROM template_metadata.template;"
    cursor = template_db.cursor()
    cursor.execute(query)
    genders = [row[0] for row in cursor.fetchall()]
    cursor.close()

    query = "SELECT DISTINCT shop_id FROM shopify.shop;"
    cursor = shopify_db.cursor()
    cursor.execute(query)
    shop_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # Select a shop_id with a unique key
    selected_shop_id = st.selectbox("Select a shop_id:", shop_ids, key="shop_id_selectbox")

    # Select a theme, gender, and MIX_name options
    selected_theme = st.selectbox("Select a theme:", themes, key="theme_selectbox")
    selected_gender = st.selectbox("Select a gender:", genders, key="gender_selectbox")

    # Retrieve the MIX_name options for the selected theme and gender
    mix_names_query = f"SELECT MIX_name FROM template_metadata.template WHERE theme = '{selected_theme}' AND gender = '{selected_gender}';"
    cursor = template_db.cursor()
    cursor.execute(mix_names_query)
    mix_name_options = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # Select "subscribed" and "enabled" options with labels
    subscribed_option = st.radio("Select an option for 'Do you want to be subscribed?':", ["Yes", "No"], key="subscribed_radio")
    enabled_option = st.radio("Select an option for 'Do you want to be enabled?':", ["Yes", "No"], key="enabled_radio")

    # Map the selected options to 1 (Yes) or 0 (No)
    subscribed_value = 1 if subscribed_option == "Yes" else 0
    enabled_value = 1 if enabled_option == "Yes" else 0

    # Create checkboxes for each MIX_name option
    selected_mix_names = st.multiselect(f"Select MIX_name options for {selected_theme} - {selected_gender}:", mix_name_options, key="mix_name_multiselect")

    # Display the selected options
    if selected_mix_names:
        st.write("Selected MIX_name options:")
        st.write(selected_mix_names)

        # Retrieve the rows from the database for the selected options
        selected_rows_query = f"SELECT * FROM template_metadata.template WHERE theme = '{selected_theme}' AND gender = '{selected_gender}' AND MIX_name IN {tuple(selected_mix_names)};"
        cursor = template_db.cursor(dictionary=True)
        cursor.execute(selected_rows_query)
        selected_rows = cursor.fetchall()
        cursor.close()

        # Add the selected shop_id, subscribed, and enabled values to each row
        for row in selected_rows:
            row['shop_id'] = selected_shop_id
            row['subscribed'] = subscribed_value
            row['enabled'] = enabled_value

        # Convert the selected rows to a DataFrame
        selected_df = pd.DataFrame(selected_rows)

        # Save the selected DataFrame as a CSV file
        # ... Rest of your code ...

# Save the selected DataFrame as a CSV file
    if st.button("Save Selected Options as CSV"):
        # Generate a continuous number for 'id'
        selected_df['id'] = range(1, len(selected_df) + 1)

        # Get the UTC created time
        selected_df['created_time'] = datetime.datetime.utcnow()
        selected_df['updated_time'] = datetime.datetime.utcnow()

        # Get the theme_id based on the selected theme
        # Check if the theme exists in the masterthemetable
        theme_id_query = f"SELECT id FROM shopify.masterthemetable WHERE theme_name = '{selected_theme}';"
        cursor = template_db.cursor()
        cursor.execute(theme_id_query)
        theme_id_result = cursor.fetchone()
        cursor.close()

        if theme_id_result:
            # Theme exists, retrieve the 'id'
            theme_id = theme_id_result[0]
        else:
            data = {'theme_name': [selected_theme], 'no_of_filters': ['0'], 'prod_type_id': ['1'], 'enabled': ['1']}
            data = pd.DataFrame(data=data)
            index = []
            Utils.dataframe_to_MySQL(data, index, 'masterthemetable', shopify_db)

            # Retrieve the 'id' of the newly inserted theme
            cursor = shopify_db.cursor()
            cursor.execute(theme_id_query)
            theme_id = cursor.fetchone()[0]
            cursor.close()


        # Now you have the 'theme_id' for the selected theme, which can be used in your application logic.

        selected_df['theme_id'] = theme_id

        # Rename columns to match the desired column names
        selected_df.rename(columns={
            'MIX_name': 'filter_name',
            'subscribed': 'subscribed',
            'enabled': 'enabled'
        }, inplace=True)

        # Add the remaining columns with default values
        selected_df['sync_flag'] = 1
        selected_df['source'] = "shopifycatalogfilters"
        selected_df['prev_subscription'] = 0
        selected_df['products_count'] = 0
        selected_df['total_attribute_match_count'] = 0

        # Define the order of columns
        column_order = [
            'id', 'created_time','updated_time', 'shop_id', 'theme_id', 'filter_name', 'sync_flag',
            'subscribed', 'enabled', 'source', 'prev_subscription', 'products_count',
            'total_attribute_match_count'
        ]

        # Reorder the columns
        selected_df = selected_df[column_order]
        # Check if the user wants to integrate to the database
    # Check if the user wants to integrate to the database
        integrate_to_db = st.radio("Do you want to integrate to the database?", ["Yes", "No"], key="integrate_db_radio")

        if integrate_to_db == "Yes":
            # Assuming you have the data generated from "type 1" in the DataFrame selected_df
            # You also have shop_id, theme_id, filter_name, subscribed_value, enabled_value as variables

            # Iterate through the rows in selected_df
            for index, row in selected_df.iterrows():
                # Extract the necessary values from the row
                shop_id = row['shop_id']
                theme_id = row['theme_id']
                filter_name = row['filter_name']
                subscribed_value = row['subscribed']
                enabled_value = row['enabled']

                # Check if the combination of shop_id, theme_id, and filter_name exists
                check_query = f"""
                    SELECT id FROM shopify.shopfiltermappingtable
                    WHERE shop_id = {shop_id}
                    AND theme_id = {theme_id}
                    AND filter_name = '{filter_name}';
                """

                cursor = shopify_db.cursor()
                cursor.execute(check_query)
                existing_id = cursor.fetchone()
                cursor.close()

                if existing_id:
                    # Case 1: shop_id, theme_id, and filter_name already exist, update the row
                    update_query = f"""
                        UPDATE shopify.shopfiltermappingtable
                        SET
                            subscribed = {subscribed_value},
                            enabled = {enabled_value},
                            updated_time = NOW()  # Use MySQL's NOW() function to get the current timestamp
                        WHERE id = {existing_id[0]};
                    """

                    cursor = shopify_db.cursor()
                    cursor.execute(update_query)
                    cursor.close()
                    shopify_db.commit()
                    st.info(f"shop_id {shop_id}, theme_id {theme_id}, and filter_name '{filter_name}' already exist and updated as per user preferences.")
                else:
                    # Case 2: shop_id, theme_id, or filter_name do not exist, insert a new row
                    insert_query = f"""
                        INSERT INTO shopify.shopfiltermappingtable (
                            shop_id, theme_id, filter_name, sync_flag,
                            subscribed, enabled, source, prev_subscription,
                            products_count, total_attribute_match_count,
                            created_time, updated_time
                        )
                        VALUES (
                            {shop_id}, {theme_id}, '{filter_name}', 1,
                            {subscribed_value}, {enabled_value}, 'shopifycatalogfilters', 0,
                            0, 0, NOW(), NOW()
                        );
                    """

                    cursor = shopify_db.cursor()
                    cursor.execute(insert_query)
                    cursor.close()
                    shopify_db.commit()
                    st.info(f"Inserted a new record for shop_id {shop_id}, theme_id {theme_id}, and filter_name '{filter_name}' as per user preferences.")
        else:
            # Case 3: Integration to the database is skipped
            st.info("Integration to the database is skipped as per user preferences.")


            # Save the DataFrame as a CSV file
            selected_df.to_csv("selected_options.csv", index=False)
            st.success("Selected options saved as 'selected_options.csv'")


    # Display the selected DataFrame
    if "selected_df" in locals():
        st.dataframe(selected_df)

elif mapping_type == "Theme Mapping":
    # Define your Theme Mapping logic here
    query = "SELECT DISTINCT theme FROM template_metadata.template;"
    cursor = template_db.cursor()
    cursor.execute(query)
    themes = [row[0] for row in cursor.fetchall()]
    cursor.close()

    query = "SELECT DISTINCT shop_id FROM shopify.shop;"
    cursor = shopify_db.cursor()
    cursor.execute(query)
    shop_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # Select a shop_id with a unique key
    selected_shop_id = st.selectbox("Select a shop_id:", shop_ids, key="shop_id_selectbox")

    # Select a theme from the distinct themes
    selected_theme = st.selectbox("Select a theme:", themes, key="theme_selectbox")

    # Check if the theme exists in the masterthemetable
    theme_id_query = f"SELECT id FROM shopify.masterthemetable WHERE theme_name = '{selected_theme}';"
    cursor = shopify_db.cursor()
    cursor.execute(theme_id_query)
    theme_id_result = cursor.fetchone()
    cursor.close()

    if theme_id_result:
        # Theme exists, retrieve the 'id'
        theme_id = theme_id_result[0]
    else:
        # Theme doesn't exist, insert a new row
        data = {'theme_name': [selected_theme], 'no_of_filters': ['0'], 'prod_type_id': ['1'], 'enabled': ['1']}
        data = pd.DataFrame(data=data)
        index = []
        Utils.dataframe_to_MySQL(data, index, 'masterthemetable', shopify_db)

        # Retrieve the 'id' of the newly inserted theme
        cursor = shopify_db.cursor()
        cursor.execute(theme_id_query)
        theme_id = cursor.fetchone()[0]
        cursor.close()


    # Now you have the 'theme_id' for the selected theme, which can be used in your application logic.

    # You can continue with the rest of your Theme Mapping logic here

    # For example, you can select other options, set default values, and save the data to a CSV file
    enabled_option = st.radio("Select an option for 'Enabled?':", ["Yes", "No"], key="enabled_radio")
    subscribed_option = st.radio("Select an option for 'Subscribed?':", ["Yes", "No"], key="subscribed_radio")

    enabled_value = 1 if enabled_option == "Yes" else 0
    subscribed_value = 1 if subscribed_option == "Yes" else 0

    # Create a DataFrame with the selected data
    selected_data = {
    'id': list(range(1, 2)),  # Consecutive IDs starting from 1
    'shop_id': [selected_shop_id],
    'theme_id': [theme_id],
    'enabled': [enabled_value],
    'subscribed': [subscribed_value],
    'created_time': [datetime.datetime.utcnow()],
    'updated_time': [datetime.datetime.utcnow()],  # Default value is None
    'subscribed_filter_count': [0]
    }

    selected_df = pd.DataFrame(selected_data)
    # Ask whether the user wants to integrate to the database
    integrate_to_db = st.radio("Do you want to integrate to the database?", ["Yes", "No"], key="integrate_db_radio")

    if integrate_to_db == "Yes":
        # Check if the combination of shop_id and theme_id exists in the database
        check_query = f"SELECT id FROM shopify.shopthememappingtable WHERE shop_id = {selected_shop_id} AND theme_id = {theme_id};"
        cursor = shopify_db.cursor()
        cursor.execute(check_query)
        existing_id = cursor.fetchone()
        cursor.close()

        if existing_id:
            # Case 1: shop_id and theme_id already exist, update the row
            update_query = f"""
            UPDATE shopify.shopthememappingtable
            SET
                enabled = {enabled_value},
                subscribed = {subscribed_value},
                updated_time = '{datetime.datetime.utcnow()}'
            WHERE id = {existing_id[0]};
            """
            cursor = shopify_db.cursor()
            cursor.execute(update_query)
            cursor.close()
            shopify_db.commit()
            st.info(f"shop_id {selected_shop_id} and theme_id {theme_id} already exist and updated as per user preferences.")
        elif not existing_id:
            # Case 2: shop_id exists but theme_id does not exist, insert a new row with all columns, including shop_id and theme_id
            insert_query = f"""
            INSERT INTO shopify.shopthememappingtable (
                shop_id, theme_id, enabled, subscribed, created_time, updated_time, subscribed_filter_count
            )
            VALUES (
                {selected_shop_id}, {theme_id}, {enabled_value}, {subscribed_value},
                '{datetime.datetime.utcnow()}', NULL, 0
            );
            """
            cursor = shopify_db.cursor()
            cursor.execute(insert_query)
            cursor.close()
            shopify_db.commit()
            st.info(f"shop_id {selected_shop_id} exists, but theme_id {theme_id} does not exist and inserted a new record as per user preferences.")
        else:
            # Case 3: shop_id and theme_id do not exist, insert a new row with all columns, including shop_id and theme_id
            insert_query = f"""
            INSERT INTO shopify.shopthememappingtable (
                shop_id, theme_id, enabled, subscribed, created_time, updated_time, subscribed_filter_count
            )
            VALUES (
                {selected_shop_id}, {theme_id}, {enabled_value}, {subscribed_value},
                '{datetime.datetime.utcnow()}', NULL, 0
            );
            """
            cursor = shopify_db.cursor()
            cursor.execute(insert_query)
            cursor.close()
            shopify_db.commit()
            st.info(f"shop_id {selected_shop_id} and theme_id {theme_id} do not exist and inserted a new record as per user preferences.")
    else:
        # Case 4: Integration to the database is skipped
        st.info("Integration to the database is skipped as per user preferences.")



    # Save the selected DataFrame as a CSV file
    if st.button("Save Selected Options as CSV"):
        # Generate a continuous number for 'id'
        selected_df['id'] = range(1, len(selected_df) + 1)

        # Define the order of columns
        column_order = [
            'id', 'created_time', 'shop_id', 'theme_id', 'enabled', 'subscribed', 'subscribed_filter_count'
        ]

        # Reorder the columns
        selected_df = selected_df[column_order]

        # Save the DataFrame as a CSV file
        selected_df.to_csv("theme_mapping_options.csv", index=False)
        st.success("Theme mapping options saved as 'theme_mapping_options.csv'")

    # Display the selected DataFrame
    if not selected_df.empty:
        st.dataframe(selected_df)
