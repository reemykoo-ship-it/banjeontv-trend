import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET

st.set_page_config(layout="wide", page_title="banjeontv 트렌드 대시보드")
st.title("🔥 실시간 통합 트렌드 & 랭킹 대시보드")
st.markdown("구글 검색, 구글 뉴스, 네이버, 네이트의 현재 가장 뜨거운 이슈를 한눈에 확인하세요.")

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def get_google_trends():
    """구글 인기 검색어 (안정적)"""
    url = "https://trends.google.co.kr/trending/rss?geo=KR"
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        trends = [{"순위": i+1, "키워드 (구글 검색)": item.find('title').text} for i, item in enumerate(root.findall('./channel/item')[:10])]
        return pd.DataFrame(trends)
    except:
        return pd.DataFrame({"오류": ["구글 검색 트렌드를 불러오지 못했습니다."]})

def get_naver_news():
    """네이버 많이 본 뉴스"""
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.rankingnews_list > li > .list_content > a')[:10]
        return pd.DataFrame([{"순위": i+1, "인기 뉴스 (네이버)": item.text.strip()} for i, item in enumerate(items)])
    except:
        return pd.DataFrame({"오류": ["네이버 데이터를 불러오지 못했습니다."]})

def get_google_korea_news():
    """구글 한국 실시간 뉴스 (기존 다음 뉴스를 대체하는 100% 안정적인 소스)"""
    url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        news_list = [{"순위": i+1, "인기 뉴스 (구글 뉴스)": item.find('title').text} for i, item in enumerate(root.findall('./channel/item')[:10])]
        return pd.DataFrame(news_list)
    except:
        return pd.DataFrame({"오류": ["구글 뉴스를 불러오지 못했습니다."]})

def get_nate_news():
    """네이트 랭킹 뉴스 (한글 깨짐 해결 완료)"""
    url = "https://news.nate.com/rank/interest?sc=sisa"
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'euc-kr'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.mduSubjectList .tit')[:10]
        return pd.DataFrame([{"순위": i+1, "인기 뉴스 (네이트)": item.text.strip()} for i, item in enumerate(items)])
    except:
        return pd.DataFrame({"오류": ["네이트 데이터를 불러오지 못했습니다."]})

# --- 화면 4분할 배치 ---
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
    # 다음 뉴스 대신 구글 뉴스로 교체!
    st.subheader("🌐 구글 실시간 핫뉴스")
    st.dataframe(get_google_korea_news(), hide_index=True, use_container_width=True)
with col4:
    st.subheader("🔴 네이트 랭킹 뉴스")
    st.dataframe(get_nate_news(), hide_index=True, use_container_width=True)
