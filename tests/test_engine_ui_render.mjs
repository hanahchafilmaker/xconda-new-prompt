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
const pos = d.querySelector('.panel-pos');
check('컷 패널에 첫 프레임 위치가 적힌다', !!pos && pos.textContent.includes('첫 프레임 공간'), pos ? pos.textContent : '없음');
check('패널 위치가 가구를 자리로 말하지 않는다', !!pos && !/보조대|사물함|책장/.test(pos.textContent), pos ? pos.textContent : '없음');

check('등장인물/레퍼런스 목록이 채워진다', d.getElementById('castList').children.length > 0, '비어 있음');

const blocks = d.getElementById('promptBody').children.length;
check('프롬프트 10블록이 나온다', blocks === 10, `${blocks}블록`);
const areas = d.getElementById('promptBody').querySelectorAll('textarea');
check('편집용 textarea가 생긴다', areas.length >= 20, `${areas.length}개`);
check('한국어와 영문 textarea가 나란히 생긴다',
  d.querySelectorAll('#promptBody textarea[data-k="ko"]').length > 0 && d.querySelectorAll('#promptBody textarea[data-k="en"]').length > 0,
  '한쪽 언어 입력창이 없음');
check('Claude HTML과 JSON을 모두 받는다', d.getElementById('fileInput').accept.includes('.html') && d.getElementById('fileInput').accept.includes('.json'), d.getElementById('fileInput').accept);
check('수정본 HTML 저장 버튼이 있다', d.getElementById('saveHtmlBtn') !== null, '저장 버튼 없음');
check('Claude 재요청 버튼이 없다', !d.querySelector('.bar').textContent.includes('Claude'), d.querySelector('.bar').textContent.trim());
const blk02 = d.getElementById('promptBody').children[1];
check('02·08 블록은 펴져 있다', !!blk02 && !blk02.classList.contains('fold'), blk02 ? 'fold 걸림' : '02블록 자체가 없음');

const cnt = d.getElementById('cnt').textContent;
check('하단 글자 수가 계산된다', /한글 [\d,]+자/.test(cnt), cnt);
check('검수 결과가 나온다', d.getElementById('audit').textContent.trim().length > 0, '빈 검수창');
const en = dom.window.assembleEn();
check('씨댄스 복사본에 right behind 가 없다', !en.includes('right behind'), 'right behind 잔존');
check('씨댄스 복사본이 패널과 같은 앞뒤를 말한다', en.includes('frame-center in the foreground') && en.includes('stacked in depth on the same center axis'), en.slice(0, 180));
check('right behind 를 복사 전에 고친다', !dom.window.seedanceSafe('sitting right behind').includes('right behind') && dom.window.seedanceSafe('at frame-right').includes('frame-right'));

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

// Claude가 만든 기존 HTML을 다시 읽고, 브라우저 안에서 직접 한/영을 수정할 수 있어야 한다.
const extracted = dom.window.extractEmbeddedScene(html);
check('HTML의 EMBEDDED_SCENE을 다시 읽는다', extracted.schema === 'xconda-scene-v1' && extracted.parts.length === 5, extracted.schema);
const enArea = d.querySelector('#promptBody textarea[data-k="en"]');
if (enArea) {
  enArea.value += '\nDIRECT EN EDIT TEST';
  enArea.dispatchEvent(new dom.window.Event('input', { bubbles: true }));
  check('영문 직접 수정이 씨댄스 복사본에 즉시 반영된다', dom.window.assembleEn().includes('DIRECT EN EDIT TEST'), '수정 문구가 없음');
  check('직접 수정하면 저장 상태가 수정됨으로 바뀐다', d.getElementById('saveState').classList.contains('dirty'), d.getElementById('saveState').textContent);
} else {
  check('영문 직접 수정이 씨댄스 복사본에 즉시 반영된다', false, '영문 textarea 없음');
}

const lockRefs = d.getElementById('lockRef').options.length;
check('위치 락 도구에 현재 파트 레퍼런스가 채워진다', lockRefs > 0, `${lockRefs}개`);
check('위치 락 영문 미리보기에 실제 인물명이 나온다', /POSITION LOCK.+(Hyunwoo|Baksu)/.test(d.getElementById('lockPreview').textContent), d.getElementById('lockPreview').textContent.slice(0, 180));
d.getElementById('lockHorizontal').value = 'right';
dom.window.addPositionLock();
check('위치 락이 한국어와 영문에 동시에 들어간다', dom.window.assembleKo().includes('위치 고정 —') && dom.window.assembleEn().includes('POSITION LOCK —'), '한쪽 락이 없음');
const firstLockTag = d.getElementById('lockRef').options[d.getElementById('lockRef').selectedIndex].textContent.split(' · ')[0];
d.getElementById('lockHorizontal').value = 'left';
dom.window.addPositionLock();
const lockLines = dom.window.assembleEn().split('\n').filter((line) => line.includes(`POSITION LOCK — ${firstLockTag}`));
check('같은 레퍼런스 위치 락은 중복 대신 교체된다', lockLines.length === 1 && lockLines[0].includes('frame-left') && !lockLines[0].includes('frame-right'), lockLines.join(' | '));

const savedHtml = dom.window.editedHtmlSource();
const reopened = dom.window.extractEmbeddedScene(savedHtml);
check('수정본 HTML에 편집한 씬이 다시 심긴다', reopened.schema === 'xconda-scene-v1' && JSON.stringify(reopened).includes('POSITION LOCK'), '저장 HTML에 수정 내용 없음');

console.log(failed ? `\n실패 ${failed}건` : '\nUI 스모크 통과 — HTML 불러오기·한영 직접 편집·위치 락·재저장까지 렌더됨');
process.exit(failed ? 1 : 0);
