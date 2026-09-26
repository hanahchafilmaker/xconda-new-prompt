/* 편집기 UI가 실제로 "보이는지" 확인하는 스모크 테스트.
 * tests/test_engine_room_compat.mjs 가 좌표 환산 **함수**만 떼어서 검사한다면,
 * 이 테스트는 index.html(씬이 심긴 편집기)을 jsdom에서 **실제로 실행**해서
 * 화면에 탭·컷 패널·등장인물 목록·10블록 프롬프트가 그려지는지를 본다.
 *
 * 실행: make test-ui   (jsdom 필요 — make setup-web)
 * jsdom이 없으면 실패가 아니라 "건너뜀"으로 끝난다 (오프라인 환경 대비).
 */
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

let JSDOM;
try {
  ({ JSDOM } = await import('jsdom'));
} catch {
  console.log('skip  jsdom이 설치돼 있지 않다 — `make setup-web` 후 다시 실행');
  process.exit(0);
}

const EDITOR = join(ROOT, 'index.html');
if (!existsSync(EDITOR)) {
  console.error('FAIL: index.html이 없다 — `make engine-html` 를 먼저 실행');
  process.exit(1);
}

const html = readFileSync(EDITOR, 'utf8');
const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true });
const d = dom.window.document;

let failed = 0;
function check(label, cond, detail) {
  console.log(`${cond ? 'ok  ' : 'FAIL'}  ${label}${cond ? '' : ` → ${detail}`}`);
  if (!cond) failed++;
}

// loadScene()이 동기 실행이라 파싱 직후에 이미 UI가 그려져 있다.
await new Promise((r) => dom.window.setTimeout(r, 50));

check('EMBEDDED_SCENE가 심겨 있다', /const EMBEDDED_SCENE = \{\s*"schema": "xconda-scene-v1"/.test(html), '빈 {}이면 빌드 안 된 파일');
check('씬이 로드되면 드롭존이 숨는다', d.getElementById('drop').style.display === 'none', `"${d.getElementById('drop').style.display}"`);
check('무대가 켜진다 (stage.on)', d.getElementById('stage').classList.contains('on'), d.getElementById('stage').className);
check('헤더에 씬 이름이 찍힌다', d.getElementById('hSlug').textContent.includes('S8'), d.getElementById('hSlug').textContent);

const tabs = d.getElementById('tabs').children.length;
check('파트 탭 5개(A~E)', tabs === 5, `${tabs}개`);
check('탭 하나가 선택 상태다', d.getElementById('tabs').querySelector('.tab.on') !== null, '선택 없음');

const svgs = d.getElementById('panelGrid').querySelectorAll('svg').length;
check('컷별 패널 SVG가 그려진다', svgs > 0, `${svgs}개`);
check('패널 안에 인물 글리프(원)가 있다', d.getElementById('panelGrid').querySelectorAll('circle').length > 0, '원 0개');

check('등장인물/레퍼런스 목록이 채워진다', d.getElementById('castList').children.length > 0, '비어 있음');

const blocks = d.getElementById('promptBody').children.length;
check('프롬프트 10블록이 나온다', blocks === 10, `${blocks}블록`);
const areas = d.getElementById('promptBody').querySelectorAll('textarea');
check('편집용 textarea가 생긴다', areas.length >= 10, `${areas.length}개`);
const blk02 = d.getElementById('promptBody').children[1];
check('02·08 블록은 펴져 있다', !!blk02 && !blk02.classList.contains('fold'), blk02 ? 'fold 걸림' : '02블록 자체가 없음');

const cnt = d.getElementById('cnt').textContent;
check('하단 글자 수가 계산된다', /한글 [\d,]+자/.test(cnt), cnt);
check('검수 결과가 나온다', d.getElementById('audit').textContent.trim().length > 0, '빈 검수창');

// 파트를 실제로 클릭해서 갈아타지는지도 본다 (이벤트 핸들러가 살아 있는지).
const tab3 = d.getElementById('tabs').children[2];
if (!tab3) {
  check('탭 클릭으로 파트가 바뀐다', false, '탭이 없어서 클릭조차 못 함');
} else {
  tab3.click();
  await new Promise((r) => dom.window.setTimeout(r, 20));
  check('탭 클릭으로 파트가 바뀐다', /파트 C$/.test(d.getElementById('cnt').textContent), d.getElementById('cnt').textContent);
  check('파트를 바꾸면 패널이 다시 그려진다', d.getElementById('panelGrid').querySelectorAll('svg').length > 0, 'SVG 0개');
}

console.log(failed ? `\n실패 ${failed}건` : '\nUI 스모크 통과 — 웹에서 보이는 요소 전부 렌더됨');
process.exit(failed ? 1 : 0);
