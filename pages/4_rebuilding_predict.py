# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly

import geopandas as gpd
from matplotlib import font_manager, rc

font_path = r"data/GULIM.TTC"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

@st.cache_data
def get_sliced_gpd():
    # fpd 불러오기
    sampled_gpd = gpd.read_file("data/sampled_data.geojson")
    # sampled_gpd

    sampled_gpd.drop(columns=['법정동명', '물건금액(만원)', '건물면적(㎡)', '층', '건축년도', '건물용도'], inplace=True)
    # sampled_gpd

    # 중복값 제거
    refined_gpd = sampled_gpd.drop_duplicates()
    refined_gpd.reset_index(drop=True, inplace=True)
    # refined_gpd

    # data 불러오기
    data_f = pd.read_csv("data/data.csv")
    # data_f

    data_f = data_f.drop(columns=['ACC_YEAR', 'BJDONG_CD', 'SGG_CD', 'BJDONG_NM', 'LAND_GBN_NM', 'BONBEON', 'BLDG_AREA', 'TOT_AREA', 'RIGHT_GBN', 'CNTL_YMD', 'Unnamed: 0', 'LAND_GBN', 'BUBEON', 'BLDG_NM', 'OBJ_AMT', 'REQ_GBN', 'RDEALER_LAWDNM', 'DEAL_YMD'])
    # 삭제된 컬럼을 제외한 데이터프레임 확인
    # data_f

    # 여러 개의 컬럼명 변경
    data_f.rename(columns={'SGG_NM': '자치구명', 'FLOOR': '층', 'BUILD_YEAR': '건축년도', 'HOUSE_TYPE': '건물용도'}, inplace=True)

    data_f = data_f[data_f['건축년도'] != 0]
    data_f.reset_index(drop=True, inplace=True)
    # data_f # 결측치 제거

    # 건물나이 컬럼 추가
    data_f = data_f.assign(건물나이 = 2024 - data_f['건축년도'])
    # data_f

    conditions = [
    (data_f['건축년도'] <= 1981) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 20),
    (data_f['건축년도'] <= 1981) & (data_f['층'] >= 5) & (data_f['건물나이'] >= 20),
    (data_f['건축년도'] == 1982) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 21),
    (data_f['건축년도'] == 1982) & (data_f['층'] >= 5) & (data_f['건물나이'] >= 22),
    (data_f['건축년도'] == 1983) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 22),
    (data_f['건축년도'] == 1983) & (data_f['층'] >= 5) & (data_f['건물나이'] >= 24),
    (data_f['건축년도'] == 1984) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 23),
    (data_f['건축년도'] == 1984) & (data_f['층'] >= 5) & (data_f['건물나이'] >= 26),
    (data_f['건축년도'] == 1985) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 24),
    (data_f['건축년도'] == 1985) & (data_f['층'] >= 5) & (data_f['건물나이'] >= 28),
    (data_f['건축년도'] == 1986) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 25),
    (data_f['건축년도'] >= 1986) & (data_f['층'] >= 5) & (data_f['건물나이'] >= 30),
    (data_f['건축년도'] == 1987) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 26),
    (data_f['건축년도'] == 1988) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 27),
    (data_f['건축년도'] == 1989) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 28),
    (data_f['건축년도'] == 1990) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 29),
    (data_f['건축년도'] >= 1991) & (data_f['층'] <= 4) & (data_f['건물나이'] >= 30)
    ]

    choices = [True, True, True, True, True, True, True, True, True,
               True, True, True, True, True, True, True, True]

    data_f['재건축연한초과'] = np.select(conditions, choices, default=False)

    # 결과물 확인
    # data_f

    # 이제 data_f와 refined_gpd를 합쳐서 data_f에 geometry컬럼이 들어가도록 할 것이다.
    # 기준은 '자치구명'.
    merged_gpd = refined_gpd.merge(data_f, on='자치구명', how='left')
    # merged_gpd

    # 자치구명, 건물용도 기준으로 그룹화하고, 그 결과물에서 건축년도에 대한 평균과 size 구하기.
    summary_seoul = merged_gpd.groupby(['자치구명', '건물용도',])['건축년도'].agg(['mean', 'size']).reset_index()
    # summary_seoul

    final_gpd = merged_gpd.merge(summary_seoul[['자치구명', '건물용도', 'mean', 'size']], on=['자치구명', '건물용도'], how='left')
    # final_gpd

    random_sliced_gpd = final_gpd.sample(n=5000, random_state=42).reset_index(drop=True)
    return random_sliced_gpd


# 데이터 불러와서 전역변수 만들기
random_sliced_gpd = get_sliced_gpd()


# 이하 시각화 함수들
def apt_avg(df):
    st.title("지역별 아파트 건축년도 평균")

    apartment_df = df[df['건물용도']=='아파트']

    fig = px.choropleth_mapbox(apartment_df, 
                               geojson=apartment_df.geometry, 
                               locations=apartment_df.index, 
                               color='mean',
                               color_continuous_scale="RdYlBu",
                               range_color=(apartment_df['mean'].min(), apartment_df['mean'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": apartment_df.geometry.centroid.y.mean(), "lon": apartment_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='아파트 건축년도 평균(년)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)

def multi_gene_avg(df):
    st.title("지역별 연립다세대 건축년도 평균")

    townhouse_df = df[df['건물용도']=='연립다세대']

    fig = px.choropleth_mapbox(townhouse_df, 
                               geojson=townhouse_df.geometry, 
                               locations=townhouse_df.index, 
                               color='mean',
                               color_continuous_scale="RdYlBu",
                               range_color=(townhouse_df['mean'].min(), townhouse_df['mean'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": townhouse_df.geometry.centroid.y.mean(), "lon": townhouse_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='연립다세대 건축년도 평균(년)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)

def single_avg(df):
    st.title("지역별 단독다가구 건축년도 평균")
    # '단독다가구'에 대한 데이터만 필터링
    detached_house_df = df[df['건물용도']=='단독다가구']

    fig = px.choropleth_mapbox(detached_house_df, 
                               geojson=detached_house_df.geometry, 
                               locations=detached_house_df.index, 
                               color='mean',
                               color_continuous_scale="RdYlBu",
                               range_color=(detached_house_df['mean'].min(), detached_house_df['mean'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": detached_house_df.geometry.centroid.y.mean(), "lon": detached_house_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='단독다가구 건축년도 평균(년)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)

def office_avg(df):
    st.title("지역별 오피스텔 건축년도 평균")

    # '오피스텔'에 대한 데이터만 필터링
    office_df = df[df['건물용도']=='오피스텔']

    fig = px.choropleth_mapbox(office_df, 
                               geojson=office_df.geometry, 
                               locations=office_df.index, 
                               color='mean',
                               color_continuous_scale="RdYlBu",
                               range_color=(office_df['mean'].min(), office_df['mean'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": office_df.geometry.centroid.y.mean(), "lon": office_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='오피스텔 건축년도 평균(년)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)


# 이하 재건축 수 차트
def apt_over(df):
    st.title('지역별 아파트 재건축연한 초과 수')

    apartment_df = df[(df['건물용도'] == '아파트') & (df['재건축연한초과'])] # '재건축연한초과'부분은 ==True가 따로 없으면 자동으로 True에 대한 값을 조건으로 잡아준다.

    # '자치구명' 컬럼을 hover_data에 추가
    fig = px.choropleth_mapbox(apartment_df, 
                               geojson=apartment_df.geometry, 
                               locations=apartment_df.index, 
                               color='size',
                               color_continuous_scale="RdYlBu",
                               range_color=(apartment_df['size'].min(), apartment_df['size'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": apartment_df.geometry.centroid.y.mean(), "lon": apartment_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='아파트 재건축연한초과 수(채)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)

def multi_gene_over(df):
    st.title('지역별 연립다세대 재건축연한 초과 수')
    # 연립다세대 데이터
    apartment_df = df[(df['건물용도'] == '연립다세대') & (df['재건축연한초과'])]

    # '자치구명' 컬럼을 hover_data에 추가
    fig = px.choropleth_mapbox(apartment_df, 
                               geojson=apartment_df.geometry, 
                               locations=apartment_df.index, 
                               color='size',
                               color_continuous_scale="RdYlBu",
                               range_color=(apartment_df['size'].min(), apartment_df['size'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": apartment_df.geometry.centroid.y.mean(), "lon": apartment_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='연립다세대 재건축연한초과 수(채)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)


def single_over(df):
    apartment_df = df[(df['건물용도'] == '단독다가구') & (df['재건축연한초과'])]

    # '자치구명' 컬럼을 hover_data에 추가
    fig = px.choropleth_mapbox(apartment_df, 
                               geojson=apartment_df.geometry, 
                               locations=apartment_df.index, 
                               color='size',
                               color_continuous_scale="RdYlBu",
                               range_color=(apartment_df['size'].min(), apartment_df['size'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": apartment_df.geometry.centroid.y.mean(), "lon": apartment_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='단독다가구 재건축연한초과 수(채)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)


def office_over(df):
    apartment_df = df[(df['건물용도'] == '오피스텔') & (df['재건축연한초과'])]

    # '자치구명' 컬럼을 hover_data에 추가
    fig = px.choropleth_mapbox(apartment_df, 
                               geojson=apartment_df.geometry, 
                               locations=apartment_df.index, 
                               color='size',
                               color_continuous_scale="RdYlBu",
                               range_color=(apartment_df['size'].min(), apartment_df['size'].max()),
                               mapbox_style="carto-positron",
                               center={"lat": apartment_df.geometry.centroid.y.mean(), "lon": apartment_df.geometry.centroid.x.mean()},
                               zoom=10,
                               opacity=0.7,
                               title='오피스텔 재건축연한초과 수(채)',
                               hover_data=['자치구명'])  # '자치구명' hover_data 추가

    # 레이아웃 설정
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # 플롯 보이기
    st.plotly_chart(fig, use_container_width=True)

# 여기까지 시각화 함수들

# 아래는 메인


def main():

    st.header("재건축 관련 정보")
    st.write('-'*50)

    tab1, tab2 = st.tabs(["건축년도 평균", "재건축 연한 초과"])

    with tab1:
        st.header("지역별 건축년도 평균")
        
        # 지역별 건축년도 평균 select box
        avg_selectbox = st.selectbox('지역별 건축년도 평균', ('아파트', '연립다세대', '단독다가구', '오피스텔'), index=None, placeholder="건물 유형을 선택하세요")

        if avg_selectbox == '아파트':
            # 시각화 코드 불러오기
            apt_avg(random_sliced_gpd)
        elif avg_selectbox == '연립다세대':
            multi_gene_avg(random_sliced_gpd)
        elif avg_selectbox == '단독다가구':
            single_avg(random_sliced_gpd)
        elif avg_selectbox == "오피스텔":
            office_avg(random_sliced_gpd)


    with tab2:
        st.header("지역별 재건축연한 초과 건물 수")

        # 지역별 재건축연한 초과 건물수 select box
        over_selectbox = st.selectbox('지역별 재건축연한 초과건물 수', ('아파트', '연립다세대', '단독다가구', '오피스텔'), index=None, placeholder="건물 유형을 선택하세요")

        if over_selectbox == '아파트':
            # 시각화 코드 불러오기
            apt_over(random_sliced_gpd)
        elif over_selectbox == '연립다세대':
            multi_gene_over(random_sliced_gpd)
        elif over_selectbox == '단독다가구':
            single_over(random_sliced_gpd)
        elif over_selectbox == '오피스텔':
            office_over(random_sliced_gpd)


    # 체크박스를 생성
    show_plot = st.checkbox("서울 재건축연한 기준표")

    if show_plot:
        # 체크박스가 활성화된 경우 .png 파일을 불러와서 출력합니다.
        st.image("data/rebuilding_standard.png")




if __name__ == "__main__":
    main()