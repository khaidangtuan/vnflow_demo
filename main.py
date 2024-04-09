import yaml
from yaml.loader import SafeLoader
from PIL import Image
import streamlit_authenticator as stauth
import streamlit as st

st.set_page_config(
    page_title='Analytics',
    page_icon='',
    layout='centered',
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

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

with st.container(border=True):
    phoenix_logo, vnflow_logo = st.columns([0.55,0.2], gap='large')
    with phoenix_logo:
        phoenix_img = Image.open('image/phoenix_logo.png')
        width, height = phoenix_img.size
        phoenix_img_resized = phoenix_img.resize((round(width/3), round(height/3)))
        st.image(phoenix_img_resized, width=2, use_column_width='auto')
    with vnflow_logo:
        st.image('image/vnflow_logo.jpg', width=80, use_column_width='always')
        

name, authentication_status, username = authenticator.login( 'main','Login')


if authentication_status:
    authenticator.logout('Logout', 'main')
    st.session_state['password_correct'] = True
    st.write(f'Welcome *{name}*')
    st.switch_page('pages/dashboard.py')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')