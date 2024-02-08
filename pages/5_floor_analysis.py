import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import folium_static

file_path = "data/sampled_data2.geojson"
gdf = gpd.read_file(file_path)

st.title('서울시 건물 평균 층수 대시보드')
st.write('이 대시보드는 서울시의 건물 데이터를 사용하여 만들어졌습니다.')

average_floors = gdf['층'].mean()

st.write(f'서울시 건물의 평균 층수: {average_floors:.2f} 층')

st.sidebar.title('메뉴')
selected_option = st.sidebar.radio('이동할 페이지를 선택하세요.', ['시각화 지도'])

if selected_option == '시각화 지도':
    sub_option = st.sidebar.radio('페이지를 선택하세요.', ['시각화 지도', '막대 그래프', '히트맵', '건물 용도별 층수', '건물 용도 및 건축 연도별 분석'])

    if sub_option == '시각화 지도':
        st.subheader('서울시의 건물 분포:')
        m = folium.Map(location=[37.5665, 126.978], zoom_start=12)
        for idx, row in gdf.iterrows():
            center = row.geometry.centroid
            lat, lon = center.y, center.x
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue',
                popup=f"층수: {row['층']}"
            ).add_to(m)
        
        for idx, row in gdf.iterrows():
            center = row.geometry.centroid
            lat, lon = center.y, center.x
            folium.CircleMarker(
                location=[lat, lon],
                radius=row['층'] * 0.5,  
                color='red',
                fill=True,
                fill_color='red',
                popup=f"층수: {row['층']}"
            ).add_to(m)
        folium_static(m)  

    elif sub_option == '막대 그래프':
        st.subheader('자치구별 층수 시각화')
        fig = px.bar(
            gdf.groupby('자치구명')['층'].mean().reset_index(),  
            x='자치구명',
            y='층',
            title='자치구별 평균 층수',
            labels={'층': '평균 층수', '자치구명': '자치구'},
            height=400
        )
        st.plotly_chart(fig)

    elif sub_option == '히트맵':
       
        st.subheader('서울시 건물 층 수 분포 히트맵')
        gdf['centroid_lat'] = gdf.geometry.centroid.y
        gdf['centroid_lon'] = gdf.geometry.centroid.x
        fig = px.density_mapbox(
            gdf, 
            lat='centroid_lat', 
            lon='centroid_lon', 
            z='층', 
            radius=30,  
            center=dict(lat=37.5665, lon=126.978),
            zoom=10,
            mapbox_style="carto-positron",
            title="서울시 건물 층 수 분포",
        )
        st.plotly_chart(fig)

    elif sub_option == '건물 용도별 층수':
        st.subheader('건물 용도별 층수 분석')
        building_types = gdf['건물용도'].unique()
        selected_building_types = st.multiselect('건물 용도 선택', building_types, default=building_types)
        
        if selected_building_types:
            filtered_gdf = gdf[gdf['건물용도'].isin(selected_building_types)]
            fig = px.box(filtered_gdf, x='건물용도', y='층', points="all")
            fig.update_layout(
                title="건물 용도별 층수 분포",
                xaxis_title="건물 용도",
                yaxis_title="층수",
                height=500
            )
            st.plotly_chart(fig)
    
    elif sub_option == '건물 용도 및 건축 연도별 분석':
        st.subheader('건물 용도 및 건축 연도별 분석')
        building_types = gdf['건물용도'].unique()
        selected_building_types = st.multiselect('건물 용도 선택', building_types, default=building_types)
        
        construction_years = sorted(gdf['건축년도'].unique())  
        selected_construction_years = st.selectbox('건축 연도 선택', options=construction_years, format_func=lambda x: f"{int(x)}년")
        
        if selected_building_types and selected_construction_years:
            filtered_gdf = gdf[gdf['건물용도'].isin(selected_building_types) & gdf['건축년도'].isin([selected_construction_years])]
            fig = px.box(filtered_gdf, x='건물용도', y='층', color='건축년도', points="all")
            fig.update_layout(
                title="건물 용도 및 건축 연도별 층수 분포",
                xaxis_title="건물 용도",
                yaxis_title="층수",
                height=500
            )
            st.plotly_chart(fig)