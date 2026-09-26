# -*- coding: utf-8 -*-
"""S#8 위장사무실 — 10블록 프롬프트 본문(한/영) 데이터.
build_s8.py 가 이 데이터를 지오메트리와 합쳐 씬 JSON을 만든다.
규칙 근거: SKILL §5(한 정보=한 블록) §6(포지티브 락) §7(@태그 인라인) §7-C(파트 로컬 번호)
          §10(화각 9단계 앵커) references/cut-linking.md(컷 연결 6규칙)
"""

# 씬 전역 태그 — 파트가 바뀌어도 절대 안 바뀜 (§7-C ②)
GLOBAL = {
    "hyunwoo": "@Image_hyunwoo", "daehan": "@Image_daehan", "baksu": "@Image_baksu",
    "minhee": "@Image_minhee", "kkangchul": "@Image_kkangchul", "chaokbun": "@Image_chaokbun",
    "office_wide": "@Image_office_wide", "office_cabinets": "@Image_office_cabinets",
}
NAME = {"hyunwoo": "현우", "daehan": "방대한", "baksu": "박수", "minhee": "민희",
        "kkangchul": "깡철이", "chaokbun": "차옥분",
        "office_wide": "0과 위장사무실(와이드)", "office_cabinets": "캐비넷 통로 구역"}
NAME_EN = {"hyunwoo": "Hyunwoo", "daehan": "Daehan", "baksu": "Baksu", "minhee": "Minhee",
           "kkangchul": "Kkangchul", "chaokbun": "Cha Okbun",
           "office_wide": "Division Zero cover office (wide)", "office_cabinets": "cabinet passage area"}
ROLE = {
    "hyunwoo": ("디비전 제로 신입, 20대 남성", "a man in his twenties, new recruit of Division Zero",
                "얼굴과 옷에만 쓴다", "face and clothing only"),
    "daehan": ("0과 과장 방대한, 50대 남성", "Daehan, section chief in his fifties",
               "얼굴과 옷에만 쓴다", "face and clothing only"),
    "baksu": ("0과 소속 박수, 30대 남성", "Baksu, a man in his thirties attached to Division Zero",
              "얼굴과 옷에만 쓴다", "face and clothing only"),
    "minhee": ("0과 소속 민희, 20대 여성", "Minhee, a woman in her twenties attached to Division Zero",
               "얼굴과 옷에만 쓴다", "face and clothing only"),
    "kkangchul": ("박수의 도마뱀 깡철이", "Kkangchul, Baksu's lizard",
                  "생김새·크기만", "creature shape and scale only"),
    "chaokbun": ("현우의 모친 차옥분, 30대 여성", "Cha Okbun, Hyunwoo's mother, a woman in her thirties",
                 "얼굴과 옷에만 쓴다", "face and clothing only"),
    "office_wide": ("창문 없는 낡은 사무실 전체", "the whole windowless old office",
                    "공간·조명 기준", "space and lighting reference"),
    "office_cabinets": ("철제 캐비넷이 늘어선 통로", "the aisle lined with steel cabinets",
                        "공간 기준", "space reference"),
}
# 파트별 업로드 순서 = 파트 로컬 번호 (§7-C ①)
ORDER = {
    "A": ["hyunwoo", "daehan", "office_wide"],
    "B": ["hyunwoo", "daehan", "office_wide"],
    "C": ["hyunwoo", "daehan", "baksu", "kkangchul", "chaokbun", "office_wide", "office_cabinets"],
    "D": ["hyunwoo", "daehan", "baksu", "kkangchul", "office_wide"],
    "E": ["hyunwoo", "daehan", "baksu", "minhee", "kkangchul", "office_wide", "office_cabinets"],
}
PEOPLE = {"hyunwoo", "daehan", "baksu", "minhee", "kkangchul", "chaokbun"}

TITLE = {"A": "철문이 열리고 — 첫 대면", "B": "모친의 비밀", "C": "캐비넷에서 나온 박수와 깡철이",
         "D": "깡철이 소동", "E": "민희의 경고 — 캐비넷으로"}

# ── 03 공간·조명 (조명·색감은 여기서만 — §5) ─────────────────────────────
def b03(tag):
    ko = (f"{tag} — 0과 위장사무실. 창문 없는 가로 9미터·세로 7미터 실내, 천장 높이 2.6미터. "
          "낡은 천장 형광등이 4300K 푸른 흰빛을 균일하게 깔고, 책상마다 켜진 노란 백열 스탠드(2700K)가 "
          "책상 위에만 따뜻한 웅덩이를 만든다. 깊이 레이어 — 전경: 산처럼 쌓인 서류더미와 낡은 책상 모서리. "
          "중경: 공동 데스크와 그 앞 통로. 후경: 북측 서류 책장과 철제 사물함 벽. "
          "최후경: 창고 사물함 사이로 열린 어두운 통로. 사물함과 창고 사물함 사이 통로가 이 파트의 주 동선이며, "
          "좌측은 서류 책장, 우측은 복사기 구역으로 열린다.")
    en = (f"{tag} — Division Zero's cover office. A windowless interior 9 meters wide and 7 meters deep, "
          "ceiling 2.6 meters high. Aged ceiling fluorescents lay down an even 4300K blue-white, while the yellow "
          "incandescent desk lamps (2700K) pool warm light only on the desktops. Depth layers — foreground: "
          "mountains of stacked paperwork and the corners of battered desks. Mid-ground: the shared desks and the "
          "aisle in front of them. Background: the north file shelves and the wall of steel lockers. Far background: "
          "the dark passage opening between the storage lockers. The aisle between the lockers and the storage "
          "lockers is this part's main path, open to the file shelves on the left and the copier area on the right.")
    return ko, en

# ── 05 소품·의상 (형태·재질·색은 여기서만) ──────────────────────────────
def b05(who):
    ko = ["서류더미 — 누렇게 변색된 갱지 수백 장, 모서리가 말린 채 책상 위에 사람 키만큼 쌓여 있다. 형태는 처음부터 끝까지 동일하다.",
          "낡은 벽시계 — 흰 문자판, 검은 테, 초침만 움직인다.",
          "철제 사물함 — 찌그러진 회색 철제, 손잡이에 벗겨진 페인트. 문이 통로로 열린다."]
    en = ["Stacked paperwork — hundreds of yellowed sheets, corners curled, piled shoulder-high on the desk. Identical form throughout.",
          "An old wall clock — white dial, black rim, only the second hand moving.",
          "Steel lockers — dented grey steel, paint flaked off the handles. One door opens onto the passage."]
    W = {"hyunwoo": ("현우의 의상 — 짙은 남색 정장에 헐거운 흰 셔츠, 맨 위 단추만 채움.",
                     "Hyunwoo's wardrobe — a dark navy suit with a loose white shirt, only the top button fastened."),
         "daehan": ("방대한의 의상 — 갈색 니트 조끼, 소매 걷은 흰 셔츠, 검은 뿔테 안경.",
                    "Daehan's wardrobe — a brown knit vest over a white shirt with sleeves rolled, black horn-rimmed glasses."),
         "baksu": ("박수의 의상 — 베이지 점퍼, 목 늘어난 회색 티셔츠.",
                   "Baksu's wardrobe — a beige jacket over a stretched grey T-shirt."),
         "minhee": ("민희의 의상 — 붉은 체크 남방, 청바지, 갈색 카우보이 부츠.",
                    "Minhee's wardrobe — a red plaid shirt, jeans, and brown cowboy boots."),
         "kkangchul": ("깡철이 — 손바닥만 한 크기, 칙칙한 올리브빛 비늘, 목 아래 주름.",
                       "Kkangchul — palm-sized, dull olive scales, a wrinkled throat."),
         "chaokbun": ("차옥분 — 흰 소복, 풀린 머리, 굿당 촛불 아래.",
                      "Cha Okbun — white ritual robes, hair unbound, under shrine candlelight.")}
    for cid in who:
        if cid in W:
            ko.append(W[cid][0]); en.append(W[cid][1])
    return "\n".join(ko), "\n".join(en)

# ── 06 퍼포먼스 ────────────────────────────────────────────────────────
PERF = {
 "A": ("[자세] 두 인물은 이 파트 내내 서 있다.\n"
       "· 방대한 — 고개를 숙인 채 서류에서 시선을 떼지 않는다. 어깨는 굳어 있고 종이 넘기는 손만 움직인다.\n"
       "· 현우 — 문 앞에서 멈춰 선 긴장 상태. 헛기침을 한 번 하고 허리를 살짝 숙여 인사한다.",
       "[POSTURE] Both remain standing throughout this part.\n"
       "· Daehan — head lowered, eyes never leaving the paperwork. His shoulders are stiff; only the hand turning pages moves.\n"
       "· Hyunwoo — held tight at the doorway. He gives one dry cough and bows slightly in greeting."),
 "B": ("[자세] 두 인물은 이 파트 내내 서 있다.\n"
       "· 방대한 — 서류를 읽던 손을 멈추고 시선만 들어 현우를 응시한다. 표정은 읽히지 않는다.\n"
       "· 현우 — 모친 이야기가 나오자 턱에 힘이 들어가지만 대답은 짧게 끊는다.",
       "[POSTURE] Both remain standing throughout this part.\n"
       "· Daehan — his page-turning hand stops and he lifts only his eyes to hold Hyunwoo's face. His expression stays unreadable.\n"
       "· Hyunwoo — his jaw tightens at the mention of his mother, but he keeps his answer short."),
 "C": ("[자세] 인물들은 이 파트 내내 서 있다.\n"
       "· 박수 — 캐비넷 문을 밀고 나오며 밝게 웃다가, 악수하는 도중 웃음기가 천천히 빠지고 어깨가 잘게 떨린다.\n"
       "· 현우 — 낯선 등장에 몸을 반쯤 돌렸다가 악수에 응한다. 깡철이를 보고 눈을 크게 뜬다.\n"
       "· 방대한 — 자리에서 시선만 옮겨 상황을 지켜본다.\n"
       "· 깡철이 — 박수 어깨 위에서 미동 없이 앉았다가 몸을 낮춘다.",
       "[POSTURE] All remain standing throughout this part.\n"
       "· Baksu — pushes the cabinet door open with a bright smile; mid-handshake the smile slowly drains and his shoulders quiver.\n"
       "· Hyunwoo — half turns at the unexpected entrance, then meets the handshake. His eyes widen at the lizard.\n"
       "· Daehan — watches from his desk, moving only his eyes.\n"
       "· Kkangchul — sits motionless on Baksu's shoulder, then lowers its body."),
 "D": ("[자세] 인물들은 이 파트 내내 서 있다.\n"
       "· 현우 — 손등 위에 깡철이를 떠받친 채 엉덩이를 뒤로 뺀 자세로 굳는다. 목소리가 반 톤 올라간다.\n"
       "· 박수 — 억지웃음을 지으며 손을 내젓다가, 깡철이를 받아 든다.\n"
       "· 깡철이 — 현우의 어깨, 가슴, 배를 기어 오르다 손등 위에 올라앉는다. 움직임은 느리고 집요하다.\n"
       "· 방대한 — 서류를 덮지 않은 채 곁눈으로만 본다.",
       "[POSTURE] All remain standing throughout this part.\n"
       "· Hyunwoo — freezes with the lizard held up on the back of his hand, hips pulled back. His voice rises half a tone.\n"
       "· Baksu — waves it off with a forced laugh, then takes the lizard back.\n"
       "· Kkangchul — crawls up Hyunwoo's shoulder, chest, and belly, then settles on the back of his hand. Its movement is slow and insistent.\n"
       "· Daehan — watches from the corner of his eye without closing the file."),
 "E": ("[자세] 인물들은 이 파트 내내 서 있다.\n"
       "· 민희 — 캐비넷에서 나와 무표정으로 서류를 건네고, 팔짱을 낀 채 현우를 위아래로 훑는다.\n"
       "· 현우 — 손등 위 깡철이를 떠받친 자세 그대로 굳었다가, 지나가는 민희를 고개로 따라간다.\n"
       "· 박수 — 깡철이를 받아 들고 캐비넷 쪽으로 몸을 튼다.\n"
       "· 방대한 — 서류에서 시선을 들지 않은 채 한마디로 상황을 정리한다.\n"
       "· 깡철이 — 현우 손등에서 박수 손으로 옮겨 앉는다.",
       "[POSTURE] All remain standing throughout this part.\n"
       "· Minhee — steps out of the cabinet, hands over a file without expression, and looks Hyunwoo up and down with arms folded.\n"
       "· Hyunwoo — stays locked in the pose of holding the lizard, then follows Minhee with his head as she passes.\n"
       "· Baksu — takes the lizard back and turns toward the cabinets.\n"
       "· Daehan — closes the matter in one line without looking up from his paperwork.\n"
       "· Kkangchul — is passed from Hyunwoo's hand into Baksu's."),
}

# ── 08 컷 본문 (액션·타이밍은 여기서만) ─────────────────────────────────
# (ko_lines, en_lines) — 첫 줄은 타임코드, 두 번째 줄 자리에 공간 문장이 들어간다
CUT_TEXT = {
"CUT8-1": (["0-5초 — CUT8-1.",
            "끼이익 소리와 함께 철문이 열리고 {LOC} 낡은 사무실 안이 드러난다. @Image2 방대한이 안쪽 가장 높은 책상 뒤에서 고개를 숙인 채 서류를 읽고 있다. 카메라는 그의 등을 향해 천천히 앞으로 흘러 들어간다. 서류더미가 양옆으로 지나간다."],
           ["0-5s — CUT8-1.",
            "With a shriek of hinges the iron door opens and {LOC} the old office is revealed. @Image2 Daehan stands behind the tallest desk at the far end, head bent over paperwork. The camera drifts slowly forward toward his back as piles of documents pass on either side."]),
"CUT8-2": (["5-10초 — CUT8-2.",
            "@Image1 현우가 낡은 사무실 분위기를 둘러보다 헛기침을 하고 @Image2 방대한에게 인사한다. 방대한은 시선을 서류에 고정한 채 입을 연다.",
            "대사 — 방대한: {자네, 디비전 제로 자원했다며.}",
            "9.5초부터 0.5초 마이크로 파즈. 종이 넘기는 소리가 이어진다."],
           ["5-10s — CUT8-2.",
            "@Image1 Hyunwoo takes in the shabby office, gives a dry cough, and greets @Image2 Daehan. Daehan speaks without lifting his eyes from the paperwork.",
            "Dialogue — Daehan: {자네, 디비전 제로 자원했다며.}",
            "A 0.5s micro-pause from 9.5s. The sound of pages turning continues."]),
"CUT8-3": (["10-15초 — CUT8-3.",
            "(CUT8-2에서 이어) @Image1 현우가 사람을 쳐다보지도 않는 태도에 기분이 상하지만 참고 짧게 대답한다. @Image2 방대한의 어깨가 프레임 가장자리에 걸린다.",
            "대사 — 현우: {...예.}",
            "13초부터 0.5초 마이크로 파즈. 낡은 벽시계 초침 소리가 남는다."],
           ["10-15s — CUT8-3.",
            "(continuing from CUT8-2) @Image1 Hyunwoo is stung by being addressed without eye contact but holds it in and answers shortly. @Image2 Daehan's shoulder sits at the frame edge.",
            "Dialogue — Hyunwoo: {...예.}",
            "A 0.5s micro-pause from 13s. The ticking of the old wall clock remains."]),
"CUT8-4": (["0-6초 — CUT8-4.",
            "{LOC} 사무실 안, @Image2 방대한이 일을 멈추고 시선을 들어 @Image1 현우를 응시하며 말한다. @Image1 현우의 어깨가 굳는다.",
            "대사 — 방대한: {무속인 모친은 1998년 실종. 그 양반이 자네한테 뭔 짓을 해 놨는지... 그게 궁금해서 받았어.}"],
           ["0-6s — CUT8-4.",
            "Inside {LOC} the office, @Image2 Daehan stops working, lifts his eyes, and holds @Image1 Hyunwoo's gaze as he speaks. @Image1 Hyunwoo's shoulders stiffen.",
            "Dialogue — Daehan: {무속인 모친은 1998년 실종. 그 양반이 자네한테 뭔 짓을 해 놨는지... 그게 궁금해서 받았어.}"]),
"CUT8-5": (["6-11초 — CUT8-5.",
            "(CUT8-4에서 이어) @Image1 현우가 갑자기 모친 이야기를 꺼낸 데 기분이 상하지만 참으며 되묻는다. @Image2 방대한의 어깨가 프레임 아래쪽에 걸린다.",
            "대사 — 현우: {...제가 안 끌려간 거랑 관련 있습니까?}",
            "10초부터 0.5초 마이크로 파즈."],
           ["6-11s — CUT8-5.",
            "(continuing from CUT8-4) @Image1 Hyunwoo is stung by the sudden mention of his mother but holds it in and asks back. @Image2 Daehan's shoulder sits at the bottom of frame.",
            "Dialogue — Hyunwoo: {...제가 안 끌려간 거랑 관련 있습니까?}",
            "A 0.5s micro-pause from 10s."]),
"CUT8-6": (["11-18초 — CUT8-6.",
            "@Image2 방대한이 시선을 다시 서류로 내리며 짧게 답한다. @Image1 현우는 대답을 듣지 못한 채 그 자리에 남는다. 형광등 빛이 두 사람 사이를 가로막는다."],
           ["11-18s — CUT8-6.",
            "@Image2 Daehan drops his eyes back to the paperwork and answers shortly. @Image1 Hyunwoo is left standing without an answer. The fluorescent light cuts between them."]),
"CUT8-7": (["0-5.5초 — CUT8-7.",
            "{LOC} 사무실 안, {CAB} 캐비넷 통로 쪽 철제 사물함 문이 열리고 @Image3 박수가 불쑥 나온다. 어깨 위에는 @Image4 깡철이가 점잖게 앉아 있다. @Image1 현우가 놀라 돌아보고, 박수가 웃으며 악수를 청하자 손을 잡고 응한다. @Image2 방대한은 자리에서 그쪽을 본다.",
            "대사 — 박수: {안녕하세요~ 저는 박수라고 해요.}",
            "대사 — 현우: {이현우입니다.}"],
           ["0-5.5s — CUT8-7.",
            "Inside {LOC} the office, a steel locker door on the {CAB} cabinet aisle swings open and @Image3 Baksu pops out. @Image4 Kkangchul sits sedately on his shoulder. @Image1 Hyunwoo spins around in surprise; Baksu offers a handshake with a grin and Hyunwoo takes it. @Image2 Daehan looks over from his desk.",
            "Dialogue — Baksu: {안녕하세요~ 저는 박수라고 해요.}",
            "Dialogue — Hyunwoo: {이현우입니다.}"]),
"CUT8-8": (["5.5-8.5초 — CUT8-8.",
            "@Image3 박수의 얼굴에서 웃음기가 천천히 사라진다. 잡은 손에 힘이 들어가고 시선이 허공 어딘가에 못 박힌다."],
           ["5.5-8.5s — CUT8-8.",
            "The smile drains slowly from @Image3 Baksu's face. His grip tightens and his eyes lock on some point in empty air."]),
"CUT8-9": (["8.5-9초 — CUT8-9 (인서트).",
            "@Image5 차옥분의 환영. 촛불만 밝힌 어두운 굿당에서 그녀의 머리가 세차게 흔들리고 눈이 하얗게 뒤집혀 있다. 오래된 필름 그레인이 화면 전체를 덮는다.",
            "효과음: 굿방울 소리."],
           ["8.5-9s — CUT8-9 (insert).",
            "A vision of @Image5 Cha Okbun. In a dark shrine room lit only by candles her head shakes violently, her eyes rolled back to white. Old film grain covers the whole frame.",
            "SFX: the shake of shaman bells."]),
"CUT8-10": (["9-12초 — CUT8-10.",
            "(CUT8-8에서 이어) @Image3 박수가 경기 일으키듯 몸서리치며 @Image1 현우의 손을 놓는다. 어깨 위 @Image4 깡철이가 몸을 낮춘다. @Image1 현우는 놓인 손을 든 채 멈춘다."],
           ["9-12s — CUT8-10.",
            "(continuing from CUT8-8) @Image3 Baksu shudders as if seized by a fit and lets go of @Image1 Hyunwoo's hand. @Image4 Kkangchul lowers its body on his shoulder. @Image1 Hyunwoo stops with his released hand still raised."]),
"CUT8-11": (["0-3초 — CUT8-11.",
            "{LOC} 사무실 안, @Image1 현우가 박수의 갑작스러운 행동을 보고 놀라 묻는다.",
            "대사 — 현우: {뭡니까?}"],
           ["0-3s — CUT8-11.",
            "Inside {LOC} the office, @Image1 Hyunwoo starts at Baksu's sudden behavior and asks.",
            "Dialogue — Hyunwoo: {뭡니까?}"]),
"CUT8-12": (["3-9초 — CUT8-12.",
            "(CUT8-11에서 이어) @Image3 박수가 실례가 되지 않으려는 듯 억지웃음으로 너스레를 떤다. @Image2 방대한의 어깨가 프레임 가장자리에 걸린다. 그때 @Image4 깡철이가 박수 어깨에서 팍 뛰어 @Image1 현우 머리 쪽으로 옮겨 붙는다.",
            "대사 — 박수: {아! 아녀. 현우 씨 손이 좀 차네요. 으슬으슬....}",
            "대사 — 현우: {어.. 어...}",
            "효과음: 깡철이가 옷에 부비는 소리."],
           ["3-9s — CUT8-12.",
            "(continuing from CUT8-11) @Image3 Baksu covers it with a forced laugh so as not to give offense. @Image2 Daehan's shoulder sits at the frame edge. Then @Image4 Kkangchul springs off Baksu's shoulder and lands toward @Image1 Hyunwoo's head.",
            "Dialogue — Baksu: {아! 아녀. 현우 씨 손이 좀 차네요. 으슬으슬....}",
            "Dialogue — Hyunwoo: {어.. 어...}",
            "SFX: the lizard rustling against cloth."]),
"CUT8-13": (["9-13초 — CUT8-13.",
            "@Image4 깡철이가 @Image1 현우의 어깨, 가슴, 배를 기어 다니며 냄새를 맡다가 손등 위에 올라앉는다. 카메라는 그 움직임을 따라간다."],
           ["9-13s — CUT8-13.",
            "@Image4 Kkangchul crawls over @Image1 Hyunwoo's shoulder, chest, and belly, sniffing, then settles on the back of his hand. The camera follows the movement."]),
"CUT8-14": (["13-16.5초 — CUT8-14.",
            "@Image1 현우가 두 손으로 @Image4 깡철이를 떠받친 채 엉덩이를 뒤로 빼고 선 자세로 굳는다.",
            "대사 — 현우: {이, 이거 왜 이럽니까?! 도마뱀이 원래 이렇게 뜨겁습니까?!}",
            "효과음: 깡철이 숨 소리."],
           ["13-16.5s — CUT8-14.",
            "@Image1 Hyunwoo freezes, hips pulled back, holding @Image4 Kkangchul up with both hands.",
            "Dialogue — Hyunwoo: {이, 이거 왜 이럽니까?! 도마뱀이 원래 이렇게 뜨겁습니까?!}",
            "SFX: the lizard's breathing."]),
"CUT8-15": (["16.5-19.5초 — CUT8-15.",
            "@Image3 박수가 @Image1 현우의 반응을 보고 웃으며 말한다.",
            "대사 — 박수: {깡철이가 현우 씨 맘에 드나 보네여.}",
            "18.5초부터 0.5초 마이크로 파즈."],
           ["16.5-19.5s — CUT8-15.",
            "@Image3 Baksu watches @Image1 Hyunwoo's reaction and speaks with a laugh.",
            "Dialogue — Baksu: {깡철이가 현우 씨 맘에 드나 보네여.}",
            "A 0.5s micro-pause from 18.5s."]),
"CUT8-16": (["0-5초 — CUT8-16.",
            "{LOC} 사무실 안, @Image3 박수 뒤쪽 {CAB} 철제 캐비넷 문이 열리고 @Image4 민희가 나온다. 무표정한 얼굴로 @Image1 현우와 그의 손등 위 @Image5 깡철이를 힐끗 보고 지나치며 말한다.",
            "대사 — 민희: {좋겠네. 파충류한테 이쁨받아서.}"],
           ["0-5s — CUT8-16.",
            "Inside {LOC} the office, the {CAB} steel cabinet behind @Image3 Baksu opens and @Image4 Minhee steps out. Expressionless, she glances at @Image1 Hyunwoo and @Image5 Kkangchul on the back of his hand and speaks as she passes.",
            "Dialogue — Minhee: {좋겠네. 파충류한테 이쁨받아서.}"]),
"CUT8-17": (["5-9초 — CUT8-17.",
            "(CUT8-16에서 이어) @Image1 현우가 그 자세 그대로 움직이지 못한 채 지나가는 @Image4 민희를 고개로 따라가며 누군지 의아해한다."],
           ["5-9s — CUT8-17.",
            "(continuing from CUT8-16) @Image1 Hyunwoo, unable to move from that pose, follows the passing @Image4 Minhee with his head, wondering who she is."]),
"CUT8-18": (["9-14초 — CUT8-18.",
            "@Image4 민희가 붉은 체크 남방과 갈색 카우보이 부츠 차림으로 @Image2 방대한에게 서류를 건네고, 그 옆에 팔짱을 끼고 서서 @Image1 현우를 보며 말한다.",
            "대사 — 민희: {평균 8일. 도망가거나, 쓸모없거나. 둘 중 하나.}"],
           ["9-14s — CUT8-18.",
            "@Image4 Minhee, in a red plaid shirt and brown cowboy boots, hands a file to @Image2 Daehan, then stands beside him with arms folded and speaks looking at @Image1 Hyunwoo.",
            "Dialogue — Minhee: {평균 8일. 도망가거나, 쓸모없거나. 둘 중 하나.}"]),
"CUT8-19": (["14-18초 — CUT8-19.",
            "(CUT8-18에서 이어) @Image1 현우가 까칠한 말에 기분이 상한 걸 티내지 않으려고 참아낸다. 손등 위 @Image5 깡철이가 조금 움직이고, 그는 @Image4 민희가 선 캐비넷 쪽으로 몸을 돌린다."],
           ["14-18s — CUT8-19.",
            "(continuing from CUT8-18) @Image1 Hyunwoo swallows the sting of her blunt words without showing it. @Image5 Kkangchul shifts slightly on his hand, and he turns toward the cabinets where @Image4 Minhee stands."]),
"CUT8-20": (["18-23초 — CUT8-20.",
            "@Image2 방대한이 서류에서 시선을 들지 않은 채 지시한다. @Image4 민희가 팔짱을 풀고 @Image1 현우를 보며 {CAB} 캐비넷 쪽으로 걸어간다. @Image3 박수가 현우 손등의 @Image5 깡철이를 받아 들고 길을 안내한다. @Image1 현우도 따라 들어간다."],
           ["18-23s — CUT8-20.",
            "@Image2 Daehan gives the order without looking up from his paperwork. @Image4 Minhee unfolds her arms and walks toward the {CAB} cabinets, looking at @Image1 Hyunwoo. @Image3 Baksu takes @Image5 Kkangchul from Hyunwoo's hand and leads the way. @Image1 Hyunwoo follows them in."]),
"CUT8-21": (["23-26초 — CUT8-21.",
            "(CUT8-20에서 이어) @Image1 현우가 까칠한 민희를 떠올리며 기분이 상한 걸 참고 @Image3 박수의 안내를 받아 {CAB} 캐비넷 안으로 들어간다. 그의 등이 어둠 속으로 사라지며 프레임에서 벗어난다."],
           ["23-26s — CUT8-21.",
            "(continuing from CUT8-20) @Image1 Hyunwoo holds back his irritation at Minhee's bluntness and, guided by @Image3 Baksu, steps into the {CAB} cabinets. His back disappears into the dark and out of frame."]),
}

# ── 04 컷 목록(화각·샷사이즈·무브) — 카메라는 여기서만 ──────────────────
MOVE = {
 "CUT8-1": ("스테디캠 후방 트래킹", "Steadicam rear tracking"),
 "CUT8-2": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-3": ("로우앵글 핸드헬드", "low-angle handheld"),
 "CUT8-4": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-5": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-6": ("고정", "locked off"),
 "CUT8-7": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-8": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-9": ("고정 (0.5초 플래시)", "locked off (0.5s flash)"),
 "CUT8-10": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-11": ("고정", "locked off"),
 "CUT8-12": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-13": ("핸드헬드 팔로", "handheld follow"),
 "CUT8-14": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-15": ("고정", "locked off"),
 "CUT8-16": ("핸드헬드 팔로", "handheld follow"),
 "CUT8-17": ("고정", "locked off"),
 "CUT8-18": ("핸드헬드 미세 흔들림", "handheld with fine shake"),
 "CUT8-19": ("고정", "locked off"),
 "CUT8-20": ("스테디캠 전면 트래킹", "Steadicam front tracking"),
 "CUT8-21": ("핸드헬드 후퇴, 프레임아웃", "handheld pull-back, frame out"),
}
