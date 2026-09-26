/* XCONDA 편집기(assets/xconda_engine.html)의 room 호환 블록 회귀 테스트.
 * HTML에서 __ROOM_COMPAT_START__ ~ __ROOM_COMPAT_END__ 사이의 실제 소스를 뽑아 실행한다
 * (별도 사본을 돌리는 게 아니라, 편집기에 실제로 실려 있는 그 코드를 그대로 실행한다).
 * 실행: node tests/test_engine_room_compat.mjs   또는  make test-js
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const ENGINE = join(ROOT, 'xconda-new-prompt', 'assets', 'xconda_engine.html');
const FIXTURE = join(ROOT, 'tests', 'fixtures', 'scene_v1_sample.json');
const LEGACY = join(ROOT, 'tests', 'fixtures', 'scene_legacy_sample.json');

const html = readFileSync(ENGINE, 'utf8');
const m = html.match(/\/\* __ROOM_COMPAT_START__[\s\S]*?__ROOM_COMPAT_END__ \*\//);
if (!m) { console.error('FAIL: engine에서 ROOM_COMPAT 블록을 찾지 못했다'); process.exit(1); }
const normalizeRoom = new Function(`${m[0]}\nreturn normalizeRoom;`)();

let failed = 0;
function eq(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log(`${ok ? 'ok  ' : 'FAIL'}  ${label}${ok ? '' : ` → got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`}`);
  if (!ok) failed++;
}

// 1) loadScene이 실제로 이 함수를 호출하는가
eq('loadScene이 normalizeRoom을 호출한다', /function loadScene\(data\)\{[\s\S]{0,200}?normalizeRoom\(data\);/.test(html), true);

// 2) 미터 room → px (assets/scene_compat.py 와 같은 값)
const scene = JSON.parse(readFileSync(FIXTURE, 'utf8'));
normalizeRoom(scene);
eq('centerPx', scene.room.centerPx, [0, 0]);
eq('widthPx (8m)', scene.room.widthPx, 320);
eq('depthPx (6m)', scene.room.depthPx, 240);
eq('items 개수', scene.room.items.length, 2);
const desk = scene.room.items.find(i => i.name === '공동 데스크');
eq('데스크 px(x,y,w,h)', [desk.x, desk.y, desk.w, desk.h], [-40, -40, 64, 32]);
eq('portals는 items에 없다', scene.room.items.some(i => i.id === 'door_e'), false);

// 3) panelGeom이 이 px 필드로 실제 패널 좌표를 만드는가 (엔진 코드 그대로)
const geomSrc = html.match(/function panelGeom\(\)\{[\s\S]*?\n\}/)[0];
const SCENE = scene;
const panelGeom = new Function(`const SCENE=${JSON.stringify(SCENE)};${geomSrc}\nreturn panelGeom;`)();
const g = panelGeom();
eq('패널 스케일이 유한한 값이다', Number.isFinite(g.sc) && g.sc > 0, true);
eq('방 원점이 패널 안에 그려진다', g.TX(0) > 0 && g.TX(0) < g.W && g.TY(0) > 0 && g.TY(0) < g.Hc, true);

// 4) 예전 px room은 무변환 통과
const legacy = JSON.parse(readFileSync(LEGACY, 'utf8'));
normalizeRoom(legacy);
eq('레거시 centerPx 유지', legacy.room.centerPx, [320, 240]);
eq('레거시 items 유지', legacy.room.items.length, 1);
eq('레거시에 표식 안 남는다', legacy.room._itemsFrom === undefined, true);

// 5) [프롬프트 복사]가 블록 머리("01 SCENE CONTEXT")를 붙여 조립하는가
//    — examples/template_10block_prompt.txt 가 약속한 형식. v9.13 이전에 이게 빠져 있었다.
const assembleSrc = html.match(/function assemble\(p,L\)\{[\s\S]*?\n\}/)[0];
const assemble = new Function(`${assembleSrc}\nreturn assemble;`)();
const enPrompt = assemble(scene.parts[0], 'en');
eq('영문 프롬프트에 01 블록 머리', enPrompt.startsWith('01 SCENE CONTEXT\n'), true);
eq('블록 머리가 순서대로 들어간다',
  ['01 SCENE CONTEXT', '02 ACTIVE REFERENCES', '08 ACTION TIMELINE', '10 POSITIVE LOCKS']
    .map(h => enPrompt.indexOf(h)).every((v, i, a) => v >= 0 && (i === 0 || v > a[i - 1])), true);
eq('08번 아래에 컷 본문이 붙는다', /08 ACTION TIMELINE\n\[ACTION TIMELINE\][\s\S]*?0-8s — CUT99-1/.test(enPrompt), true);

console.log(failed ? `\n${failed}건 실패` : '\n통과 — 편집기 room 호환 블록 정상');
process.exit(failed ? 1 : 0);
