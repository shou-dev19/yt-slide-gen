import path from 'path';
import fs from 'fs';
import os from 'os';

// Resolve the Chromium executable for Puppeteer, in priority order:
//   1. PUPPETEER_EXECUTABLE_PATH (explicit override)
//   2. chrome-headless-shell from the Puppeteer cache (the Debian-packaged
//      Chromium crashes on launch in some container environments, so the
//      official headless shell is preferred over system browsers)
//   3. System-installed Chromium/Chrome (needed on ARM64 Linux containers
//      where Puppeteer's bundled x64 Chromium fails via Rosetta)
//   4. undefined → Puppeteer's bundled browser
//
// Install the headless shell once with:
//   npx puppeteer browsers install chrome-headless-shell
export function resolveBrowserExecutable() {
    if (process.env.PUPPETEER_EXECUTABLE_PATH) {
        return process.env.PUPPETEER_EXECUTABLE_PATH;
    }

    const headlessShell = findChromeHeadlessShell();
    if (headlessShell) {
        return headlessShell;
    }

    const systemChromiumCandidates = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
    ];
    return systemChromiumCandidates.find((p) => fs.existsSync(p));
}

function findChromeHeadlessShell() {
    const cacheDir = path.join(
        process.env.PUPPETEER_CACHE_DIR || path.join(os.homedir(), '.cache', 'puppeteer'),
        'chrome-headless-shell'
    );
    if (!fs.existsSync(cacheDir)) return undefined;

    const versions = fs
        .readdirSync(cacheDir)
        .sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));

    for (const version of versions) {
        const versionDir = path.join(cacheDir, version);
        let platformDirs;
        try {
            platformDirs = fs
                .readdirSync(versionDir)
                .filter((d) => d.startsWith('chrome-headless-shell'));
        } catch {
            continue;
        }
        for (const platformDir of platformDirs) {
            for (const bin of ['chrome-headless-shell', 'chrome-headless-shell.exe']) {
                const executable = path.join(versionDir, platformDir, bin);
                if (fs.existsSync(executable)) return executable;
            }
        }
    }
    return undefined;
}
