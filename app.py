import streamlit as st 
from PIL import Image
from functions.processing import resource_path, local_css, footer_message

icon_path = resource_path("assets/HPE_icon.webp")

# Session state initialization
if 'figures' not in st.session_state:
    st.session_state.figures = {}
if 'models' not in st.session_state:
    st.session_state.models = {}
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'previous_scenario' not in st.session_state:
    st.session_state.previous_scenario = None
if 'previous_view' not in st.session_state:
    st.session_state.previous_view = None
if 'previous_chart_type' not in st.session_state:
    st.session_state.previous_chart_type = None
if 'previous_model_selection' not in st.session_state:
    st.session_state.previous_model_selection = None

# Page config
st.set_page_config(
    page_title="GreenLake Pulse",
    page_icon=Image.open(icon_path),
    layout="wide"
)

local_css("style.css")

st.title("GreenLake Pulse")
st.subheader("Finance Analytics Dashboard")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 - Data Ingestion
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("#### 1. Data Ingestion")

uploaded_file = st.file_uploader(
    "Upload an Excel model file (you can load multiple models one by one)",
    type=["xlsx"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file:
    with st.spinner("Loading modules..."):
        from functions.processing import dynamic_options_selector, load_data, view_option_select, consolidate_models
        from functions.graphicator import graph_type_selector, table_generation, rebate_graph_type_selector
        from functions.download import save_individual_chart, save_all_charts_zip_button, render_export_buttons

    model_name = uploaded_file.name.replace(".xlsx", "")

    if model_name not in st.session_state.models:
        try:
            day1_df, growth_df, sales_motion, day1_rebate, growth_rebate = load_data(uploaded_file)
            st.session_state.models[model_name] = {
                "day1_df": day1_df,
                "growth_df": growth_df,
                "sales_motion": sales_motion,
                "day1_rebate": day1_rebate,
                "growth_rebate": growth_rebate,
            }
            st.session_state.figures = {}
            st.session_state.previous_model_selection = None
            st.toast(f"Model '{model_name}' loaded!")
        except Exception as e:
            st.error(f"Error loading '{model_name}': {e}")
    else:
        pass

# Loaded Models Cards
if st.session_state.models:
    st.markdown("##### Loaded Models")

    n_models = len(st.session_state.models)
    card_cols = st.columns(min(n_models, 5))
    models_to_delete = []

    for i, (mname, mdata) in enumerate(st.session_state.models.items()):
        with card_cols[i % 5]:
            sm = mdata["sales_motion"]
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #01A982;
                    border-radius: 8px;
                    padding: 10px 14px;
                    margin-bottom: 6px;
                    background: #f4fefb;
                ">
                    <span style="color:#01A982; font-weight:bold;">{mname}</span><br>
                    <small style="color:#555;">Sales Motion: <b>{sm}</b></small>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Remove", key=f"del_{mname}", use_container_width=True):
                models_to_delete.append(mname)

    if models_to_delete:
        for mname in models_to_delete:
            del st.session_state.models[mname]
        st.session_state.figures = {}
        st.session_state.previous_model_selection = None
        st.session_state.uploader_key += 1
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 - Financial Analysis
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.models:

    from functions.processing import dynamic_options_selector, view_option_select, consolidate_models
    from functions.graphicator import graph_type_selector, table_generation, rebate_graph_type_selector
    from functions.download import save_individual_chart, save_all_charts_zip_button, render_export_buttons

    st.write("#### 2. Financial Analysis Breakdown")

    model_options = list(st.session_state.models.keys())

    if len(model_options) > 1:
        selector_options = model_options + ["Consolidated - All Models"]
    else:
        selector_options = model_options

    # Model selector + Scenario
    col_model, col_scenario = st.columns([3, 1])

    with col_model:
        model_selection = st.selectbox("Select Model", selector_options)

    with col_scenario:
        scenario_option = st.selectbox("Select Scenario", ["Day 1", "Growth"])

    # Resolve active dataframes
    is_consolidated = model_selection == "Consolidated - All Models"

    if is_consolidated:
        scenario_key = "day1_df" if scenario_option == "Day 1" else "growth_df"
        rebate_key   = "day1_rebate" if scenario_option == "Day 1" else "growth_rebate"

        results_df = consolidate_models(
            [st.session_state.models[m][scenario_key] for m in model_options]
        )

        indirect_rebates = [
            st.session_state.models[m][rebate_key]
            for m in model_options
            if st.session_state.models[m]["sales_motion"] == "Indirect"
            and not isinstance(st.session_state.models[m][rebate_key], int)
        ]
        rebate_df = consolidate_models(indirect_rebates) if indirect_rebates else 0

        motions      = list({st.session_state.models[m]["sales_motion"] for m in model_options})
        sales_motion = motions[0] if len(motions) == 1 else "Mixed"
        model_label  = "Consolidated - All Models"

    else:
        mdata = st.session_state.models[model_selection]
        if scenario_option == "Day 1":
            results_df = mdata["day1_df"]
            rebate_df  = mdata["day1_rebate"]
        else:
            results_df = mdata["growth_df"]
            rebate_df  = mdata["growth_rebate"]
        sales_motion = mdata["sales_motion"]
        model_label  = model_selection

    # View / chart selectors + ZIP placeholder
    available_options = dynamic_options_selector(results_df)

    col_filter1, col_filter2 = st.columns([4, 1])

    with col_filter1:
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            view_option = st.selectbox("Select View", available_options)
        with sub_col2:
            chart_type = st.selectbox("Chart Style", ["Bar Charts", "Donut Charts"])

    with col_filter2:
        st.write("")
        st.write("")
        zip_button_placeholder = st.empty()

    st.markdown("---")

    st.markdown(f"##### {model_label}")
    # st.info(f"Sales Motion: {sales_motion}")

    # Clear chart cache when any filter changes
    current_state  = (scenario_option, view_option, chart_type, model_selection)
    previous_state = (
        st.session_state.previous_scenario,
        st.session_state.previous_view,
        st.session_state.previous_chart_type,
        st.session_state.previous_model_selection,
    )

    if current_state != previous_state:
        st.session_state.figures = {}
        st.session_state.previous_scenario        = scenario_option
        st.session_state.previous_view            = view_option
        st.session_state.previous_chart_type      = chart_type
        st.session_state.previous_model_selection = model_selection

    # Filter data
    filtered_plot_df, filtered_table_df, total_cost, total_revenue, total_margin, total_percentage = \
        view_option_select(view_option, results_df)

    # Charts
    if not filtered_table_df.empty:

        # Row 1
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            fig, filename = graph_type_selector(
                filtered_plot_df, chart_type, 'Cost',
                total_cost, total_revenue, total_margin, total_percentage,
                scenario_option, view_option
            )
            st.session_state.figures['cost'] = {'fig': fig, 'filename': filename}
            save_individual_chart('cost', st.session_state.figures['cost'])

        with row1_col2:
            fig, filename = graph_type_selector(
                filtered_plot_df, chart_type, 'Revenue',
                total_cost, total_revenue, total_margin, total_percentage,
                scenario_option, view_option
            )
            st.session_state.figures['revenue'] = {'fig': fig, 'filename': filename}
            save_individual_chart('revenue', st.session_state.figures['revenue'])

        # Row 2
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            fig, filename = graph_type_selector(
                filtered_plot_df, chart_type, 'Margin',
                total_cost, total_revenue, total_margin, total_percentage,
                scenario_option, view_option
            )
            st.session_state.figures['margin_pre_rebate'] = {'fig': fig, 'filename': filename}
            save_individual_chart('margin_pre_rebate', st.session_state.figures['margin_pre_rebate'])

        with row2_col2:
            if sales_motion == "Indirect" and chart_type == "Donut Charts":
                fig = rebate_graph_type_selector(rebate_df, chart_type, 'Revenue', scenario_option, view_option)
                if fig:
                    filename = f"{scenario_option}_Revenue_post_rebate_by{view_option.replace(' ', '_')}_Segment.png"
                    st.session_state.figures['revenue_post_rebate'] = {'fig': fig, 'filename': filename}
                    save_individual_chart('revenue_post_rebate', st.session_state.figures['revenue_post_rebate'])
            else:
                fig, filename = graph_type_selector(
                    filtered_plot_df, chart_type, 'Percentage',
                    total_cost, total_revenue, total_margin, total_percentage,
                    scenario_option, view_option
                )
                st.session_state.figures['percentage'] = {'fig': fig, 'filename': filename}
                save_individual_chart('percentage', st.session_state.figures['percentage'])

        # Row 3 - Rebate (Indirect only)
        if sales_motion == "Indirect":
            row3_col1, row3_col2 = st.columns(2)

            with row3_col1:
                if chart_type == "Bar Charts":
                    fig = rebate_graph_type_selector(rebate_df, chart_type, 'Revenue', scenario_option, view_option)
                    if fig:
                        filename = f"{scenario_option}_Revenue_post_rebate_by{view_option.replace(' ', '_')}_Segment.png"
                        st.session_state.figures['revenue_post_rebate'] = {'fig': fig, 'filename': filename}
                        save_individual_chart('revenue_post_rebate', st.session_state.figures['revenue_post_rebate'])

            with row3_col2:
                if chart_type == "Bar Charts":
                    fig = rebate_graph_type_selector(rebate_df, chart_type, 'Percentage', scenario_option, view_option)
                    if fig:
                        filename = f"{scenario_option}_Percentage_post_rebate_by{view_option.replace(' ', '_')}_Segment.png"
                        st.session_state.figures['percentage_post_rebate'] = {'fig': fig, 'filename': filename}
                        save_individual_chart('percentage_post_rebate', st.session_state.figures['percentage_post_rebate'])

    # ZIP button
    with zip_button_placeholder.container():
        save_all_charts_zip_button(st.session_state.figures)

    # Summary Table
    st.write("#### Data Summary")
    if not filtered_table_df.empty:
        html_table = table_generation(filtered_table_df)
        st.markdown(html_table, unsafe_allow_html=True)

    # Additional Exports
    st.write("#### 3. Additional Exports")
    render_export_buttons()

    footer_message()

else:
    st.warning("Awaiting file upload...")
    footer_message()