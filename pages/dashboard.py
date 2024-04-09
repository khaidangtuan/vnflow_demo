from config import data_path
import pandas as pd
import streamlit as st
import plotly.express as px
import time
import requests
import xml.etree.ElementTree as ET  
import numpy as np

def exr_fetch(api_url):
    # fetch xml data via api
    info = requests.get(api_url)
    
    # parse xmml
    root = ET.fromstring(info.content)
    
    # extract info
    date = ''
    exr_df = {'CurrencyCode':[],
              'CurrencyName':[],
              'Buy':[],
              'Transfer':[],
              'Sell':[],
             }
              
    for child in root:
        if child.tag == 'DateTime':
            date = child.text
        elif child.tag == 'Exrate':
            for k, v in child.attrib.items():
                
                exr_df[k].append(v)
                
    return date, exr_df

def prepare_data(df, group, model):
    df[['Date','Time']] = df['created_at'].str.split(' ', n=1, expand=True)
    if group == 'All':
        data = df[df.model == model].sort_values(by=['created_at'], ascending=False)
    else:
        data = df[(df.model == model) & (df.groupName == group)].sort_values(by=['created_at'], ascending=False)
    
    return data

def statics(df, no_of_day):
    message_count = df.groupby(['Date'])['model'].count().reset_index().tail(no_of_day)
    message_count.rename(columns={'model':'count'}, inplace=True)
    message_yesterday, message_today = message_count.tail(2)['count'].values
    day_price = df.groupby(['Date'])['price'].mean().reset_index().tail(no_of_day)
    price_yesterday, price_today = day_price.tail(2)['price'].values
    
    day_group_price = df.groupby(['Date','groupName'])['price'].mean().reset_index().tail(no_of_day)
    day_price['groupName'] = 'All'
    day_price = pd.concat([day_price, day_group_price], ignore_index=True)
    
    return message_count, message_yesterday, message_today, day_price, price_yesterday, price_today
        
# load data
items = pd.read_csv(data_path)
groups = items.groupName.unique().tolist()
models = items.model.unique().tolist()

# page configuration
st.set_page_config(
    page_title='Analytics',
    page_icon='',
    layout='wide',
)

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if 'password_correct' not in st.session_state:
    st.error(':confused: Please log in first')
    
    login_butt = st.button('Đăng nhập')
    
    if login_butt:
        st.switch_page('main.py')
        
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    group_selection = st.selectbox("Select the group", ['All'] + groups)    
with col2:
    model_selection = st.selectbox("Select the model", models)
with col3:
    noday_observed = st.number_input('Số ngày quan sát', min_value=3, max_value=30, value=5)
statics_placeholder = st.empty()
chart_placeholder = st.empty()
rcm_placeholder = st.empty()


model_state = ''

while True:
    if model_selection == model_state:
        continue
    else:
        data = prepare_data(items, group_selection, model_selection)
        
    if data.empty:
        with statics_placeholder.container():
            st.error('No data')
        continue
    
    # simple statics
    message_count, yesterday_count, today_count, daily_price, price_yesterday, price_today = statics(data, no_of_day=noday_observed)
    
    with statics_placeholder.container():
        daily_message_count, daily_avg_price = st.columns(2)
        with daily_message_count.container(border=True):
            st.metric(
                label='Số tin rao bán trong ngày',
                value='{:,}'.format(int(today_count)),
                delta='{:,}'.format(int(today_count - yesterday_count)),
            )
        
        with daily_avg_price.container(border=True):
            st.metric(
                label='Giá trung bình ngày',
                value='{:,}'.format(int(price_today)),
                delta='{:,}'.format(int(price_today - price_yesterday)),
            )
            
    with chart_placeholder.container():
        chart, exr_table = st.columns(2)
        with chart.container(border=True):
            fig = px.bar(
                data_frame=message_count,
                x='Date',
                y='count',
                text='count',
                title='Số lượng tin rao bán theo ngày'
            )
            st.plotly_chart(fig, use_container_width=True)

            if group_selection == 'All':
                fig = px.line(
                    data_frame=daily_price,
                    x='Date',
                    y='price',
                    color='groupName',
                    markers=True,
                    title='Giá rao bán theo ngày'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:    
                fig = px.line(
                    data_frame=daily_price[daily_price['groupName'] == 'All'],
                    x='Date',
                    y='price',
                    markers=True,
                    title='Giá rao bán theo ngày'
                )
                st.plotly_chart(fig, use_container_width=True)
        with exr_table.container(border=True):
            st.markdown('##### Bảng tỉ giá')
            url = 'https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx'
            date, exr_tab = exr_fetch(url)
            st.write('Thời gian {}'.format(date))
            st.table(pd.DataFrame(exr_tab))
        
    with rcm_placeholder.container(border=True):
        st.markdown('##### Dự báo giá')
    time.sleep(5)
        
        
    
    



    




