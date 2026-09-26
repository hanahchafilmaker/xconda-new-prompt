/* 글콘티 작업실(storyboard.html) UI 및 기능 스모크 테스트 (jsdom)
 * 실행: node tests/test_storyboard_ui.mjs
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

const STORYBOARD = join(ROOT, 'storyboard.html');
if (!existsSync(STORYBOARD)) {
  console.error('FAIL: storyboard.html 파일이 없습니다');
  process.exit(1);
}

const html = readFileSync(STORYBOARD, 'utf8');
const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true });
const d = dom.window.document;
const w = dom.window;

let failed = 0;
function check(label, cond, detail) {
  console.log(`${cond ? 'ok  ' : 'FAIL'}  ${label}${cond ? '' : ` → ${detail}`}`);
  if (!cond) failed++;
}

// DOMContentLoaded 대기
await new Promise(r => setTimeout(r, 60));

check('storyboard.html 헤더가 렌더링된다', d.querySelector('.g-brand') !== null);
check('사이드바 저장소 목록이 생성된다', d.getElementById('storyList').children.length >= 3, `${d.getElementById('storyList').children.length}개`);
check('기본 씬 번호가 채워진다', d.getElementById('metaSceneId').value.includes('S#8'), d.getElementById('metaSceneId').value);
check('기본 컷 카드가 5개 렌더링된다', d.querySelectorAll('.cut-card').length === 5, `${d.querySelectorAll('.cut-card').length}개`);
check('총 러닝타임 계산된다', d.getElementById('runtimeSummary').textContent.includes('18.0s'), d.getElementById('runtimeSummary').textContent);

// 새 컷 추가 테스트
const curLen = d.querySelectorAll('.cut-card').length;
w.addCutCard();
await new Promise(r => setTimeout(r, 20));
check('addCutCard() 실행 후 컷이 추가된다', d.querySelectorAll('.cut-card').length === curLen + 1, `${d.querySelectorAll('.cut-card').length}개`);

// scene-v1 생성기 검증
const curStory = w.getCur();
const sceneV1 = w.buildXcondaSceneV1(curStory);
check('XCONDA 씬 JSON 스키마가 일치한다', sceneV1.schema === 'xconda-scene-v1', sceneV1.schema);
check('파트 A와 10블록 프롬프트가 생성된다', (sceneV1.parts[0].prompt.blocks || []).length === 10, `${(sceneV1.parts[0].prompt.blocks || []).length}블록`);
check('컷 데이터가 정상 변환된다', (sceneV1.parts[0].prompt.cuts || []).length > 0, '컷 0개');

// 스마트 파서 테스트
const testScript = `S#99 테스트 씬
장소: 비밀 기지
등장인물: 요원A, 요원B

CUT 99-1 [0-4초] 풀 샷 84° 돌리 인
요원A가 문을 박차고 들어선다.
대사 — 요원A: {아무도 움직이지 마!}

CUT 99-2 [4-8초] 클로즈업 34° 고정
요원B가 천천히 손을 든다.
대사 — 요원B: {예상보다 빨랐군.}`;

d.getElementById('rawScriptText').value = testScript;
w.parseRawScriptToCards();
await new Promise(r => setTimeout(r, 20));

check('스마트 파서로 씬 번호가 파싱된다', d.getElementById('metaSceneId').value.includes('S#99'), d.getElementById('metaSceneId').value);
check('스마트 파서로 2개 컷이 생성된다', d.querySelectorAll('.cut-card').length === 2, `${d.querySelectorAll('.cut-card').length}개`);
check('대사가 정상 파싱된다', d.querySelector('.cut-dlg-text').value.includes('움직이지 마'), d.querySelector('.cut-dlg-text').value);

console.log(failed ? `\n실패 ${failed}건` : '\n글콘티 스튜디오(storyboard.html) 테스트 전체 통과');
process.exit(failed ? 1 : 0);
