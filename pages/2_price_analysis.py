import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data(filepath):
    return pd.read_csv(filepath)

def type_scatter(df, house_type):
    df_filtered = df[df['HOUSE_TYPE'] == house_type]
    fig = px.scatter(df_filtered, x='BLDG_AREA', y='OBJ_AMT', 
                     title=f'{house_type} 건물 면적별 부동산 매매 가격',
                     labels={'BLDG_AREA': '건물 면적 (㎡)', 'OBJ_AMT': '매매 가격 (만 원)'},
                     trendline='ols',
                     trendline_color_override="red")
    
    fig.update_layout(plot_bgcolor='#F5FBFC',
                      paper_bgcolor='#F5FBFC',
                      title_font_family="나눔고딕",
                      title_font_size=18,
                      hovermode="x unified",
                      template='plotly_white',
                      yaxis_tickformat=',',
                      legend=dict(orientation='h', xanchor="center", x=0.85, y=1.1),
                      barmode='group',
                      xaxis=dict(title_font=dict(family="나눔고딕", color="black")),
                      yaxis=dict(title_font=dict(family="나눔고딕", color="black")))
    
    fig.update_traces(marker=dict(size=8, color='#00CC00', line=dict(width=2, color='DarkSlateGrey')))

    fig.update_traces(hovertemplate="<b>건물 면적</b>: %{x} (㎡)<br><b>매매 가격</b>: %{y} (만 원)<extra></extra>")
    trendline_trace = fig.data[-1]
    trendline_trace.hovertemplate = '<b>건물 면적</b>: %{x} (㎡)<br><b>매매 가격</b>: %{y} (만 원)<extra></extra>'

    fig.update_xaxes(title_font_family="나눔고딕", color="black")
    fig.update_yaxes(title_font_family="나눔고딕", color="black")

    return fig
    
def type_mean(df, year, month, housing_type):
    # 데이터타입
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    df['mean'] = df['mean'].astype(int)

    # 특정 년도 및 월 선택
    filtered_df = df[(df['year'] == year) & (df['month'] == month)]
    filtered_df = filtered_df.sort_values(by='mean', ascending=False)

    # 건물 용도별 제목
    title_map = {
        '아파트': '자치구별 아파트 매매(실거래가) 평균',
        '오피스텔': '자치구별 오피스텔 매매(실거래가) 평균',
        '단독다가구': '자치구별 단독다가구 매매(실거래가) 평균',
        '연립다세대': '자치구별 연립다세대 매매(실거래가) 평균'
    }
    title = f"{title_map[housing_type]} <br>"

    # 시각화
    fig = px.bar(filtered_df, x='SIG_KOR_NM', y='mean',
                 title=title,
                 labels={'mean': '매매 가격 (만 원)', 'SIG_KOR_NM': '자치구명'},
                 color='mean',
                 color_continuous_scale='greens')
    
    # 레이아웃 업데이트
    fig.update_layout(plot_bgcolor='#F5FBFC',
                      paper_bgcolor='#F5FBFC',
                      title_font_family="나눔고딕",
                      title_font_size=18,
                      hovermode="x unified",
                      template='plotly_white',
                      xaxis_tickangle=90,
                      yaxis_tickformat=',',
                      legend=dict(title_font_family="나눔고딕", font=dict(size= 15), 
                                  orientation='h', xanchor="center", x=0.85, y=1.1),
                      xaxis=dict(title_font=dict(family="나눔고딕", color="black")),
                      yaxis=dict(title_font=dict(family="나눔고딕", color="black")),
                   
    )

    
    # y값 숫자 형식 변경
    fig.update_coloraxes(colorbar_tickprefix='', colorbar_tickformat=',')
    # marker 형식 변경
    fig.update_traces(marker_line=dict(width=2, color='DarkSlateGrey'))
    # x, y축 폰트 및 색상 변경
    fig.update_xaxes(title_font_family="나눔고딕", color="black", tickangle=-45)
    fig.update_yaxes(title_font_family="나눔고딕", color="black")
    # hover 내용 변경
    fig.update_traces(hovertemplate="<b>자치구명</b>: %{x}<br><b>매매 가격</b>: %{y} (만 원)<extra></extra>")

    return fig

def house_price_trend(df, sgg_nms, house_type):
    # 데이터 필터링
    df_filtered = df[(df['SGG_NM'].isin(sgg_nms)) & (df['HOUSE_TYPE'] == house_type)]

    # 'DEAL_YMD'를 datetime으로 변환하고 'Year Month' 열을 준비
    df_filtered['DEAL_YMD'] = pd.to_datetime(df_filtered['DEAL_YMD'], format='%Y%m%d')
    df_filtered['YearMonth'] = df_filtered['DEAL_YMD'].dt.to_period('M').dt.to_timestamp()

    # 데이터 'YearMonth'별로 정렬
    df_filtered = df_filtered.sort_values(by='YearMonth')

    # 'YearMonth'와 'SGG_NM'으로 데이터 그룹화 및 평균 'OBJ_AMT'를 계산
    df_grouped = df_filtered.groupby(['YearMonth', 'SGG_NM'])['OBJ_AMT'].mean().reset_index()

    # 시각화
    fig = px.line(df_grouped, 
                  x='YearMonth', 
                  y='OBJ_AMT', 
                  color='SGG_NM', 
                  labels={'YearMonth': '계약일', 'OBJ_AMT': '평균 거래 가격 (만 원)'}, 
                  title=f'{house_type} 가격 변동 추이 비교',
                  hover_name='SGG_NM')

    # 레이아웃 추가
    fig.update_layout(plot_bgcolor='#F5FBFC',
                      paper_bgcolor='#F5FBFC',
                      xaxis_title='계약일', 
                      yaxis_title='평균 거래 가격 (만 원)',
                      yaxis_tickformat=',', 
                      hovermode="x unified",
                      legend_title='자치구명',
                      legend=dict(title_font_family="나눔고딕",
                              font=dict(size= 15)),
                      xaxis=dict(title_font=dict(family="나눔고딕", color="black")),
                      yaxis=dict(title_font=dict(family="나눔고딕", color="black")))
    
    #날짜 형식 변경
    fig.update_xaxes(tickformat="%Y년 %m월")
    # hover 내용 변경
    fig.update_traces(hovertemplate="<b>자치구명</b>: %{hovertext}<br>" +
                                "<b>계약일</b>: %{x}<br>" +
                                "<b>평균 거래 가격</b>: %{y:,.0f} (만 원)<extra></extra>")
                                                    
    return fig

def main():
    st.title('부동산 유형별 데이터 분석')

    # 분석 유형 선택
    analysis_type = st.sidebar.selectbox("분석 유형을 선택하세요.",
                                         ["건물 면적과 매매 가격 분석", "자치구별 매매 가격 평균", "자치구별 가격 변동 추이"])

    if analysis_type == "건물 면적과 매매 가격 분석":
        house_type = st.sidebar.selectbox('부동산 유형을 선택하세요.',
                                          ['아파트', '오피스텔', '단독다가구', '연립다세대'])
        #데이터 불러오기 
        df = load_data('./data/data.csv')  
        fig = type_scatter(df, house_type)
        st.plotly_chart(fig)
    elif analysis_type == '자치구별 매매 가격 평균':
        year = st.sidebar.selectbox('년도를 입력하세요.', ['2024', '2023'])

        #선택된 년도에 따른 조건문
        if year == '2024':
            month_options = ['1']
            
        elif year == '2023':
            month_options = ['5', '6', '7', '8', '9', '10', '11', '12']

        #month_options = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
            
        month = st.sidebar.selectbox('월을 입력하세요.', month_options)
        month = int(month)
    
        
        housing_type = st.sidebar.selectbox('부동산 유형을 선택하세요.',
                                            ['아파트', '오피스텔', '단독다가구', '연립다세대'])
        
        file_paths = {
            '아파트': './data/merge_df1.csv',
            '오피스텔': './data/merge_df2.csv',
            '단독다가구': './data/merge_df3.csv',
            '연립다세대': './data/merge_df4.csv',
        }
        df = load_data(file_paths[housing_type])
        fig = type_mean(df, int(year), month, housing_type)
        st.plotly_chart(fig)
    
    elif analysis_type == "자치구별 가격 변동 추이":
        df = load_data('./data/data.csv') 
        df['DEAL_YMD'] = pd.to_datetime(df['DEAL_YMD'], format='%Y%m%d')  
        
       # 다중 자치구 선택 
        selected_sgg_nms = st.sidebar.multiselect('자치구명을 선택하세요.', df['SGG_NM'].unique(), default=df['SGG_NM'].unique()[0:2])
    
        # 부동산 유형 선택 
        selected_house_type = st.sidebar.selectbox('부동산 유형을 선택하세요.', df['HOUSE_TYPE'].unique())
    
        # 시각화 
        if selected_sgg_nms and selected_house_type:
            fig = house_price_trend(df, selected_sgg_nms, selected_house_type)
            st.plotly_chart(fig)
        else:
            st.warning('자치구명과 주택 유형을 선택해주세요.')

if __name__ == '__main__':
    main()
