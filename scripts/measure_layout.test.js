import assert from 'node:assert/strict';
import test from 'node:test';
import { findIllustrationDominant, collectOverflow } from './measure_layout.js';

const page = (over = {}) => ({
    label: 'left',
    illustrationCount: 1,
    illustrationImages: [{ src: 'pose_atama_kakaeru_woman.png', widthRatio: 0.3, heightPx: 300 }],
    illustrationAreaRatio: 0.1,
    textAreaRatio: 0.4,
    headlineFontSize: 60,
    headlineText: '見出し',
    illustrationVsHeadline: 1.2,
    ...over,
});

test('findIllustrationDominant: ページの大半がイラストなら不合格', () => {
    const results = [{ id: 'C', pages: [page({ illustrationAreaRatio: 0.73, textAreaRatio: 0.12 })] }];

    const over = findIllustrationDominant(results);

    assert.equal(over.length, 1);
    assert.equal(over[0].id, 'C');
    assert.ok(over[0].reasons.includes('ページの大半がイラスト'));
});

test('findIllustrationDominant: 面積が小さくてもテキストより大きければ主役化として不合格', () => {
    const results = [{ id: 'D', pages: [page({ illustrationAreaRatio: 0.2, textAreaRatio: 0.05 })] }];

    const over = findIllustrationDominant(results);

    assert.equal(over.length, 1);
    assert.deepEqual(over[0].reasons, ['テキストよりイラストが大きい']);
});

test('findIllustrationDominant: 見出し矩形との比が1を超えても、テキストが主役なら合格', () => {
    // いらすとやの PNG は透明余白を含むため bbox が実際の絵より大きく出る。見出し比で
    // 判定すると目視で問題のない導入スライド（実測 1.06〜1.67）が落ちるので、判定に使わない。
    const results = [
        { id: '1', pages: [page({ illustrationAreaRatio: 0.129, textAreaRatio: 0.442, illustrationVsHeadline: 1.67 })] },
    ];

    assert.deepEqual(findIllustrationDominant(results), []);
});

test('findIllustrationDominant: いらすとやが無いページは対象外', () => {
    const results = [
        { id: '9', pages: [page({ illustrationCount: 0, illustrationImages: [], illustrationAreaRatio: 0, textAreaRatio: 0 })] },
    ];

    assert.deepEqual(findIllustrationDominant(results), []);
});

test('findIllustrationDominant: 閾値は引数で変更できる', () => {
    const results = [{ id: '6-2', pages: [page({ illustrationAreaRatio: 0.3, textAreaRatio: 0.41 })] }];

    assert.deepEqual(findIllustrationDominant(results), []);
    assert.equal(findIllustrationDominant(results, { areaRatio: 0.25 }).length, 1);
});

test('collectOverflow: スライドIDを付けて見切れ・はみ出しを集約する', () => {
    const results = [
        {
            id: 'A',
            clipped: [{ label: 'left', path: 'div.lead', text: '長い本文', clippedXPx: 0, clippedYPx: 599 }],
            outOfBounds: [],
        },
        {
            id: 'B',
            clipped: [],
            outOfBounds: [{ label: 'left', path: 'div.lead', text: '字幕帯に侵入', overflowPx: { bottom: 190 } }],
        },
    ];

    const { clipped, outOfBounds } = collectOverflow(results);

    assert.deepEqual(clipped.map((c) => c.id), ['A']);
    assert.deepEqual(outOfBounds.map((o) => o.id), ['B']);
    assert.equal(outOfBounds[0].overflowPx.bottom, 190);
});
