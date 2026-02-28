import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET

st.set_page_config(layout="wide", page_title="banjeontv 트렌드 대시보드")
st.title("🔥 실시간 통합 트렌드 & 랭킹 대시보드")
st.markdown("구글, 네이버, 다음, 네이트의 현재 가장 뜨거운 이슈를 한눈에 확인하세요.")

# 최신 맥(Mac) 환경으로 완벽하게 위장하여 포털의 차단을 방지합니다.
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def get_google_trends():
    url = "https://trends.google.co.kr/trending/rss?geo=KR"
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        trends = [{"순위": i+1, "키워드 (구글)": item.find('title').text} for i, item in enumerate(root.findall('./channel/item')[:10])]
        return pd.DataFrame(trends)
    except:
        return pd.DataFrame({"오류": ["구글 데이터를 불러오지 못했습니다."]})

def get_naver_news():
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.rankingnews_list > li > .list_content > a')[:10]
        return pd.DataFrame([{"순위": i+1, "인기 뉴스 (네이버)": item.text.strip()} for i, item in enumerate(items)])
    except:
        return pd.DataFrame({"오류": ["네이버 데이터를 불러오지 못했습니다."]})

def get_daum_news():
    url = "https://news.daum.net/ranking/popular"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 다음 뉴스는 페이지 내부 구조가 자주 변하므로, 여러 가지 그물을 던져서 잡아냅니다.
        selectors = [
            '.list_news2 .tit_thumb a',
            '.list_news2 a.link_txt',
            'ul.list_news a.link_txt',
            '.item_issue a.link_txt',
            '.item_news a',
            'a.link_txt' # 최후의 수단: 페이지 내의 모든 주요 링크
        ]
        
        items = []
        for selector in selectors:
            found = soup.select(selector)
            if len(found) >= 5: # 5개 이상 찾아지면 맞는 경로로 판단
                items = found
                break
                
        news_list = []
        for item in items:
            title = item.text.strip()
            # 너무 짧은 단어(메뉴 버튼 등) 제외, 중복 기사 제외
            if title and len(title) > 5 and title not in [n["인기 뉴스 (다음)"] for n in news_list]:
                news_list.append({"순위": len(news_list)+1, "인기 뉴스 (다음)": title})
            if len(news_list) == 10:
                break
                
        if not news_list:
            return pd.DataFrame({"오류": ["페이지 구조가 변경되어 제목을 찾을 수 없습니다."]})
            
        return pd.DataFrame(news_list)
    except:
        return pd.DataFrame({"오류": ["다음 데이터를 불러오지 못했습니다."]})

def get_nate_news():
    url = "https://news.nate.com/rank/interest?sc=sisa"
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'euc-kr'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.mduSubjectList .tit')[:10]
        return pd.DataFrame([{"순위": i+1, "인기 뉴스 (네이트)": item.text.strip()} for i, item in enumerate(items)])
    except:
        return pd.DataFrame({"오류": ["네이트 데이터를 불러오지 못했습니다."]})

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
