# Drill 11

Python 3.11, Pico2D 1.5.1, transitions 0.9.3을 사용한다.

```text
python -m pip install -r requirements.txt
python main.py
```

이 PC에서는 `C:\Users\3este\miniconda3\envs\game2d\python.exe main.py`로 실행할 수 있다.

`run_game.cmd`를 더블클릭해도 실행된다. 이미 켜 둔 게임은 닫고 다시 실행해야 변경이 반영된다.

좌우 방향키는 달리기, A·D는 좌우 자동 달리기, Esc는 종료다. 대기 5초 후 수면에 들어가며 방향키 또는 A·D로 깨어난다.

좌우 동시 입력은 정지하고, 같은 프레임에 A·D를 누르면 D가 우선한다. 자동 달리기는 5초 동안 가속·감속하며 방향키를 누르면 수동 RUN으로 전환한다. 종료 후 유지 중인 방향키는 놓았다가 다시 눌러야 한다.

충돌과 바닥 정렬은 이미지의 투명 여백을 제외한 실제 몸을 기준으로 한다. 수면 자세도 회전 후의 몸 아래쪽을 땅에 맞춘다. 영역 정보는 `sprite_bounds.json`에 있다.

한국어 상태도는 `state_diagram.png`, UML 원본은 `state_diagram.puml`이다. 원본의 연결이나 배치를 바꾸면 `tools/render_state_diagram.py`도 함께 조정한다. PNG 재생성과 프레임 영역 추출 도구에는 Pillow가 필요하며 게임 실행에는 필요하지 않다.

사용자 요청에 따라 마지막 충돌·바닥 정렬 수정 후에는 테스트를 추가 실행하지 않았다. 앞선 14개 검사 통과 기록은 수정 전 결과다.
