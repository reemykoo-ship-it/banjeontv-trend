import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET

st.set_page_config(layout="wide", page_title="banjeontv 트렌드 대시보드")
st.title("🔥 실시간 통합 트렌드 & 랭킹 대시보드")
st.markdown("구글 검색, 구글 뉴스, 네이버, 네이트의 현재 가장 뜨거운 이슈를 한눈에 확인하세요. **(제목을 클릭하면 기사로 이동합니다)**")

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def get_google_trends():
    url = "https://trends.google.co.kr/trending/rss?geo=KR"
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        trends = []
        for i, item in enumerate(root.findall('./channel/item')[:10]):
            title = item.find('title').text
            # 구글 검색어로 연결되는 링크 생성
            link = f"https://www.google.com/search?q={title}"
            trends.append({"순위": i+1, "제목": title, "링크": link})
        return trends
    except:
        return [{"오류": "구글 검색 트렌드를 불러오지 못했습니다."}]

def get_naver_news():
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.rankingnews_list > li > .list_content > a')[:10]
        news = []
        for i, item in enumerate(items):
            title = item.text.strip()
            link = item['href'] # 네이버 기사 링크 추출
            news.append({"순위": i+1, "제목": title, "링크": link})
        return news
    except:
        return [{"오류": "네이버 데이터를 불러오지 못했습니다."}]

def get_google_korea_news():
    url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        news = []
        for i, item in enumerate(root.findall('./channel/item')[:10]):
            title = item.find('title').text
            link = item.find('link').text # 구글 뉴스 링크 추출
            news.append({"순위": i+1, "제목": title, "링크": link})
        return news
    except:
        return [{"오류": "구글 뉴스를 불러오지 못했습니다."}]

def get_nate_news():
    url = "https://news.nate.com/rank/interest?sc=sisa"
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'euc-kr'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.mduSubjectList .tit')[:10]
        news = []
        for i, item in enumerate(items):
            title = item.text.strip()
            # 네이트 기사 링크 추출 및 주소 형태 보정
            parent_a = item.find_parent('a')
            link = parent_a['href'] if parent_a else "#"
            if link.startswith('//'):
                link = 'https:' + link
            elif link.startswith('/'):
                link = 'https://news.nate.com' + link
            news.append({"순위": i+1, "제목": title, "링크": link})
        return news
    except:
        return [{"오류": "네이트 데이터를 불러오지 못했습니다."}]

# --- 깔끔한 클릭형 리스트 출력 함수 ---
def display_links(data_list):
    if not data_list:
        return
    if "오류" in data_list[0]:
        st.error(data_list[0]["오류"])
        return
    
    # 리스트 형태로 순위와 링크를 예쁘게 출력
    for item in data_list:
        st.markdown(f"**{item['순위']}.** [{item['제목']}]({item['링크']})")

# --- 화면 4분할 배치 ---
st.markdown("---")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.subheader("🔵 구글 인기 검색어")
    display_links(get_google_trends())
with col2:
    st.subheader("🟢 네이버 많이 본 뉴스")
    display_links(get_naver_news())
with col3:
    st.subheader("🌐 구글 실시간 핫뉴스")
    display_links(get_google_korea_news())
with col4:
    st.subheader("🔴 네이트 랭킹 뉴스")
    display_links(get_nate_news())
