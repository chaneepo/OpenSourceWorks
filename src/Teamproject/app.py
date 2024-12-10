from flask import Flask, render_template, request, session, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = "your_secret_key"

# API 정보
API_URL = "http://apis.data.go.kr/B552657/HsptlAsembySearchService/getHsptlMdcncListInfoInqire"
SERVICE_KEY = "OOx8eZeg5kKlpLNPv03FH3Q5p0qaVYG/u7zLn7c9bAZNfzhFR/rAzrejjcnNQeleaiCI2ZvqjSPJaeqodVwfeg=="

# 병원별 대기열 저장소
waiting_lists = {}

@app.route('/')
def index():
    """메인 페이지: 최근 검색 기록 표시"""
    recent_searches = session.get("recent_searches", [])
    return render_template('index.html', recent_searches=recent_searches)


@app.route('/hospital-list', methods=['GET'])
def hospital_list():
    """병원 검색 결과 페이지"""
    query = request.args.get('query', '').lower()
    region = request.args.get('region', '').lower()
    district = request.args.get('district', '').lower()

    # API 호출
    params = {
        "ServiceKey": SERVICE_KEY,
        "Q0": region,
        "Q1": district,
        "ORD": "NAME",
        "pageNo": 1,
        "numOfRows": 10,
    }
    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        print(f"API 호출 실패: {response.status_code}")
        return "API 호출 실패", 500

    # XML 파싱
    root = ET.fromstring(response.content)
    items = root.findall(".//item")
    hospitals = []
    for item in items:
        hospital_id = item.findtext("hpid")
        hospitals.append({
            "id": hospital_id,
            "name": item.findtext("dutyName"),
            "address": item.findtext("dutyAddr"),
            "phone": item.findtext("dutyTel1"),
        })

        # 병원 ID가 waiting_lists에 없으면 추가
        if hospital_id not in waiting_lists:
            waiting_lists[hospital_id] = []

    return render_template('hospital_list.html', hospitals=hospitals)


@app.route('/hospital/<hospital_id>')
def hospital_detail(hospital_id):
    """병원 상세 페이지"""
    if hospital_id not in waiting_lists:
        return "잘못된 병원 ID입니다.", 404

    # 병원 대기열 상태 가져오기
    waiting_list = waiting_lists[hospital_id]
    return render_template('hospital_detail.html', hospital_id=hospital_id, waiting_list=waiting_list)


@app.route('/ticket/add/<hospital_id>', methods=['POST'])
def add_ticket(hospital_id):
    """번호표 추가 (Ajax 기반)"""
    if hospital_id not in waiting_lists:
        return jsonify({"error": "잘못된 병원 ID입니다."}), 404

    ticket_number = len(waiting_lists[hospital_id]) + 1
    waiting_lists[hospital_id].append(ticket_number)
    return jsonify({"message": "번호표 발급 성공", "ticket_number": ticket_number, "waiting_list": waiting_lists[hospital_id]})


@app.route('/ticket/remove/<hospital_id>', methods=['POST'])
def remove_ticket(hospital_id):
    """대기열 번호 제거 (Ajax 기반)"""
    if hospital_id not in waiting_lists:
        return jsonify({"error": "잘못된 병원 ID입니다."}), 404

    if waiting_lists[hospital_id]:
        removed_ticket = waiting_lists[hospital_id].pop(0)
        return jsonify({"message": "번호표 제거 성공", "removed_ticket": removed_ticket, "waiting_list": waiting_lists[hospital_id]})
    else:
        return jsonify({"error": "대기열이 비어 있습니다."}), 400


if __name__ == '__main__':
    app.run(debug=True)