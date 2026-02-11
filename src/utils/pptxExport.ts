import pptxgen from "pptxgenjs";

interface SlideData {
  id: number;
  content: string;
  speaker: string;
  expression: string;
  script: string;
}

const PRIMARY_COLOR = "E6007F";
const TEXT_DARK = "1A237E";

export const exportToPptx = async (slides: SlideData[]) => {
  console.log('Starting PPTX export for', slides.length, 'slides...');
  
  try {
    const pptx = new pptxgen();
    
    // Correct layout name is "LAYOUT_16x9" (with an 'x')
    // Alternatively, define a custom layout to be absolutely safe
    try {
        pptx.layout = "LAYOUT_16x9";
    } catch (e) {
        console.warn("Standard LAYOUT_16x9 failed, defining custom 16:9 layout");
        pptx.defineLayout({ name: 'CUSTOM_169', width: 13.33, height: 7.5 });
        pptx.layout = 'CUSTOM_169';
    }

    for (const slide of slides) {
      const pptxSlide = pptx.addSlide();
      const content = slide.content;
      const lines = content.split('\n').map(l => l.trim()).filter(l => l);

      // Default Background & Border
      pptxSlide.background = { color: "FFFFFF" };
      pptxSlide.addShape(pptx.ShapeType.rect, {
          x: 0, y: 0, w: "100%", h: "100%",
          line: { color: PRIMARY_COLOR, width: 10 }
      });

      // Chapter Slide
      if (content.includes('章タイトル') || content.includes('Chapter')) {
        pptxSlide.addShape(pptx.ShapeType.rect, {
            x: 0, y: 0, w: "100%", h: "100%",
            fill: { color: PRIMARY_COLOR }
        });

        const chapterLine = lines.find(l => l.includes('Chapter') || l.includes('章タイトル')) || '';
        const title = chapterLine.replace(/章タイトル：|Chapter \d+/, '').trim();
        const chapterNumMatch = chapterLine.match(/Chapter (\d+)/);

        pptxSlide.addText(chapterNumMatch ? `Chapter ${chapterNumMatch[1]}` : 'Chapter', {
          x: 0, y: "30%", w: "100%", align: "center",
          fontSize: 48, color: "FFD700", bold: true
        });
        pptxSlide.addText(title, {
          x: 0, y: "45%", w: "100%", align: "center",
          fontSize: 60, color: "FFFFFF", bold: true
        });
        continue;
      }

      // Image-only Slide Detection
      const commonImages: Record<string, string> = {
          '評価項目について': '/slides/common/評価項目について.png',
          '評価ランクの基準について': '/slides/common/評価ランクの基準について.png',
          '評価は独断と偏見': '/slides/common/評価は独断と偏見.png',
          'プランやキャンペーンは投稿時点': '/slides/common/プランやキャンペーンは投稿時点のもの注意喚起.png',
          'ブログもやってます': '/slides/common/ブログもやってます.png',
          'チャンネル登録と高評価': '/slides/common/チャンネル登録と高評価よろしくお願いします.png'
      };

      let matchedImage = '';
      for (const [key, path] of Object.entries(commonImages)) {
          if (content.includes(key)) {
              matchedImage = path;
              break;
          }
      }

      if (matchedImage) {
          pptxSlide.addImage({ path: window.location.origin + matchedImage, x: 0, y: 0, w: "100%", h: "100%" });
          continue;
      }

      // Chart detection
      if (content.includes('レーダーチャート') || content.includes('成績表')) {
          let chartPath = '';
          if (content.includes('HISモバイル')) chartPath = '/slides/charts/HISモバイル.png';
          else if (content.includes('日本通信')) chartPath = '/slides/charts/日本通信SIM.png';
          else if (content.includes('IIJmio')) chartPath = '/slides/charts/IIJmio.png';
          else if (content.includes('LINEMO')) chartPath = '/slides/charts/LINEMO.png';

          if (chartPath) {
              pptxSlide.addImage({ path: window.location.origin + chartPath, x: "10%", y: "10%", w: "80%", h: "80%" });
              continue;
          }
      }

      // Standard Content Rendering
      let currentY = 15;

      lines.forEach((line) => {
        if (line.startsWith('タイトルロゴ：')) {
          const val = line.replace('タイトルロゴ：', '');
          pptxSlide.addText(val, {
            x: 0, y: "40%", w: "100%", align: "center",
            fontSize: 44, color: TEXT_DARK, bold: true
          });
        } 
        else if (line.startsWith('テキスト：') || line.startsWith('テキスト一覧：') || line.startsWith('リスト表示')) {
          const text = line.replace(/テキスト：|テキスト一覧：|リスト表示/, '').trim();
          pptxSlide.addText(text, {
            x: "10%", y: `${currentY}%`, w: "80%", align: "center",
            fontSize: 32, color: TEXT_DARK
          });
          currentY += 12;
        } 
        else if (line.startsWith('イラスト：') || line.startsWith('画像：') || line.startsWith('背景：') || line.startsWith('テロップ：')) {
          const prompt = line.split('：')[1] || line;
          pptxSlide.addText(`[PLACEHOLDER] ${prompt}`, {
            x: "10%", y: "75%", w: "80%", h: "15%", align: "center",
            fontSize: 18, color: "666666", fill: { color: "F8F8F8" }, line: { color: "CCCCCC", width: 1 }
          });
        }
        else {
          pptxSlide.addText(line, {
            x: "10%", y: `${currentY}%`, w: "80%", align: "center",
            fontSize: 32, color: TEXT_DARK
          });
          currentY += 10;
        }
      });
    }

    console.log('Finalizing PPTX file...');
    await pptx.writeFile({ fileName: `HISモバイル_解説スライド_${new Date().getTime()}.pptx` });
    console.log('PPTX export completed successfully.');
  } catch (error) {
    console.error('PPTX Export Error:', error);
    alert('PPTXの書き出し中にエラーが発生しました。\n' + (error instanceof Error ? error.message : String(error)));
  }
};
