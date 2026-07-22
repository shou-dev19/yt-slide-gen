import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { copyCapturedSlides } from './copy_captured_slides.js';

const withTempDirectories = (callback) => {
    const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), 'copy-captured-slides-'));
    const sourceDir = path.join(rootDir, 'out');
    const destinationDir = path.join(rootDir, 'slides');
    fs.mkdirSync(sourceDir);
    fs.mkdirSync(destinationDir);

    try {
        callback({ sourceDir, destinationDir, rootDir });
    } finally {
        fs.rmSync(rootDir, { recursive: true, force: true });
    }
};

test('copies only long slides after removing old destination PNGs', () => {
    withTempDirectories(({ sourceDir, destinationDir }) => {
        fs.writeFileSync(path.join(sourceDir, 'slide_01.png'), 'new long');
        fs.writeFileSync(path.join(sourceDir, 'short_slide_01.png'), 'new short');
        fs.writeFileSync(path.join(destinationDir, 'stale.png'), 'stale');
        fs.writeFileSync(path.join(destinationDir, 'keep.txt'), 'keep');

        const result = copyCapturedSlides({ sourceDir, destinationDir, mode: 'long' });

        assert.deepEqual(result, { copiedCount: 1, removedCount: 1 });
        assert.deepEqual(fs.readdirSync(destinationDir).sort(), ['keep.txt', 'slide_01.png']);
        assert.equal(fs.readFileSync(path.join(destinationDir, 'slide_01.png'), 'utf8'), 'new long');
    });
});

test('copies only short slides', () => {
    withTempDirectories(({ sourceDir, destinationDir }) => {
        fs.writeFileSync(path.join(sourceDir, 'slide_01.png'), 'new long');
        fs.writeFileSync(path.join(sourceDir, 'short_slide_01.png'), 'new short');

        const result = copyCapturedSlides({ sourceDir, destinationDir, mode: 'short' });

        assert.deepEqual(result, { copiedCount: 1, removedCount: 0 });
        assert.deepEqual(fs.readdirSync(destinationDir), ['short_slide_01.png']);
    });
});

test('fails without creating a missing destination directory', () => {
    withTempDirectories(({ sourceDir, rootDir }) => {
        const missingDestinationDir = path.join(rootDir, 'missing', 'slides');
        fs.writeFileSync(path.join(sourceDir, 'slide_01.png'), 'new long');

        assert.throws(
            () => copyCapturedSlides({
                sourceDir,
                destinationDir: missingDestinationDir,
                mode: 'long',
            }),
            /Slide destination directory does not exist/,
        );
        assert.equal(fs.existsSync(missingDestinationDir), false);
    });
});

test('keeps destination PNGs when no source slides exist', () => {
    withTempDirectories(({ sourceDir, destinationDir }) => {
        const existingSlide = path.join(destinationDir, 'existing.png');
        fs.writeFileSync(existingSlide, 'existing');

        assert.throws(
            () => copyCapturedSlides({ sourceDir, destinationDir, mode: 'long' }),
            /No long slide PNGs found/,
        );
        assert.equal(fs.readFileSync(existingSlide, 'utf8'), 'existing');
    });
});
