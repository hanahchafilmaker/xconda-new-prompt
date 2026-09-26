/* ============================================================
   XCONDA · 자세(pose) 파서 v1  —  블로킹 보드 app.js에 붙여넣는 조각
   ------------------------------------------------------------
   하는 일 두 가지
   ① normalizePose(v)  : "sit" · "seated" · "앉아" 같은 값을 보드 표준어 "앉다"로 통일
   ② parsePose(text)   : 문장에서 자세를 읽어낸다 ("대한은 의자에 앉아 서류를 읽는다" → "앉다")
   ③ parsePoseFor(name, text) : 여러 사람이 섞인 문단에서 그 사람 절(節)만 골라 판정

   보드 표준어는 markers 규격(`pose:서다`)에 맞춰 한국어로 고정한다.
   ============================================================ */

var POSE_STAND = '서다', POSE_SIT = '앉다', POSE_LIE = '눕다', POSE_KNEEL = '무릎꿇다';

/* ① 값 정규화 — 씬 JSON이 "sit"으로 와도 보드는 "앉다"로 받는다 */
var POSE_ALIAS = {
  'sit': POSE_SIT, 'sits': POSE_SIT, 'sitting': POSE_SIT, 'seated': POSE_SIT, 'sat': POSE_SIT,
  'perch': POSE_SIT, 'perched': POSE_SIT, '착석': POSE_SIT, '앉음': POSE_SIT, '앉다': POSE_SIT, '앉아': POSE_SIT,
  'stand': POSE_STAND, 'stands': POSE_STAND, 'standing': POSE_STAND, 'stood': POSE_STAND,
  'idle': POSE_STAND, '기립': POSE_STAND, '서다': POSE_STAND, '서': POSE_STAND, '섬': POSE_STAND,
  'lie': POSE_LIE, 'lying': POSE_LIE, 'lies': POSE_LIE, 'prone': POSE_LIE, '눕다': POSE_LIE, '누움': POSE_LIE,
  'kneel': POSE_KNEEL, 'kneeling': POSE_KNEEL, '무릎꿇다': POSE_KNEEL
};
function normalizePose(v, fallback) {
  if (v == null) return fallback || POSE_STAND;
  var k = String(v).trim().toLowerCase();
  return POSE_ALIAS[k] || POSE_ALIAS[String(v).trim()] || fallback || POSE_STAND;
}

/* ② 문장 → 자세
   - 사역·타동("앉히다/앉혀")은 주체의 자세가 아니므로 제외한다. (깡철이를 의자에 앉힌다)
   - 미수행("앉으려", "앉을 생각")도 제외한다.
   - 한 문장에 자세 전환이 두 번 있으면 "마지막에 취한 자세"가 이긴다.
     ("앉아 있다가 일어선다" → 서다)                                         */
var POSE_RULES = [
  // [정규식, 자세]
  [/앉히|앉혀|앉히는|앉혀서/g,                     null],              // 사역 — 무시 표시
  [/앉으려|앉을\s|앉을지|앉고\s*싶/g,               null],              // 미수행 — 무시 표시
  [/주저앉|걸터앉|고쳐\s*앉|앉아있|앉아\s*있|앉은\s*채|앉아서|앉아|앉은|앉는|착석/g, POSE_SIT],
  [/일어서|일어나|일어선|몸을\s*일으|기립|선\s*채|서\s*있|서서|섰다/g,       POSE_STAND],
  [/무릎을\s*꿇|무릎\s*꿇|꿇어앉/g,                 POSE_KNEEL],
  [/드러눕|누워\s*있|눕는다|누웠다|엎드려/g,         POSE_LIE],
  // 영문
  [/\bseats?\s+(?:him|her|it|them)|\bsits?\s+\w+\s+down\b/gi, null],   // 사역 — 무시
  [/\b(?:sits?|sitting|seated|sat|perch(?:es|ed|ing)?)\b/gi,  POSE_SIT],
  [/\b(?:stands?|standing|stood|gets?\s+up|rises?|rose)\b/gi, POSE_STAND],
  [/\bkneel(?:s|ing)?\b|\bknelt\b/gi,                         POSE_KNEEL],
  [/\b(?:lies?\s+down|lying|lay\s+down|prone)\b/gi,           POSE_LIE]
];

function parsePose(text, fallback) {
  if (!text) return fallback || null;
  var hits = [];                                   // {at, pose}  at = 문장 내 위치
  POSE_RULES.forEach(function (r) {
    var re = new RegExp(r[0].source, r[0].flags), m;
    while ((m = re.exec(text)) !== null) {
      hits.push({ at: m.index, len: m[0].length, pose: r[1] });
      if (m.index === re.lastIndex) re.lastIndex++;  // 빈 매치 무한루프 방지
    }
  });
  if (!hits.length) return fallback || null;
  hits.sort(function (a, b) { return a.at - b.at; });
  // 무시 구간(사역·미수행)과 겹치는 자세 매치는 버린다
  var skip = hits.filter(function (h) { return h.pose === null; });
  var real = hits.filter(function (h) {
    return h.pose !== null && !skip.some(function (s) {
      return h.at >= s.at && h.at < s.at + s.len + 2;
    });
  });
  if (!real.length) return fallback || null;
  return real[real.length - 1].pose;               // 마지막 자세가 이긴다
}

/* ③ 이름으로 절을 좁혀서 판정 — 한 문단에 여러 인물이 있을 때 */
function parsePoseFor(name, text, fallback) {
  if (!name || !text) return parsePose(text, fallback);
  var clauses = String(text).split(/[.。!?\n]|,\s|\u00b7/);   // 구형 브라우저 호환(룩비하인드 미사용)
  var mine = clauses.filter(function (c) { return c.indexOf(name) !== -1; });
  var hit = parsePose(mine.join(' '), null);
  return hit || fallback || null;                  // 그 사람 절에 자세어가 없으면 fallback
}

/* ── 보드 임포트에서 쓰는 법 ───────────────────────────────
   actor를 만들 때 한 줄만 바꾼다.

   [전]  pose: bl.pose || '서다'
   [후]  pose: normalizePose(bl.pose, parsePoseFor(c.name, promptText, '서다'))

   의미 — 씬 JSON에 pose가 있으면 그 값을 표준어로 바꿔 쓰고,
          없으면 프롬프트 본문에서 그 인물의 자세를 읽어내고,
          그것도 없으면 '서다'로 둔다.
   ───────────────────────────────────────────────────────── */

if (typeof module !== 'undefined') module.exports = { normalizePose: normalizePose, parsePose: parsePose, parsePoseFor: parsePoseFor, POSE_ALIAS: POSE_ALIAS };
