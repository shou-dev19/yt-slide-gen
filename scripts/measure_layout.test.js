import assert from 'node:assert/strict';
import test from 'node:test';
import {
    measureShortSpread,
    findIllustrationDominant,
    collectOverflow,
    collectBrokenIcons,
    collectShortSpreadViolations,
} from './measure_layout.js';

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

test('collectBrokenIcons: スライドIDを付けて未定義アイコンを集約する', () => {
    // 実例: fa-gauge-simple-low は Pro 限定で、6.5.0 Free には定義が無い。
    const results = [
        {
            id: '4-1',
            brokenIcons: [
                {
                    label: 'left',
                    path: 'div.page-body > div.emph > i',
                    classes: 'fa-solid fa-gauge-simple-low',
                    iconClasses: ['fa-gauge-simple-low'],
                },
            ],
        },
        { id: '4-2', brokenIcons: [] },
    ];

    const broken = collectBrokenIcons(results);

    assert.equal(broken.length, 1);
    assert.equal(broken[0].id, '4-1');
    assert.deepEqual(broken[0].iconClasses, ['fa-gauge-simple-low']);
});

test('collectBrokenIcons: brokenIcons を持たない結果でも落ちない', () => {
    // 旧フォーマットのレポートを読み込んだ場合や、計測が null を返した場合の後方互換。
    assert.deepEqual(collectBrokenIcons([{ id: '1' }]), []);
});

const shortSlide = ({
    pageCount = 0,
    hasLeft = false,
    hasRight = false,
    ownClasses = [],
    descendantClasses = [],
} = {}) => ({
    classList: {
        contains: (className) => ownClasses.includes(className),
    },
    querySelectorAll: (selector) => selector === '.page' ? Array.from({ length: pageCount }, () => ({})) : [],
    querySelector: (selector) => {
        if (selector === '.page.left') return hasLeft ? {} : null;
        if (selector === '.page.right') return hasRight ? {} : null;
        return descendantClasses.includes(selector.slice(1)) ? {} : null;
    },
});

const fakePage = (slides) => ({
    evaluate: async (measure, slideSelector, index) => {
        const previousDocument = globalThis.document;
        globalThis.document = {
            querySelectorAll: (selector) => selector === slideSelector ? slides : [],
        };
        try {
            return measure(slideSelector, index);
        } finally {
            globalThis.document = previousDocument;
        }
    },
});

test('measureShortSpread: .page が2つ以上あれば見開き構造として検出する', async () => {
    const result = await measureShortSpread(fakePage([shortSlide({ pageCount: 2 })]), '.slide-container', 0);

    assert.deepEqual(result.reasons, ['見開き構造']);
    assert.equal(result.evidence.pageCount, 2);
    assert.equal(result.evidence.hasLeftAndRight, false);
});

test('measureShortSpread: .page.left と .page.right が揃っていれば見開き構造として検出する', async () => {
    const result = await measureShortSpread(
        fakePage([shortSlide({ pageCount: 1, hasLeft: true, hasRight: true })]),
        '.slide-container',
        0,
    );

    assert.deepEqual(result.reasons, ['見開き構造']);
    assert.equal(result.evidence.hasLeftAndRight, true);
});

test('measureShortSpread: 自身と子孫の spread-base 由来クラスを図鑑装丁として検出する', async () => {
    const result = await measureShortSpread(
        fakePage([
            shortSlide({
                ownClasses: ['short-spread'],
                descendantClasses: ['paper-slide', 'paper-grain'],
            }),
        ]),
        '.slide-container',
        0,
    );

    assert.deepEqual(result.reasons, ['図鑑装丁クラス']);
    assert.deepEqual(result.evidence.classes, ['short-spread', 'paper-slide', 'paper-grain']);
});

test('measureShortSpread: 単ページで図鑑装丁クラスがなければ検出しない', async () => {
    const result = await measureShortSpread(fakePage([shortSlide()]), '.slide-container', 0);

    assert.deepEqual(result, {
        reasons: [],
        evidence: {
            pageCount: 0,
            hasLeftAndRight: false,
            classes: [],
        },
    });
});

test('collectShortSpreadViolations: スライドIDを付けて違反だけを集約する', () => {
    const results = [
        {
            id: '2',
            shortSpread: {
                reasons: ['見開き構造', '図鑑装丁クラス'],
                evidence: {
                    pageCount: 2,
                    hasLeftAndRight: true,
                    classes: ['paper-slide'],
                },
            },
        },
        {
            id: '3',
            shortSpread: {
                reasons: [],
                evidence: {
                    pageCount: 0,
                    hasLeftAndRight: false,
                    classes: [],
                },
            },
        },
        { id: '4' },
    ];

    const violations = collectShortSpreadViolations(results);

    assert.equal(violations.length, 1);
    assert.equal(violations[0].id, '2');
    assert.deepEqual(violations[0].reasons, ['見開き構造', '図鑑装丁クラス']);
    assert.deepEqual(violations[0].evidence.classes, ['paper-slide']);
});
