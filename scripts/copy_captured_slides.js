import fs from 'fs';
import path from 'path';

const isPngForMode = (filename, mode) => {
    const prefix = mode === 'short' ? 'short_slide_' : 'slide_';
    return filename.startsWith(prefix) && filename.endsWith('.png');
};

const assertExistingDirectory = (directoryPath) => {
    if (!fs.existsSync(directoryPath) || !fs.statSync(directoryPath).isDirectory()) {
        throw new Error(`Slide destination directory does not exist: ${directoryPath}`);
    }
};

export const copyCapturedSlides = ({ sourceDir, destinationDir, mode }) => {
    const sourceFiles = fs.readdirSync(sourceDir, { withFileTypes: true })
        .filter((entry) => entry.isFile() && isPngForMode(entry.name, mode))
        .map((entry) => entry.name);

    if (sourceFiles.length === 0) {
        throw new Error(`No ${mode} slide PNGs found in ${sourceDir}`);
    }

    assertExistingDirectory(destinationDir);

    const oldPngFiles = fs.readdirSync(destinationDir, { withFileTypes: true })
        .filter((entry) => entry.isFile() && entry.name.endsWith('.png'))
        .map((entry) => entry.name);

    for (const filename of oldPngFiles) {
        fs.unlinkSync(path.join(destinationDir, filename));
    }

    for (const filename of sourceFiles) {
        fs.copyFileSync(
            path.join(sourceDir, filename),
            path.join(destinationDir, filename),
        );
    }

    return { copiedCount: sourceFiles.length, removedCount: oldPngFiles.length };
};
