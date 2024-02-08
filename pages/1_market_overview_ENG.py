import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import numpy as np
from plotly.subplots import make_subplots
import math

st.set_page_config(
    page_title="Main",
    page_icon=None,  
    layout="wide",
    initial_sidebar_state="expanded"
    )

# Load Data
@st.cache_data
def load_data():
    # Load csv file
    data = pd.read_csv('data/data.csv', index_col=0)

    # Handle N/A
    data = data.dropna(subset=['BUILD_YEAR'])

    # Extract deal year, month
    data['datetime'] = pd.to_datetime(data['DEAL_YMD'], format="%Y%m%d")
    data['deal_year'] = data['datetime'].dt.year
    data['deal_month'] = data['datetime'].dt.month

    return data

@st.cache_data
def load_data2():
    rent = pd.read_csv("data/rent.csv", index_col=0)
    rent['datetime'] = pd.to_datetime(rent['계약일'], format="%Y%m%d")
    rent['년'] = rent['datetime'].dt.year
    rent['월'] = rent['datetime'].dt.month
    return rent

def main():
    df = load_data()
    rent = load_data2()

    # Dashboard Menu
    with st.sidebar:
        selected = option_menu("Index", ["Overview", "Exploratory Analysis", "Correlation Analysis"],
                            icons=['house', 'bar-chart-steps', 'kanban'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "5!important", "background-color": "#black"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
        )
        SGG_NM = st.selectbox("Select a Region.", sorted(list(df['SGG_NM'].unique())))
        deal_year = st.radio("Selece a Year.", sorted(list(df['deal_year'].unique())))
        unique_month = sorted(df[df['deal_year'] == deal_year]['deal_month'].unique())

        deal_month = st.selectbox("Select a Month.", unique_month)
            
        st.markdown(f'Chosen: <font color="green">{deal_year}/{deal_month}</font>', unsafe_allow_html=True)


    # Distrct, Year, Month Filter
    sgg_select = df.loc[df['SGG_NM'] == SGG_NM, :]
    year_select = sgg_select.loc[sgg_select['deal_year'] == deal_year, :]
    month_select = year_select.loc[year_select['deal_month'] == deal_month, :]

    # House Type Filter
    house1 = month_select[month_select['HOUSE_TYPE']=='아파트']
    house2 = month_select[month_select['HOUSE_TYPE']=='오피스텔']
    house3 = month_select[month_select['HOUSE_TYPE']=='연립다세대']
    house4 = month_select[month_select['HOUSE_TYPE']=='단독다가구']

    # Rent Data Filter
    rent_sgg = rent.loc[rent['자치구명'] == SGG_NM, :]
    rent_mon = rent_sgg.loc[rent_sgg['월'] == deal_month, :]

    # Average Price, Total Transaction
    mean_price = math.ceil(month_select['OBJ_AMT'].mean())
    mean_prev = math.ceil(month_select['OBJ_AMT'].shift(1).mean())

    ttl_count = month_select.shape[0]

    # Menu 1
    if selected == "Overview":
        st.header("✨Seoul✨ Real Estate Dashboard")
        st.divider()
        st.subheader("Apartment Price for " + str(deal_month) + "." + str(deal_year) + " in " + str(SGG_NM) )

        st.write('Click on the district, year, and month on the left. ')
        st.write('You can view the average sales price, total transaction volume, minimum & maximum transaction price for each district.')
        st.write("")
        st.write("")

        # KPI
        kpi1, kpi2 = st.columns(2)   

        with st.container():
            kpi1.metric(
            label = "Average Sales Price (10,000won)",
            value = '{:,}'.format(mean_price),
            delta = '{:,}'.format(mean_price - mean_prev)
            )

            kpi2.metric(
                label= "Total Transaction",
                value='{:,}'.format(ttl_count)
                , delta= '3.56%'
            )

        with st.container():
            kpi3, kpi4 = st.columns(2)   
            kpi1.metric(
                label = "Min. Transaction (10,000won)",
                value = '{:,}'.format(house1['OBJ_AMT'].min())
                )

            kpi2.metric(
                label= "Max. Transaction (10,000won)",
                value='{:,}'.format(house1['OBJ_AMT'].max()),
            )
        st.divider()

        # top10 Apt df
        top10_apt = house1.sort_values(by='OBJ_AMT', ascending=False).head(10).reset_index(drop=False)
        top10_apt = top10_apt[['SGG_NM', 'BJDONG_NM', 'BLDG_NM', 'OBJ_AMT']]
        
        # bottom10 Apt df
        bottom10_apt = house1.sort_values(by='OBJ_AMT').head(10).reset_index(drop=False)
        bottom10_apt = bottom10_apt[['SGG_NM', 'BJDONG_NM', 'BLDG_NM', 'OBJ_AMT']]

        # Format 'OBJ_AMT' column with commas
        top10_apt['OBJ_AMT'] = top10_apt['OBJ_AMT'].apply(lambda x: "{:,}".format(x))
        bottom10_apt['OBJ_AMT'] = bottom10_apt['OBJ_AMT'].apply(lambda x: "{:,}".format(x))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 10 Apartments🌿")
            st.dataframe(top10_apt, 
                        column_config={
                            'SGG_NM': 'District',
                            'BJDONG_NM': 'Dong',
                            'BLDG_NM':'Apt. Name', 
                            'OBJ_AMT':'Price'
                            },
                        width=600, height=390
                        )
        
        st.divider()

        with col2:
            st.subheader("Lowest 10 Apartments🍁")
            st.dataframe(bottom10_apt, 
                        column_config={
                            'SGG_NM': 'District',
                            'BJDONG_NM': 'Dong',
                            'BLDG_NM':'Apt. Name', 
                            'OBJ_AMT':'Price'},
                        width=600, height=390)

    # Menu 2
    elif selected == "Exploratory Analysis":
        st.header("Exploratory Analysis")
        tab1, tab2, tab3 = st.tabs(['Home', 'Ratio', 'Trend'])

        # Sub-Menu 1
        with tab1: # Home
                st.subheader("1. Ratio Analysis")
                st.write("- Sales Ratio by House Type")
                st.write("- Ratio for Rents")
                st.write("")

                st.subheader("2. Analysis by House Type")
                st.write("- Seoul: Price Trends by House Type")
                st.write("- Price Trends by District & House Type")
                st.write("- Transaction Trends by District & House Type")

        # Sub-Menu 2
        with tab2:
            st.subheader("📝" + " Information for " + str(deal_month) + "." + str(deal_year) + " in " + str(SGG_NM) )

            # Tab2, Chart1 - Sales Ratio by House Type
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(month_select, values='OBJ_AMT', names='HOUSE_TYPE', title='Sales Ratio by House Type')
                st.plotly_chart(fig)

            # Tab2, Chart2 - Ratio for Rents
            with col2:
                fig = px.pie(rent_mon, values='계약일', names='전월세구분', title='Rent Ratio',
                            # color_discrete_sequence=px.colors.sequential.RdBu
                            )
                st.plotly_chart(fig)

            col1, col2 = st.columns(2)

            # Tab2, Chart3 - Rent Variance
            with col1:
                rent_mon = rent.loc[rent['월'] == deal_month, :]
                rent_mon['임대료증감'] = rent_mon['임대료(만원)'] - rent_mon['종전임대료']
                rent_mon['보증금증감'] = rent_mon['보증금(만원)'] - rent_mon['종전보증금']

                fig = px.bar(rent_mon, x='자치구명', y='임대료증감', 
                            title='Rent Variance', color_discrete_sequence=['#FFB2AF'])
                
                fig.update_yaxes(showticklabels=False)
                fig.update_layout(xaxis_title='', yaxis_title="")
                st.plotly_chart(fig)

            # Tab2, Chart4 - Deposit Variance
            with col2:
                fig = px.bar(rent_mon, x='자치구명', y='보증금증감', title='Deposit Variance',
                             color_discrete_sequence=['#1E90FF'])
                fig.update_yaxes(showticklabels=False)
                fig.update_layout(xaxis_title='', yaxis_title="")
                st.plotly_chart(fig)

        # Sub-Menu 3
        with tab3:
            with st.sidebar:
                chart_select = st.radio('Select a Chart.', [
                    'Seoul: Price Trends by House Type', 'Price Trends by District & House Type', 'Transaction Trends by District & House Type'
                    ])

            # Tab3, Chart1 - Seoul: Price Trends by House Type
            if chart_select == "Seoul: Price Trends by House Type":
                st.subheader("📊" + "Price Trends for " + str(deal_month) + "." + str(deal_year) + " in Seoul")
                st.write("")
                
                # Year, Month, HouseType Filter
                year_sel = df[df['deal_year'] == deal_year]
                month_sel = year_sel[year_sel['deal_month'] == deal_month]
                house1 = month_sel[month_sel['HOUSE_TYPE']=='아파트']
                house2 = month_sel[month_sel['HOUSE_TYPE']=='오피스텔']
                house3 = month_sel[month_sel['HOUSE_TYPE']=='연립다세대']
                house4 = month_sel[month_sel['HOUSE_TYPE']=='단독다가구']

                # Select HouseType
                house_sel = st.radio('House Type:', ['Apartment', 'Studio Flat', 'Vila type1', 'Vila type2'])

                if house_sel == 'Apartment':
                    fig = px.bar(house1, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='Price(10,000won)'))
                    st.plotly_chart(fig)
                elif house_sel == 'Studio Flat':
                    fig = px.bar(house2, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='Price(10,000won)'))
                    st.plotly_chart(fig)
                elif house_sel == 'Vila type1':
                    fig = px.bar(house3, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='Price(10,000won)'))
                    st.plotly_chart(fig)
                elif house_sel == 'Vila type2':
                    fig = px.bar(house4, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='Price(10,000won)'))
                    st.plotly_chart(fig)   

            # Price Trends by District & House Type
            elif chart_select == "Price Trends by District & House Type":
                st.subheader("📈" + "Price Trends for " + str(deal_month) + "." + str(deal_year) + " in " + str(SGG_NM))

                fig = make_subplots(rows=2, cols=2)
                fig.add_trace(
                    go.Scatter(x=house1['datetime'], y=house1['OBJ_AMT'], mode='lines+markers', name='Apartment'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=house2['datetime'], y=house2['OBJ_AMT'], mode='lines+markers', name="Studio Flat"),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(x=house3['datetime'], y=house3['OBJ_AMT'], mode='lines+markers', name='Vila type1'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=house4['datetime'], y=house4['OBJ_AMT'], mode='lines+markers', name='Vila type2'),
                    row=2, col=2
                )

                fig.update_xaxes(showticklabels=False, row=1, col=1)
                fig.update_xaxes(showticklabels=False, row=1, col=2)
                fig.update_xaxes(showticklabels=False, row=2, col=1)
                fig.update_xaxes(showticklabels=False, row=2, col=2)

                # dtick=50000, range=[0, 150000],
                fig.update_yaxes(tickformat=',', title_text='Price(10,000won)', row=1, col=1)
                fig.update_yaxes(tickformat=',', title_text='Price(10,000won)', row=1, col=2)
                fig.update_yaxes(tickformat=',', title_text='Price(10,000won)', row=2, col=1)
                fig.update_yaxes(tickformat=',', title_text='Price(10,000won)', row=2, col=2)

                fig.update_layout(width=1000, height=600)
                st.plotly_chart(fig)

            # Tab3, Chart3 - Transaction Trends by District & House Type
            elif chart_select == "Transaction Trends by District & House Type":
                st.subheader("📉" + "Transaction Trends for " + str(deal_month) + "." + str(deal_year) + " in " + str(SGG_NM))

                cnt1 = house1.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt2 = house2.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt3 = house3.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt4 = house4.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")

                fig = make_subplots(rows=2, cols=2)
                fig.add_trace(
                    go.Scatter(x=cnt1['datetime'], y=cnt1['counts'], mode='lines+markers', name='Apartment'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=cnt2['datetime'], y=cnt2['counts'], mode='lines+markers', name="Studio Flat"),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(x=cnt3['datetime'], y=cnt3['counts'], mode='lines+markers', name='Vila type1'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=cnt4['datetime'], y=cnt4['counts'], mode='lines+markers', name='Vila type2'),
                    row=2, col=2
                )

                fig.update_xaxes(showticklabels=False, row=1, col=1)
                fig.update_xaxes(showticklabels=False, row=1, col=2)
                fig.update_xaxes(showticklabels=False, row=2, col=1)
                fig.update_xaxes(showticklabels=False, row=2, col=2)

                fig.update_yaxes(tickformat=',', title_text='Transactions', row=1, col=1)
                fig.update_yaxes(tickformat=',', title_text='Transactions', row=1, col=2)
                fig.update_yaxes(tickformat=',', title_text='Transactions', row=2, col=1)
                fig.update_yaxes(tickformat=',', title_text='Transactions', row=2, col=2)

                fig.update_layout(width=1000, height=600)
                st.plotly_chart(fig)

    elif selected == "Correlation Analysis":
        st.subheader("📉" + "Correlation between Build Year and Price by District")
        
        fig = px.density_heatmap(house1, x="BUILD_YEAR", y="OBJ_AMT", 
                #  color_continuous_scale=["#2828CD", "#FFEB46"]
                color_continuous_scale="Viridis"
                 )

        fig.update_layout(
            yaxis=dict(showticklabels=False),
            xaxis_title="Build Year ",
            yaxis_title="Price"
        )

        st.plotly_chart(fig)

        with st.expander("See explanation"):
            st.write('''
            This density heatmap visually represents the distribution of apartment sales prices in Seoul according to the year of construction. 
                     It enables a visual understanding of the correlation between variables. 
                     Higher density is indicated by yellowish colors, while lower density tends towards purple.
            ''')

if __name__ == "__main__":
    main()
