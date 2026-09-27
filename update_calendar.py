import os
import re

# 파일 경로 설정
txt_path = 'schedule.txt'
html_path = 'calendar.html'

def parse_schedule():
    if not os.path.exists(txt_path):
        print(f"Error: {txt_path} 파일이 존재하지 않습니다.")
        return None

    # 2007년부터 2080년까지 처리할 수 있도록 딕셔너리 확장 생성
    data = {str(year): [] for year in range(2007, 2081)}
    current_year = None

    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 연도 체크 (2007년부터 2080년까지 매칭 가능하도록 정규식 수정)
            year_match = re.match(r'^\[(20[0-7][0-9]|2080)\]$', line)
            if year_match:
                key = year_match.group(1)
                if key in data:
                    current_year = key
                continue
            
            # 데이터 파싱 (| 구분자 이용)
            if current_year and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) == 4:
                    date, event, works, location = parts
                    
                    # 곡목: // 기호를 분리하여 리스트 형태로 HTML 생성
                    works_list = [w.strip() for w in works.split('//') if w.strip()]
                    if len(works_list) > 1:
                        works_html = "".join([f"<div class='work-item'>• {w}</div>" for w in works_list])
                    elif len(works_list) == 1:
                        works_html = f"<div class='work-item'>• {works_list[0]}</div>"
                    else:
                        works_html = ""
                    
                    # 장소: // 기호를 HTML 줄바꿈 태그(<br />)로 치환
                    location_html = "<br />".join([l.strip() for l in location.split('//')])
                    
                    row_html = f"""\t\t\t\t\t\t\t\t\t<tr>
\t\t\t\t\t\t\t\t\t\t<td class="date-col">{date}</td>
\t\t\t\t\t\t\t\t\t\t<td class="event-col">{event}</td>
\t\t\t\t\t\t\t\t\t\t<td class="works-col">{works_html}</td>
\t\t\t\t\t\t\t\t\t\t<td class="location-col">{location_html}</td>
\t\t\t\t\t\t\t\t\t</tr>"""
                    data[current_year].append(row_html)
    return data

def build_html(schedule_data):
    # 2080년부터 2007년까지 역순으로 탭 및 섹션 생성
    sections_html = ""
    years = [str(y) for y in range(2080, 2006, -1)]
    
    # 웹사이트 접속 시 기본으로 활성화할 연도 선택 (현재 시점인 2026년을 기본값으로 설정)
    default_active_year = '2026'
    
    for year in years:
        # 해당 연도에 등록된 공연 일정이 있을 때만 HTML 테이블 구조 생성 (출력 최적화)
        if schedule_data[year]:
            active_class = " active" if year == default_active_year else ""
            rows = "\n".join(schedule_data[year])
            
            sections_html += f"""\t\t\t\t\t<div id="year-{year}" class="calendar-content{active_class}">
\t\t\t\t\t\t<h2 style="font-weight: 700; margin-bottom: 2rem;">{year} Concerts</h2>
\t\t\t\t\t\t<div class="table-wrapper">
\t\t\t\t\t\t\t<table class="calendar-table">
\t\t\t\t\t\t\t\t<thead>
\t\t\t\t\t\t\t\t\t<tr>
\t\t\t\t\t\t\t\t\t\t<th class="date-col">Date / Time</th>
\t\t\t\t\t\t\t\t\t\t<th class="event-col">Event</th>
\t\t\t\t\t\t\t\t\t\t<th class="works-col">Works</th>
\t\t\t\t\t\t\t\t\t\t<th class="location-col">Location</th>
\t\t\t\t\t\t\t\t\t</tr>
\t\t\t\t\t\t\t\t</thead>
\t\t\t\t\t\t\t\t<tbody>
{rows}
\t\t\t\t\t\t\t\t</tbody>
\t\t\t\t\t\t\t</table>
\t\t\t\t\t\t</div>
\t\t\t\t\t\t<div class="calendar-footnote" style="margin-top: 2rem; font-size: 0.85rem; opacity: 0.7; text-align: left; line-height: 1.6;">
\t\t\t\t\t\t\t*CNSMDP = Conservatoire National Supérieur de Musique et de Danse de Paris (Paris Conservatory)<br />
\t\t\t\t\t\t\t*MDW = Universität für Musik und darstellende Kunst Wien (University of Music and Performing Arts Vienna)<br />
\t\t\t\t\t\t\t*IMD = Internationales Musikinstitut Darmstadt / Darmstädter Ferienkurse / Internationale Ferienkurse für Neue Musik (Darmstadt Summer Course)<br />
\t\t\t\t\t\t\t*MUMOK = Museum moderner Kunst Stiftung Ludwig Wien (Museum of modern art, Ludwig Foundation, Vienna)<br />
\t\t\t\t\t\t\t*ESMUC = Escola Superior de Música de Catalunya<br />
\t\t\t\t\t\t\t*Conservatoire d'Aulnay CRD = Conservatoire de Musique et de Danse à Rayonnement départemental Aulnay-sous-Bois
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>\n\n"""

    # 데이터가 존재하는 연도들만 상단 탭 리스트로 동적 추출
    active_years = [y for y in years if schedule_data[y]]
    
    # 만약 모든 연도에 일정이 하나도 없다면 예외적으로 2026년 기본 안내 테이블 출력
    if not active_years:
        active_years = [default_active_year]
        sections_html = f"""\t\t\t\t\t<div id="year-{default_active_year}" class="calendar-content active">
\t\t\t\t\t\t<h2 style="font-weight: 700; margin-bottom: 2rem;">{default_active_year} Concerts</h2>
\t\t\t\t\t\t<div class="table-wrapper">
\t\t\t\t\t\t\t<table class="calendar-table">
\t\t\t\t\t\t\t\t<thead>
\t\t\t\t\t\t\t\t\t<tr>
\t\t\t\t\t\t\t\t\t\t<th class="date-col">Date / Time</th>
\t\t\t\t\t\t\t\t\t\t<th class="event-col">Event</th>
\t\t\t\t\t\t\t\t\t\t<th class="works-col">Works</th>
\t\t\t\t\t\t\t\t\t\t<th class="location-col">Location</th>
\t\t\t\t\t\t\t\t\t</tr>
\t\t\t\t\t\t\t\t</thead>
\t\t\t\t\t\t\t\t<tbody>
\t\t\t\t\t\t\t\t\t<tr><td colspan='4' style='text-align:center;'>No concerts scheduled.</td></tr>
\t\t\t\t\t\t\t\t</tbody>
\t\t\t\t\t\t\t</table>
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>"""

    tabs_html = ""
    for y in active_years:
        tab_active = " active" if y == default_active_year else ""
        tabs_html += f"""\t\t\t\t\t\t<li><a href="#" class="tab-link{tab_active}" data-year="{y}">{y}</a></li>\n"""

    # 전체 HTML 템플릿 조립
    full_html = f"""<!DOCTYPE HTML>
<html>
    <head>
        <title>Youngseo Kim - Calendar</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
        <link rel="stylesheet" href="assets/css/main.css" />
        <noscript><link rel="stylesheet" href="assets/css/noscript.css" /></noscript>
        <style>
            /* 1. 세련된 미니멀 단색 배경 처리 */
            body {{
                background: #0f0f11 !important; 
                background-image: none !important;
            }}
            body::before, body::after {{
                display: none !important; 
            }}
            #wrapper {{
                background: transparent !important;
                background-image: none !important;
            }}

            /* 2. 상단 고정형 헤더 & 내비게이션 */
            #custom-header-nav {{
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 4rem !important; 
                background: rgba(15, 15, 17, 0.95) !important; 
                border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                padding: 0 4rem !important;
                z-index: 10000 !important;
                box-sizing: border-box;
            }}

            .nav-logo {{
                font-size: 1.2rem;
                font-weight: 700;
                letter-spacing: 0.1em;
                color: #ffffff;
                text-transform: uppercase;
            }}

            #nav {{
                position: relative !important;
                background: transparent !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
                width: auto !important;
                height: auto !important;
                top: auto !important;
                right: auto !important;
                left: auto !important;
            }}
            #nav ul {{
                display: flex !important;
                flex-direction: row !important;
                list-style: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }}
            #nav ul li {{
                padding: 0 !important;
                margin: 0 !important;
            }}
            #nav ul li a {{
                display: block !important;
                height: 4rem !important;
                line-height: 4rem !important;
                padding: 0 1.25rem !important;
                color: rgba(255, 255, 255, 0.6) !important;
                font-size: 0.85rem !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em;
                border: none !important;
                background: transparent !important;
                transition: color 0.2s ease;
            }}
            #nav ul li a:hover, #nav ul li a.active {{
                color: #ffffff !important;
                background: transparent !important;
            }}
            
            #wrapper {{
                padding-top: 6rem !important;
            }}

            .main header.major h2::after,
            .main header.major::after,
            .contact-major h2::after {{
                background-color: #000000 !important;
                background: #000000 !important;
            }}
            
            #footer {{
                border-top: none !important;
                padding: 0 !important;
            }}
            
            #contact {{
                margin-top: 6rem !important;
                padding-top: 2rem;
            }}
            
            .contact-major h2 {{
                position: relative;
                padding-bottom: 1rem;
                margin-bottom: 3rem;
            }}
            .contact-major h2::after {{
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 1px;
                display: block;
            }}

            .brunch-svg-link {{
                display: inline-flex !important;
                align-items: center;
                justify-content: center;
                vertical-align: middle;
            }}
            .brunch-svg-link svg {{
                width: 1.1rem;
                height: 1.1rem;
                fill: fill;
                transition: fill 0.2s ease;
            }}
            
            .copyright {{
                margin-top: 4rem !important;
                padding-bottom: 4rem;
            }}

            /* 연도 선택 탭 스타일 수정 - 글자 가독성 완전 확보 */
            .calendar-tabs {{ 
                margin-bottom: 4rem !important; 
                text-align: center !important;
                list-style: none !important;
                padding: 0 !important;
                display: flex !important;
                justify-content: center !important;
                gap: 0.6em !important;
                flex-wrap: wrap !important;
            }}
            .calendar-tabs li {{ 
                padding: 0 !important; 
                margin: 0 !important; 
            }}
            .calendar-tabs li a {{ 
                display: block !important;
                background-color: transparent !important;
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.3) !important; /* 명확한 테두리선 선언 */
                color: #888888 !important; /* 마우스 안 올라갔을 때 확실히 보이는 진한 회색으로 변경 */
                padding: 0 1.5em !important;
                height: 2.5em !important;
                line-height: 2.5em !important;
                font-size: 0.85em !important;
                letter-spacing: 0.1em !important;
                border-radius: 4px !important;
                text-decoration: none !important;
                font-weight: normal !important;
                transition: all 0.2s ease-in-out !important;
            }}
            /* 활성화(active) 되었거나 마우스를 올렸을(hover) 때 반전 스타일 적용 */
            .calendar-tabs li a.active, .calendar-tabs li a:hover {{ 
                background-color: #ffffff !important;
                color: #0f0f11 !important; /* 배경이 흰색이므로 선명한 차콜 블랙 글씨로 고정 */
                font-weight: bold !important; /* 굵은 글씨체 강제 적용 */
                box-shadow: none !important;
            }}
            
            .calendar-content {{ display: none; }}
            .calendar-content.active {{ display: block; }}
            
            .calendar-table {{ width: 100%; margin-top: 1rem; table-layout: fixed; border-collapse: collapse; }}
            .calendar-table th {{ font-weight: 700; color: #ffffff; border-bottom: 2px solid rgba(255, 255, 255, 0.1); padding: 0.75rem; text-align: left; }}
            .calendar-table td {{ padding: 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); vertical-align: top; word-break: break-word; font-weight: 400 !important; font-size: 0.9rem; line-height: 1.6; }}
            
            .work-item {{
                position: relative;
                padding-left: 1rem;
                text-indent: -1rem;
                margin-bottom: 0.25rem;
            }}
            .work-item:last-child {{
                margin-bottom: 0;
            }}
            
            .calendar-table .date-col {{ width: 15%; }}
            .calendar-table .event-col {{ width: 30%; }}
            .calendar-table .works-col {{ width: 35%; }}
            .calendar-table .location-col {{ width: 20%; }}
            
            @media screen and (max-width: 980px) {{
                #custom-header-nav {{
                    position: relative !important;
                    flex-direction: column !important;
                    height: auto !important;
                    padding: 1rem !important;
                }}
                #nav ul {{
                    flex-wrap: wrap !important;
                    justify-content: center !important;
                }}
                #nav ul li a {{
                    height: 3rem !important;
                    line-height: 3rem !important;
                    padding: 0 0.75rem !important;
                }}
                #wrapper {{
                    padding-top: 1rem !important;
                }}
                #contact {{ margin-top: 4rem !important; }}
            }}

            @media screen and (max-width: 736px) {{ 
                .calendar-table {{ table-layout: auto; }} 
                .calendar-table .date-col, .calendar-table .event-col, .calendar-table .works-col, .calendar-table .location-col {{ width: auto; }} 
            }}
        </style>
    </head>
    <body class="is-preload">

	<div id="custom-header-nav">
		<div class="nav-logo"><a href="index.html">Youngseo Kim</a></div>
		<nav id="nav">
			<ul>
				<li><a href="biography.html">Biography</a></li>
				<li><a href="calendar.html">Calendar</a></li>
				<li><a href="watch.html">Watch</a></li>
				<li><a href="projects.html">Projects</a></li>
				<li><a href="research.html">Research</a></li>
				<li><a href="works.html">Works</a></li>
				<li><a href="index.html#contact">Contact</a></li>
			</ul>
		</nav>
	</div>

        <div id="wrapper">
            <div id="main">
                <section class="main">
                    <header class="major">
                        <h2>Calendar</h2>
                    </header>
                    <ul class="calendar-tabs">
{tabs_html}\t\t\t\t\t</ul>
{sections_html}\t\t\t\t</section>
            </div>
            <footer id="footer">
                  <p class="copyright">&copy; Youngseo Kim</p>
            </footer>

        </div>

        <script src="assets/js/jquery.min.js"></script>
        <script src="assets/js/jquery.scrollex.min.js"></script>
        <script src="assets/js/jquery.scrolly.min.js"></script>
        <script src="assets/js/browser.min.js"></script>
        <script src="assets/js/breakpoints.min.js"></script>
        <script src="assets/js/util.js"></script>
        <script src="assets/js/main.js"></script>
        <script>
            document.querySelectorAll('.tab-link').forEach(tab => {{
                tab.addEventListener('click', function(e) {{
                    e.preventDefault();
                    document.querySelectorAll('.tab-link').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    const targetYear = this.getAttribute('data-year');
                    document.querySelectorAll('.calendar-content').forEach(content => {{ content.classList.remove('active'); }});
                    document.getElementById('year-' + targetYear).classList.add('active');
                }});
            }});
        </script>
    </body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print("calendar.html 컴파일 완료.")

if __name__ == "__main__":
    schedule_data = parse_schedule()
    if schedule_data:
        build_html(schedule_data)