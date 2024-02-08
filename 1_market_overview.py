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
    page_title="메인",
    page_icon=None,  # 아이콘 없음
    layout="wide",
    initial_sidebar_state="expanded"
    )

# 데이터 로딩
@st.cache_data
def load_data():
    # csv파일 불러오기
    data = pd.read_csv('data/data.csv', index_col=0)

    # 결측치 처리
    data = data.dropna(subset=['BUILD_YEAR'])

    # 거래일자 년월 추출
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

    # 대시보드 메뉴
    with st.sidebar:
        selected = option_menu("Index", ["Overview", "탐색적 자료분석", "상관관계 분석"],
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


    # 시군구, 연,월 필터
    sgg_select = df.loc[df['SGG_NM'] == SGG_NM, :]
    year_select = sgg_select.loc[sgg_select['deal_year'] == deal_year, :]
    month_select = year_select.loc[year_select['deal_month'] == deal_month, :]
    # month_select['prev_month'] = month_select['deal_month'] - 1 # 잘못된 코드

    # 주거타입 필터
    house1 = month_select[month_select['HOUSE_TYPE']=='아파트']
    house2 = month_select[month_select['HOUSE_TYPE']=='오피스텔']
    house3 = month_select[month_select['HOUSE_TYPE']=='연립다세대']
    house4 = month_select[month_select['HOUSE_TYPE']=='단독다가구']

    # 전월세 데이터 필터
    rent_sgg = rent.loc[rent['자치구명'] == SGG_NM, :]
    rent_mon = rent_sgg.loc[rent_sgg['월'] == deal_month, :]

    # 평균가, 총 거래량
    mean_price = math.ceil(month_select['OBJ_AMT'].mean())
    mean_prev = math.ceil(month_select['OBJ_AMT'].shift(1).mean())

    ttl_count = month_select.shape[0]
    # cnt_prev = month_select['prev_month'].shape[0]

    # 메뉴1
    if selected == "Overview":
        st.header("✨Seoul✨ Real Estate Dashboard")
        st.divider()
        st.subheader(str(SGG_NM) + " " + str(deal_year) + "년 " + str(deal_month) + "월 아파트 시세 정보")
        st.write("자치구와 년, 월을 클릭하면 각 지역구의 평균 매매가, 총 거래량, 거래된 최소가격, 최대가격을 확인할 수 있습니다.")
        st.write("")

        # KPI
        kpi1, kpi2 = st.columns(2)

        with st.container():
            kpi1.metric(
            label = SGG_NM + " 평균 매매가 (만원)",
            value = '{:,}'.format(mean_price),
            delta = '{:,}'.format(mean_price - mean_prev) + "만원"
            )

            kpi2.metric(
                label= SGG_NM + " 총 거래량",
                value='{:,}'.format(ttl_count)
                , delta= '3.56%'
            )

        with st.container():
            kpi3, kpi4 = st.columns(2)
            kpi1.metric(
                label = SGG_NM + " 최소 매매가 (만원)",
                value = '{:,}'.format(house1['OBJ_AMT'].min())
                )

            kpi2.metric(
                label= SGG_NM + " 최대 매매가 (만원)",
                value='{:,}'.format(house1['OBJ_AMT'].max()),
            )
        st.divider()

        # top10 아파트 df
        top10_apt = house1.sort_values(by='OBJ_AMT', ascending=False).head(10).reset_index(drop=False)
        top10_apt = top10_apt[['SGG_NM', 'BJDONG_NM', 'BLDG_NM', 'OBJ_AMT']]

        # bottom10 아파트 df
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
                            'SGG_NM': '자치구',
                            'BJDONG_NM': '법정동',
                            'BLDG_NM':'아파트명',
                            'OBJ_AMT':'건물가격'
                            },
                        width=600, height=390
                        )

        st.divider()

        with col2:
            st.subheader("Lowest 10 Apartments🍁")
            st.dataframe(bottom10_apt,
                        column_config={
                            'SGG_NM': '자치구',
                            'BJDONG_NM': '법정동',
                            'BLDG_NM':'아파트명',
                            'OBJ_AMT':'건물가격'},
                        width=600, height=390)

    # 메뉴2
    elif selected == "탐색적 자료분석":
        st.header("탐색적 자료분석")
        tab1, tab2, tab3 = st.tabs(['Home', 'Ratio', 'Trend'])

        # 서브메뉴1
        with tab1: # Home
                st.subheader("1. 비율 분석")
                st.write("- 주거유형 별 매매 비율")
                st.write("- 전월세 비율")
                st.write("")

                st.subheader("2. 주거유형별 분석")
                st.write("- 서울시 주거유형별 시세 추이")
                st.write("- 주거유형별 시세 추이")
                st.write("- 주거유형별 거래 건수 추이")

        # 서브메뉴2
        with tab2:
            st.subheader("📝" + str(SGG_NM) + " " + str(deal_year) + "년 " + str(deal_month) + "월 정보")

            # 탭2 차트1 - 주거유형 별 매매 비율
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(month_select, values='OBJ_AMT', names='HOUSE_TYPE', title='주거유형 별 매매 비율')
                st.plotly_chart(fig)

            # 탭2 차트2 - 전월세 비율
            with col2:
                fig = px.pie(rent_mon, values='계약일', names='전월세구분', title='전월세 비율',
                            # color_discrete_sequence=px.colors.sequential.RdBu
                            )
                st.plotly_chart(fig)

            col1, col2 = st.columns(2)

            # 탭2 차트3 - 임대료 증감률
            with col1:
                rent_mon = rent.loc[rent['월'] == deal_month, :]
                rent_mon['임대료증감'] = rent_mon['임대료(만원)'] - rent_mon['종전임대료']
                rent_mon['보증금증감'] = rent_mon['보증금(만원)'] - rent_mon['종전보증금']

                fig = px.bar(rent_mon, x='자치구명', y='임대료증감',
                            title='임대료 증감률', color_discrete_sequence=['#FFB2AF'])

                fig.update_yaxes(showticklabels=False)
                fig.update_layout(xaxis_title='', yaxis_title="")
                st.plotly_chart(fig)

            # 탭2 차트4 - 보증금 증감률
            with col2:
                fig = px.bar(rent_mon, x='자치구명', y='보증금증감', title='보증금 증감률',
                             color_discrete_sequence=['#1E90FF'])
                fig.update_yaxes(showticklabels=False)
                fig.update_layout(xaxis_title='', yaxis_title="")
                st.plotly_chart(fig)

        # 서브메뉴3
        with tab3:
            with st.sidebar:
                chart_select = st.radio('Select a Chart.', [
                    '서울시 주거유형별 시세 추이', '주거유형별 시세 추이', '주거유형별 거래 건수 추이'
                    ])

            # 탭3 차트1 - 서울시 주거유형별 시세 추이
            if chart_select == "서울시 주거유형별 시세 추이":
                st.subheader("📊" + "서울시 주거유형별 " + str(deal_year) + "년 " + str(deal_month) + "월 시세 추이")
                st.write("")

                # 연,월,주거타입 필터
                year_sel = df[df['deal_year'] == deal_year]
                month_sel = year_sel[year_sel['deal_month'] == deal_month]
                house1 = month_sel[month_sel['HOUSE_TYPE']=='아파트']
                house2 = month_sel[month_sel['HOUSE_TYPE']=='오피스텔']
                house3 = month_sel[month_sel['HOUSE_TYPE']=='연립다세대']
                house4 = month_sel[month_sel['HOUSE_TYPE']=='단독다가구']

                # 주거유형 선택 버튼
                house_sel = st.radio('House Type:', ['아파트', '오피스텔', '연립다세대', '단독다가구'])

                if house_sel == '아파트':
                    fig = px.bar(house1, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)
                elif house_sel == '오피스텔':
                    fig = px.bar(house2, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)
                elif house_sel == '연립다세대':
                    fig = px.bar(house3, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)
                elif house_sel == '단독다가구':
                    fig = px.bar(house4, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)

            # 탭3 차트2 - 지역별, 주거유형별 시세 추이
            elif chart_select == "주거유형별 시세 추이":
                st.subheader("📈" + str(SGG_NM) + " " + str(deal_year) + "년 " + str(deal_month) + "월 주거유형별 시세 추이")

                fig = make_subplots(rows=2, cols=2)
                fig.add_trace(
                    go.Scatter(x=house1['datetime'], y=house1['OBJ_AMT'], mode='lines+markers', name='아파트'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=house2['datetime'], y=house2['OBJ_AMT'], mode='lines+markers', name="오피스텔"),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(x=house3['datetime'], y=house3['OBJ_AMT'], mode='lines+markers', name='연립다세대'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=house4['datetime'], y=house4['OBJ_AMT'], mode='lines+markers', name='단독다가구'),
                    row=2, col=2
                )

                fig.update_xaxes(showticklabels=False, row=1, col=1)
                fig.update_xaxes(showticklabels=False, row=1, col=2)
                fig.update_xaxes(showticklabels=False, row=2, col=1)
                fig.update_xaxes(showticklabels=False, row=2, col=2)

                # dtick=50000, range=[0, 150000],
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=1, col=1)
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=1, col=2)
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=2, col=1)
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=2, col=2)

                fig.update_layout(width=1000, height=600)
                st.plotly_chart(fig)

            # 탭3 차트3 - 서울시 주거유형별 거래 건수 추이
            elif chart_select == "주거유형별 거래 건수 추이":
                st.subheader("📉" + str(SGG_NM) + " " + str(deal_year) + "년 " + str(deal_month) + "월 주거유형별 거래 건수 추이")

                cnt1 = house1.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt2 = house2.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt3 = house3.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt4 = house4.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")

                fig = make_subplots(rows=2, cols=2)
                fig.add_trace(
                    go.Scatter(x=cnt1['datetime'], y=cnt1['counts'], mode='lines+markers', name='아파트'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=cnt2['datetime'], y=cnt2['counts'], mode='lines+markers', name="오피스텔"),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(x=cnt3['datetime'], y=cnt3['counts'], mode='lines+markers', name='연립다세대'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=cnt4['datetime'], y=cnt4['counts'], mode='lines+markers', name='단독다가구'),
                    row=2, col=2
                )

                fig.update_xaxes(showticklabels=False, row=1, col=1)
                fig.update_xaxes(showticklabels=False, row=1, col=2)
                fig.update_xaxes(showticklabels=False, row=2, col=1)
                fig.update_xaxes(showticklabels=False, row=2, col=2)

                # dtick=50000, range=[0, 150000],
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=1, col=1)
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=1, col=2)
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=2, col=1)
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=2, col=2)

                fig.update_layout(width=1000, height=600)
                st.plotly_chart(fig)

    elif selected == "상관관계 분석":
        st.subheader("📉" + "지역별 아파트 건축연도와 매매가 간 상관관계")

        fig = px.density_heatmap(house1, x="BUILD_YEAR", y="OBJ_AMT",
                #  color_continuous_scale=["#2828CD", "#FFEB46"]
                color_continuous_scale="Viridis"
                 )

        fig.update_layout(
            yaxis=dict(showticklabels=False),
            xaxis_title="건축연도 ",
            yaxis_title="매매가"
        )

        st.plotly_chart(fig)

        with st.expander("see explanation"):
            st.write('''
            이 밀도 히트맵은 건축연도에 따른 서울시 아파트 매매가의 분포를 시각적으로 나타냅니다.
                     이를 통해 변수 간의 상관 관계를 시각적으로 이해할 수 있습니다.
                     노란색에 가까울수록 밀도가 높아지며, 보라색에 가까울수록 밀도가 낮아지는 경향이 있습니다.
            ''')


if __name__ == "__main__":
    main()

