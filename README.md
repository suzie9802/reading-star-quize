# ⭐ Reading Star Quiz

AR(르네상스 Accelerated Reader) 스타일의 영영 독후 퀴즈 웹앱입니다.
책을 읽고 책당 5문제를 풀면, 4문제(80%) 이상 맞혔을 때 그 책의 스티커를 받아 **Sticker Book**에 모을 수 있습니다.

- 라이브 주소: **https://suzie9802.github.io/reading-star-quiz/**
- 아이폰 Safari 기준으로 만들었습니다. 홈 화면에 추가하면 앱처럼 열립니다(공유 → 홈 화면에 추가).

## 수록 도서

| 표지 | 제목 | 저자 | AR |
|---|---|---|---|
| 🚀 | Stanley in Space | Jeff Brown | BL 3.9 · 1.0 pts (Quiz 23559) |
| 🪁 | Flat Stanley | Jeff Brown | BL 4.0 · 1.0 pts (Quiz 13392) |

AR 수치는 르네상스 AR BookFinder(arbookfind.com)의 해당 퀴즈 페이지에서 확인한 값입니다.
표지 이미지는 `covers/` 폴더에 직접 저장해 두어서 외부 사이트가 바뀌어도 엑박이 나지 않습니다.

## 새 책 추가하는 방법

### 1) 채팅으로 책 제목만 알려주는 경우
`books.json`에 아래 형식으로 한 권을 추가하면 됩니다(이 작업은 Pickle이 대신 해 드립니다).

```json
{
  "id": "mercy-watson-to-the-rescue",
  "title": "Mercy Watson to the Rescue",
  "author": "Kate DiCamillo",
  "series": "Mercy Watson",
  "cover": "covers/mercy-watson.jpg",
  "ar": { "bl": 2.7, "points": 0.5, "quiz": 88160, "interest": "LG" },
  "sticker": { "emoji": "🐷", "name": "Porcine Pal", "bg": "linear-gradient(135deg,#F59E0B 0%,#F97316 100%)" },
  "questions": [
    {
      "q": "Why did Mercy Watson wake up the Watsons?",
      "options": ["She was hungry.", "She wanted a bath.", "She heard a noise.", "She was cold."],
      "answer": 0,
      "explain": "Mercy woke up because she wanted a bedtime snack — toast with butter!"
    }
  ]
}
```

- `questions`는 **정확히 5개**, 각 문제는 **4지선다**, `answer`는 0부터 시작(A=0, B=1, C=2, D=3)입니다.
- `explain`은 정답 확인 후 보여 줄 짧은 영어 해설입니다.
- `sticker.bg`는 스티커 카드 배경 그라데이션이고, 비워도 기본값이 들어갑니다.

### 2) 스크립트로 추가하기

```bash
python3 add_book.py --list          # 지금 들어 있는 책 보기
python3 add_book.py                 # 질문에 답하면서 한 권 추가
python3 add_book.py --file new.json # 준비된 JSON 한 권 가져오기
python3 add_book.py --check         # books.json 형식 검사
```

### 3) 반영하기

```bash
git add -A && git commit -m "Add <책 제목>" && git push
```

GitHub Pages가 1~2분 안에 새 버전을 내보냅니다. 앱에서 새로고침만 하면 추가한 책이 보입니다.

## 파일 구조

```
index.html          앱 전체(화면, 퀴즈 엔진, 스티커, 저장/내보내기)
books.json          책 데이터 — 책·AR 점수·5문제·스티커
covers/             책 표지 이미지 (로컬 저장, 엑박 없음)
add_book.py         새 책 추가 도우미
```

## 동작 방식

- **문제**: 책당 5문제, 4지선다, 전부 영어. 문제를 읽어 주는 🔊 버튼이 있습니다(iOS 영어 음성).
- **진행률**: 1/5 ~ 5/5 표시와 진행 바.
- **피드백**: 선택하면 바로 정답/오답 표시 + 짧은 영어 해설. 틀려도 다그치지 않는 문장으로 되어 있습니다.
- **스티커**: 5문제 중 4문제 이상(80%)이면 색종이 애니메이션과 함께 스티커 획득.
- **Sticker Book**: 이미 받은 스티커는 반짝이고, 아직 못 받은 스티커는 자물쇠로 표시됩니다.
- **저장**: 이 기기의 브라우저 저장소(localStorage)에 저장. Sticker Book 화면 아래 **Export**로 JSON 백업, **Import**로 복원, **Reset**으로 초기화.

## 만든 방식 메모

- iOS Safari에서 버튼 터치가 씹히지 않도록 `touch-action: manipulation`, 표준 `<button>` + `click` 핸들러, `-webkit-tap-highlight-color: transparent`, 안전 영역(`env(safe-area-inset-*)`)을 적용했습니다.
- 저장은 try/catch로 감싸 사파리 프라이빗 모드처럼 저장이 막힌 환경에서도 앱이 멈추지 않습니다.
- 공개 저장소이므로 코드·HTML·커밋 메시지에 개인정보(아이 이름, 연락처 등)를 넣지 않았습니다.
