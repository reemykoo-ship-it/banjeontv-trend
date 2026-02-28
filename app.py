import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET

st.set_page_config(layout="wide", page_title="banjeontv 트렌드 대시보드")
st.title("🔥 실시간 통합 트렌드 & 랭킹 대시보드")
st.markdown("구글, 네이버, 다음, 네이트의 현재 가장 뜨거운 이슈를 한눈에 확인하세요.")

headers = {'User-Agent': 'Mozilla/5.0'}

def get_google_trends():
    url = "https://trends.google.co.kr/trending/rss?geo=KR"
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        trends = [{"순위": i+1, "키워드 (구글)": item.find('title').text} for i, item in enumerate(root.findall('./channel/item')[:10])]
        return pd.DataFrame(trends)
    except:
        return pd.DataFrame({"오류": ["데이터를 불러오지 못했습니다."]})

def get_naver_news():
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.rankingnews_list > li > .list_content > a')[:10]
        return pd.DataFrame([{"순위": i+1, "인기 뉴스 (네이버)": item.text.strip()} for i, item in enumerate(items)])
    except:
        return pd.DataFrame({"오류": ["데이터를 불러오지 못했습니다."]})

def get_daum_news():
    url = "https://news.daum.net/ranking/popular"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.list_news2 > li > .cont_thumb > .tit_thumb > a')[:10]
        return pd.DataFrame([{"순위": i+1, "인기 뉴스 (다음)": item.text.strip()} for i, item in enumerate(items)])
    except:
        return pd.DataFrame({"오류": ["데이터를 불러오지 못했습니다."]})

def get_nate_news():
    url = "https://news.nate.com/rank/interest?sc=sisa"
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.mduSubjectList .tit')[:10]
        return pd.DataFrame([{"순위": i+1, "인기 뉴스 (네이트)": item.text.strip()} for i, item in enumerate(items)])
    except:
        return pd.DataFrame({"오류": ["데이터를 불러오지 못했습니다."]})

st.markdown("---")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.subheader("🔵 구글 인기 검색어")
    st.dataframe(get_google_trends(), hide_index=True, use_container_width=True)
with col2:
    st.subheader("🟢 네이버 많이 본 뉴스")
    st.dataframe(get_naver_news(), hide_index=True, use_container_width=True)
with col3:
    st.subheader("🟡 다음 많이 본 뉴스")
    st.dataframe(get_daum_news(), hide_index=True, use_container_width=True)
with col4:
    st.subheader("🔴 네이트 랭킹 뉴스")
    st.dataframe(get_nate_news(), hide_index=True, use_container_width=True)