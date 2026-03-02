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
            link = item['href']
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
            link = item.find('link').text
            news.append({"순위": i+1, "제목": title, "링크": link})
        return news
    except:
        return [{"오류": "구글 뉴스를 불러오지 못했습니다."}]

def get_nate_sisa_news():
    """기존: 네이트 시사 랭킹"""
    url = "https://news.nate.com/rank/interest?sc=sisa"
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'euc-kr'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.mduSubjectList .tit')[:10]
        news = []
        for i, item in enumerate(items):
            title = item.text.strip()
            parent_a = item.find_parent('a')
            link = parent_a['href'] if parent_a else "#"
            if link.startswith('//'):
                link = 'https:' + link
            elif link.startswith('/'):
                link = 'https://news.nate.com' + link
            news.append({"순위": i+1, "제목": title, "링크": link})
        return news
    except:
        return [{"오류": "네이트 시사 데이터를 불러오지 못했습니다."}]

def get_nate_overall_news():
    """신규 추가: 네이트 전체 랭킹 종합 1위~10위"""
    url = "https://news.nate.com/rank/?mid=n1000"
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'euc-kr'
        soup = BeautifulSoup(response.text, 'html.parser')
        # 전체 랭킹은 1~5위 구간과 6위 이하 구간의 태그 이름이 살짝 달라서 두 개를 모두 잡아냅니다.
        items = soup.select('.mduSubjectList .tit, .postRankSubjectList .tit')[:10]
        news = []
        for i, item in enumerate(items):
            title = item.text.strip()
            parent_a = item.find_parent('a')
            link = parent_a['href'] if parent_a else "#"
            if link.startswith('//'):
                link = 'https:' + link
            elif link.startswith('/'):
                link = 'https://news.nate.com' + link
            news.append({"순위": i+1, "제목": title, "링크": link})
        return news
    except:
        return [{"오류": "네이트 전체 랭킹 데이터를 불러오지 못했습니다."}]

# --- 깔끔한 클릭형 리스트 출력 함수 ---
def display_links(data_list):
    if not data_list:
        return
    if "오류" in data_list[0]:
        st.error(data_list[0]["오류"])
        return
    for item in data_list:
        st.markdown(f"**{item['순위']}.** [{item['제목']}]({item['링크']})")

# --- 화면 배치 (2칸씩 3줄) ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔵 구글 인기 검색어")
    display_links(get_google_trends())
with col2:
    st.subheader("🟢 네이버 많이 본 뉴스")
    display_links(get_naver_news())

st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("🌐 구글 실시간 핫뉴스")
    display_links(get_google_korea_news())
with col4:
    st.subheader("🔴 네이트 시사 랭킹")
    display_links(get_nate_sisa_news())

st.markdown("---")
col5, col6 = st.columns(2)

with col5:
    st.subheader("🟣 네이트 전체 종합 랭킹")
    display_links(get_nate_overall_news())
# col6은 현재 비워둡니다. 나중에 또 추가하고 싶은 사이트가 생기면 이 자리에 넣으면 됩니다!
