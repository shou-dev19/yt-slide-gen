import assert from 'node:assert/strict';
import test from 'node:test';
import { findOverThreshold } from './measure_whitespace.js';

test('findOverThreshold: 下端の空きが閾値以上のページだけを返す', () => {
    const results = [
        {
            id: '6-1',
            pages: [
                { label: 'left', whitespaceRatio: 0.4, bottomGapRatio: 0.18 },
                { label: 'right', whitespaceRatio: 0.55, bottomGapRatio: 0.38 },
            ],
        },
        {
            id: '8-4',
            pages: [{ label: 'left', whitespaceRatio: 0.3, bottomGapRatio: 0.1 }],
        },
    ];

    const over = findOverThreshold(results);

    assert.equal(over.length, 1);
    assert.equal(over[0].id, '6-1');
    assert.equal(over[0].label, 'right');
});

test('findOverThreshold: 総余白が大きくても下端が空いていなければ通す（中央寄せレイアウト）', () => {
    // 章扉・CTA のように大きなアイコン1つを縦中央に置くページは、上下に余白が出るため
    // 総余白率は大きくなるが、視覚的には「スカスカ」ではないので不合格にしない。
    const results = [
        { id: '14', pages: [{ label: 'left', whitespaceRatio: 0.79, bottomGapRatio: 0.21 }] },
    ];

    assert.deepEqual(findOverThreshold(results), []);
});

test('findOverThreshold: 閾値は引数で変更できる', () => {
    const results = [
        { id: '12-0', pages: [{ label: 'right', whitespaceRatio: 0.66, bottomGapRatio: 0.29 }] },
    ];

    assert.equal(findOverThreshold(results).length, 0);
    assert.equal(findOverThreshold(results, 0.25).length, 1);
});
