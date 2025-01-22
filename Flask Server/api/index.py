from urllib.parse import urlparse
from flask import Flask, request, jsonify
from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup
from datetime import datetime
from fuzzywuzzy import fuzz
import tldextract
import socket
import ssl
import pandas as pd
import re


def extract_domain(url):
    try:
        parsed_url = urlparse(url) 
        domain = parsed_url.hostname or url 
        if domain[:4] == ('www.') : domain = domain[4:]
        return domain
    except Exception as e:
        return '에러 발생',e

def check_sld_kr(domain) : 
    domain = domain.split(".")
    if domain[-1] == "kr" :
        if domain[-2] in sld :
            return 1
    return 0

def check_tld(domain) :
    domain = domain.split('.')
    strange_tlds = ['shop', 'top', 'xyz']
    # 출처 
    for i in strange_tlds :
        if domain[-1] == i :
            return [1, i]
    return [0,'-']

def check_ssl_validity(url):
    domain = urlparse(url).hostname

    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)

        conn.connect((domain, 443))
        ssl_info = conn.getpeercert()
        return 1 # 유효
    except Exception as e:

        return 0 # 유효 안 함, 근데 이거 코드가 뭔가 이상한게 정상적인 인증서 가지고 있어도 0이 리턴 되는 경우가 가끔 있음
                            # 원인은 가끔 사이트마다 크롤링 방지한다고 뭘 막아놔서 그런 것 같은데 나중에 더 찾아봐야 될 듯
def count_subdomains(url):
    return (url.count('.')-1)
import ssl
import socket
from urllib.parse import urlparse

def get_ssl_certificate_type(url):
    try:
        # URL 파싱 및 호스트네임 추출
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or url
        # SSL 소켓 연결 생성
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        # 인증서에서 subject 정보 추출
        subject = dict(x[0] for x in cert['subject'])
        organization_name = subject.get('organizationName')
        # serialNumber 추출
        serial_number = subject.get('serialNumber')  # serialNumber 가져오기

        # EV 인증서: 조직 정보와 serialNumber가 모두 있을 때
        if organization_name and serial_number:
            return [2, f"EV 인증서 (조직: {organization_name}, Serial Number: {serial_number})"]
        # OV 인증서: 조직 정보만 있을 때
        elif organization_name:
            return [1, f"OV 인증서 (조직: {organization_name})"]
        # DV 인증서: 조직 정보와 serialNumber가 모두 없을 때
        else:
            return [0, "DV 인증서 (조직 정보 없음)"]
    
    except Exception as e:
        return f"오류 발생: {e}"
    

def remove_tld(url):
    ext = tldextract.extract(url)
    return f"{ext.subdomain}.{ext.domain}" if ext.subdomain else ext.domain

def extract_keywords(domain):
    words = re.findall(r'\w+', domain)
    return set(words)

def check_common_keywords(domain1, domain2, threshold=80):
    keywords1 = extract_keywords(domain1)
    keywords2 = extract_keywords(domain2)
    
    common_keywords = keywords1.intersection(keywords2)
    
    if common_keywords:
        return True, common_keywords
    else:
        return False, None

def common_check(official_urls, user_url, root_domain) :
    flag = 0
    a = ''
    b = ''
    for i in official_urls :
        smty = fuzz.ratio(i, user_url) # 편집거리
        rtdm = fuzz.ratio(i, root_domain)
        if smty == 100 or rtdm == 100: 
            flag = 1
            a = i
        elif smty < 100 and smty >= 80 : 
            if flag != 1 and flag != 3: 
                a = i
                flag = 2
        result, common_keywords = check_common_keywords(remove_tld(i), remove_tld(user_url)) #공통점
        if result : 
            if flag != 1 :
                a = i
                flag = 3

    if flag == 1 :
        return ([1,f'현재 접속중인 {a}은/는 공식 사이트 목록에 포함되어 있어요.'])
    elif flag == 2 :
        return ([2,f'현재 접속중인 {user_url}은/는 공식 사이트 목록에 있는 {a}와 유사도가 80% 이상이에요.'])
    elif flag == 3 :
        return ([3,f"현재 접속중인 {user_url}은/는 공식 사이트 목록에 있는 {a}와 사이트가 유사해요."])
    else : return([0,f"현재 접속중인 {user_url}은/는 공식 사이트 목록에 포함되어 있지 않아요."])

def remove_subdomain(url):
    extracted = tldextract.extract(url)
    root_domain = f"{extracted.domain}.{extracted.suffix}"
    return root_domain

def answer_url(string) :
    now_con_url = string
    url = extract_domain(now_con_url) # www 처리과정이 이상함 나중에 수정해야 될 듯
    url_del_sd = remove_subdomain(url)

    A = common_check(official_urls, url, url_del_sd) # 유사 사이트 체크
    B = check_sld_kr(url) # SLD가 국가주관 사이트인지 체크
    C = check_ssl_validity(now_con_url) # SSL 인증서가 유효한지 체크
    D = count_subdomains(url) # 서브 도메인의 개수가 몇개인지 체크
    E = get_ssl_certificate_type(now_con_url) # SSL 인증서의 종류가 무엇인지 체크
    F = check_tld(url)
    print(F)
    score = 60 # 점수는 0 ~ 1 사이
    arr = []
    # 점수 차감
    if A[0] == 2 or A[0] == 3 :
        score -= 25
        arr.append(A[1])
    if C != 1 : 
        score -= 25
        arr.append("현재 접속중인 사이트는 SSL/TLS 인증서가\n유효하지 않아요.")
    if D >= 2 :
        score -= 10
        arr.append("현재 접속중인 사이트는 서브 도메인의 개수가\n많아요.")
    if F[0] == 1 :
        score -= 10
        arr.append(f'현재 접속 중인 사이트는 피싱 사이트에서 자주 사용되는 .{F[1]} 도메인을 사용하고 있어요.')

    if E[0] == 1 :
        score += 20
        arr.append("현재 접속중인 사이트는 SSL 인증서의 종류가 OV 인증서예요.")

    if A[0] == 1 :
        score = 100
        arr.append(A[1])
    if B == 1 :
        score = 100
        arr.append("현재 접속중인 사이트는 정부 및 공공기관에서\n운영하는 사이트예요.")
    if E[0] == 2 : 
        score = 100
        arr.append("현재 접속중인 사이트는 SSL 인증서의 종류가 EV 인증서예요.")

    if now_con_url[:9] == 'chrome://':
        score = 100
        arr = ['안녕하세요! 새로운 탐색을 시작해 볼까요? 🌐']
    
    if A[0] == 0 and score != 100:
        arr.append(A[1])
    return [score,arr]

df = pd.read_excel('Flask Server/api/kr_sld.xlsx')
sld = df.values.flatten().tolist()

df = pd.read_excel('Flask Server/api/url.xlsx')
official_urls = df.values.flatten().tolist()

'''
while 1 : 
    fun = answer_url(input())

    final_score = fun[0]
    res_good = fun[1]
    res_bad = fun[2]

    if final_score >= 0.7 : 
        print('피싱 사이트로 의심되지 않습니다. 점수 :', final_score)
    elif final_score == 0.6 :
        print('피싱 사이트로 의심되지 않지만 주의 바랍니다. 점수 :', final_score)
    else : 
        print('피싱 사이트로 의심됩니다. 점수 :', final_score)    
    print()
'''

app = Flask(__name__)
@app.route('/api/') 
def api() :
    return "API endpoint"

@app.route('/api/check_url', methods=['GET'])
def check_url():
    url = request.args.get('url')  # URL을 쿼리 파라미터로 받기
    if not url:
        return "URL을 입력해 주세요.", 400 

    result = answer_url(url)
    score = result[0]
    arr = '\n\n'.join(result[1])
    user_url = remove_subdomain(url)
    if not result or score is None:
        return jsonify({'error' : '점수 계산 못 함'}), 400
    response =  jsonify({
        "score" : score,
        "good" : arr,
        "user_url" : user_url
    })
    response.charset = 'utf-8'
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

if __name__ == '__main__':
    app.run(debug=True)

# OV/Ev 인증서 사용 시 주의 사이트 아님
# SLD.kr이 1이 return되면 주의 사이트 아님 (정부기관 사이트)
# 유사도 체크에서 공식 사이트가 return되면 주의 사이트 아님 (공식 사이트와 100% 일치)

# 유사도 체크에서 피싱 의심 사이트가 return 될 시 점수 마이너스
# SSL 유효성에서 0이 return될 시 점수 마이너스
# 서브 도메인 개수가 2가 넘어갈 시 점수 마이너스ㅇ