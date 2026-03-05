import streamlit as st

def resource_path(relative_path):
    import os
    import sys

    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def local_css(file_name):
    import streamlit as st 
    with open(resource_path(file_name)) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def financial_retrieval(costs, revenues, margins, percentages):
    import pandas as pd

    processed_costs = [cost * 1000 for cost in costs]
    processed_revenue = [revenue * 1000 for revenue in revenues]
    processed_margin = [margin * 1000 for margin in margins]
    processed_margin_percentage = [percentage * 100 for percentage in percentages]

    data = {
        "Category": ["HPC-AI","Compute","Storage","Software","3P/OEM","Total Product","Installation","Support",
                        "Complete Care","Managed Services","Colo","3PP Product","3PP Support","SaaS","SW Services",
                        "Ezmeral","Total Services","Total Products+Services","A&PS","A&PS 3PP","A&PS Colo","Total A&PS","Pan HPE"],
        "Cost": processed_costs,
        "Revenue": processed_revenue,
        "Margin": processed_margin,
        "Percentage": processed_margin_percentage
    }

    return pd.DataFrame(data)

def model_header_read(df):
    sales_motion = df.iloc[1, 8]
    return sales_motion

def currency_read(df):
    currency_raw = df.iloc[53, 3]
    rate_raw = df.iloc[54, 3]

    try:
        float(currency_raw)
        currency = "USD"
    except (ValueError, TypeError):
        currency = str(currency_raw).strip().upper()

    try:
        rate = float(rate_raw)
    except (ValueError, TypeError):
        rate = 1.0

    fx = (1 / rate) if currency != "USD" and rate != 0 else 1.0

    return currency, rate, fx

def pl_mgmt_read(df):

    currency, rate, fx = currency_read(df)

    # Cell Mapping for Day 1 financial information
    day1_costs =       [v * fx for v in df.iloc[44, 1:24].tolist()]
    day1_revenues =    [v * fx for v in df.iloc[42, 1:24].tolist()]
    day1_margins =     [v * fx for v in df.iloc[45, 1:24].tolist()]
    day1_percentages = df.iloc[46, 1:24].tolist()

    # Cell Mapping for Growth financial information
    growth_costs =       [v * fx for v in df.iloc[27, 1:24].tolist()]
    growth_revenues =    [v * fx for v in df.iloc[25, 1:24].tolist()]
    growth_margins =     [v * fx for v in df.iloc[28, 1:24].tolist()]
    growth_percentages = df.iloc[29, 1:24].tolist()

    day1_results_df = financial_retrieval(day1_costs, day1_revenues, day1_margins, day1_percentages)
    growth_results_df = financial_retrieval(growth_costs, growth_revenues, growth_margins, growth_percentages)

    return day1_results_df, growth_results_df

def rebate_data_processing(rebate_df):
    import pandas as pd

    processed_revenue = [revenue * 1000 for revenue in rebate_df["Revenue"]]
    processed_percentage = [percentage * 100 for percentage in rebate_df["Percentage"]]

    data = {
        "Category": ["Total Product", "Total Services", "Pan HPE"],
        "Revenue": processed_revenue,
        "Percentage": processed_percentage
    }

    return pd.DataFrame(data)

def rebate_read(df):
    import pandas as pd

    currency, rate, fx = currency_read(df)

    day1_rebate = pd.DataFrame({
        "Category": ["Product", "Services", "Pan HPE"],
        "Revenue": [
            df.iloc[48, 6] * fx,
            df.iloc[48, 17] * fx,
            df.iloc[48, 18] * fx
        ],
        "Percentage": [
            df.iloc[49, 6],
            df.iloc[49, 17],
            df.iloc[49, 18]
        ]
    })

    growth_rebate = pd.DataFrame({
        "Category": ["Product", "Services", "Pan HPE"],
        "Revenue": [
            df.iloc[31, 6] * fx,
            df.iloc[31, 17] * fx,
            df.iloc[31, 18] * fx
        ],
        "Percentage": [
            df.iloc[32, 6],
            df.iloc[32, 17],
            df.iloc[32, 18]
        ]
    })

    day1_rebate = rebate_data_processing(day1_rebate)
    growth_rebate = rebate_data_processing(growth_rebate)

    return day1_rebate, growth_rebate

def dynamic_options_selector(results_df):

    prod_total_row = results_df[results_df['Category'] == 'Total Product']
    total_prod_cost = prod_total_row['Cost'].values[0] if not prod_total_row.empty else 0

    serv_total_row = results_df[results_df['Category'] == 'Total Services']
    total_serv_cost = serv_total_row['Cost'].values[0] if not serv_total_row.empty else 0

    aps_total_row = results_df[results_df['Category'] == 'Total A&PS']
    total_aps_cost = aps_total_row['Cost'].values[0] if not aps_total_row.empty else 0

    available_options = ["All"]

    if total_prod_cost > 0:
        available_options.append("Products Only")

    if total_serv_cost > 0:
        available_options.append("Services Only")

    if total_aps_cost > 0:
        available_options.append("A&PS Only")

    return available_options

def load_data(uploaded_file):
    import pandas as pd

    try:
        sheet_name = "PL_MGMT Edit"
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, engine='openpyxl')
        st.success("Custom File Loaded")
    except:
        sheet_name = "PL_MGMT"
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, engine='openpyxl')
        st.success("File Loaded")

    day1_df, growth_df = pl_mgmt_read(df)
    sales_motion = model_header_read(df)
    currency, rate, fx = currency_read(df)

    day1_rebate = 0
    growth_rebate = 0

    if sales_motion == "Indirect":
        day1_rebate, growth_rebate = rebate_read(df)

    return day1_df, growth_df, sales_motion, day1_rebate, growth_rebate, currency, rate

def view_option_select(view_option, results_df):
    from public import config

    if view_option == "Products Only":
        plot_df = results_df[results_df['Category'].isin(config.product_cats)]
        table_df = results_df[results_df['Category'].isin(config.product_cats + ["Total Product"])]

        total_cost = table_df[table_df['Category'] == 'Total Product']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total Product']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total Product']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total Product']['Percentage'].values[0]

    elif view_option == "Services Only":
        plot_df = results_df[results_df['Category'].isin(config.service_cats)]
        table_df = results_df[results_df['Category'].isin(config.service_cats + ["Total Services"])]

        total_cost = table_df[table_df['Category'] == 'Total Services']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total Services']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total Services']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total Services']['Percentage'].values[0]

    elif view_option == "A&PS Only":
        plot_df = results_df[results_df['Category'].isin(config.aps_cats)]
        table_df = results_df[results_df['Category'].isin(config.aps_cats + ["Total A&PS"])]

        total_cost = table_df[table_df['Category'] == 'Total A&PS']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Total A&PS']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Total A&PS']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Total A&PS']['Percentage'].values[0]

    else:
        plot_df = results_df[(results_df['Category'] != "Total Product") &
                                (results_df['Category'] != "Total Services") &
                                (results_df['Category'] != "Total A&PS") &
                                (results_df['Category'] != "Pan HPE") &
                                (results_df['Category'] != "Total Products+Services")]

        table_df = results_df

        total_cost = table_df[table_df['Category'] == 'Pan HPE']['Cost'].values[0]
        total_revenue = table_df[table_df['Category'] == 'Pan HPE']['Revenue'].values[0]
        total_margin = table_df[table_df['Category'] == 'Pan HPE']['Margin'].values[0]
        total_percentage = table_df[table_df['Category'] == 'Pan HPE']['Percentage'].values[0]

    filtered_plot_df = plot_df[(plot_df['Cost'] > 0) | (plot_df['Margin'] != 0)]
    filtered_table_df = table_df[(table_df['Cost'] > 0) | (table_df['Margin'] != 0)]

    filtered_table_df = filtered_table_df[~(~filtered_table_df['Category'].eq('Total A&PS').any() & filtered_table_df['Category'].eq('Total Products+Services'))]

    return filtered_plot_df, filtered_table_df, total_cost, total_revenue, total_margin, total_percentage

def footer_message():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #808495; font-size: 12px; padding: 15px;'>
            <p style='margin: 5px 0;'>
                <strong>GreenLake Pulse - Finance Analytics Dashboard</strong> v1.2.0303
            </p>
            <p style='margin: 5px 0;'>
                Built using Streamlit & Plotly | 
                <a href='mailto:sebastian.mayorga@hpe.com' style='color: #01a982; text-decoration: none;'>Contact Support</a>
            </p>
            <p style='margin: 5px 0; font-size: 10px;'>
                © 2026 GreenLake Presales Team | For internal use only
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def consolidate_models(dfs: list):
    """
    Consolidate a list of DataFrames by summing Cost, Revenue and Margin,
    then recalculating Percentage (FLGM%) as Margin / Revenue * 100.
    """
    import pandas as pd

    valid_dfs = [df for df in dfs if isinstance(df, pd.DataFrame) and not df.empty]

    if not valid_dfs:
        return pd.DataFrame()
    if len(valid_dfs) == 1:
        return valid_dfs[0].copy()

    ref_df = valid_dfs[0].copy()

    sum_cols = [c for c in ref_df.select_dtypes(include="number").columns if c != "Percentage"]

    for col in sum_cols:
        ref_df[col] = sum(
            df.set_index("Category")[col].reindex(ref_df["Category"]).fillna(0).values
            for df in valid_dfs
        )

    if "Margin" in ref_df.columns and "Percentage" in ref_df.columns:
        ref_df["Percentage"] = ref_df.apply(
            lambda row: (row["Margin"] / row["Revenue"] * 100) if row["Revenue"] != 0 else 0.0,
            axis=1,
        )
    elif "Percentage" in ref_df.columns and "Revenue" in ref_df.columns:
        weighted_pct = sum(
            df.set_index("Category")["Percentage"].reindex(ref_df["Category"]).fillna(0).values *
            df.set_index("Category")["Revenue"].reindex(ref_df["Category"]).fillna(0).values
            for df in valid_dfs
        )
        total_rev = ref_df["Revenue"].replace(0, float("nan"))
        ref_df["Percentage"] = weighted_pct / total_rev.values
        ref_df["Percentage"] = ref_df["Percentage"].fillna(0)

    return ref_df