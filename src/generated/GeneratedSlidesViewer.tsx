import React from 'react';

// --- CSS Styles ---
const cssStyles = `
  @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@800;900&display=swap');
  @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

  :root {
    --primary-color: #E6007F; /* HIS Mobile Pink */
    --secondary-color: #3366CC;
    --accent-yellow: #ffca28;
    --accent-red: #ff3d00;
    --text-dark: #1a237e;
    --bg-white: #ffffff;
  }
  
  * { box-sizing: border-box; }
  
  .slide-viewer-container {
    background: #333;
    padding: 50px;
    display: flex;
    flex-direction: column;
    gap: 50px;
    align-items: center;
    min-height: 100vh;
  }

  .slide-container {
    width: 1280px;
    height: 720px;
    background: var(--bg-white);
    border: 10px solid var(--primary-color);
    padding: 40px;
    font-family: 'M PLUS Rounded 1c', sans-serif;
    color: var(--text-dark);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
    overflow: hidden;
    flex-shrink: 0;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
  }

  h1 { font-size: 100px; font-weight: 900; margin: 0; line-height: 1.1; text-shadow: 3px 3px 0 white, 6px 6px 0 var(--primary-color); text-align: center; }
  h2 { font-size: 80px; font-weight: 800; margin: 0 0 30px 0; border-bottom: 8px solid var(--accent-yellow); display: inline-block; padding-bottom: 10px; text-align: center; }
  p, li { font-size: 54px; font-weight: 800; line-height: 1.4; margin: 20px 0; }
  ul { list-style: none; padding: 0; }
  li::before { content: '✅'; margin-right: 20px; }
  strong, .highlight { color: var(--accent-red); }
  .accent-text { color: var(--primary-color); }

  .text-large p, .text-large li { font-size: 70px; }
  .image-only-slide { border: none !important; padding: 0 !important; background: transparent !important; }
  .image-only-slide img { width: 100%; height: 100%; object-fit: cover; }

  .img-placeholder {
    background-color: #ffeb3b;
    border: 5px dashed #f57f17;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #333;
    font-size: 30px;
    margin: 20px;
    text-align: center;
    padding: 20px;
    opacity: 0.8;
  }

  .chapter-slide { background-color: var(--primary-color); border: none !important; color: white !important; }
  .chapter-slide h2 { color: #FFD700 !important; border-bottom: none !important; }
  .chapter-slide h1 { color: white !important; text-shadow: 4px 4px 10px rgba(0,0,0,0.3) !important; }
  
  .slide-info {
    color: #aaa;
    font-family: monospace;
    margin-top: -40px;
    font-size: 14px;
    align-self: flex-start;
  }

  /* Table styles */
  .slide-table { width: 100%; border-collapse: collapse; font-size: 40px; margin-top: 20px; }
  .slide-table th, .slide-table td { border: 4px solid var(--primary-color); padding: 15px; text-align: left; }
  .slide-table th { background: var(--primary-color); color: white; }
`;

interface SlideProps {
  id: string;
  children: React.ReactNode;
  className?: string;
}

const Slide = ({ id, children, className = '' }: SlideProps) => (
  <div className="slide-wrapper" id={`slide-${id}`}>
    <div className="slide-info">Slide ID: {id}</div>
    <div className={`slide-container ${className}`}>
      {children}
    </div>
  </div>
);

const Placeholder = ({ text, width = '100%', height = '300px' }: { text: string, width?: string, height?: string }) => (
  <div className="img-placeholder" style={{ width, height }}>
    <i className="fa-solid fa-wand-magic-sparkles" style={{ marginRight: '15px' }}></i>
    {text}
  </div>
);

const ImageBox = ({ src, width = '100%', height = 'auto', maxHeight = '500px' }: { src: string, width?: string, height?: string, maxHeight?: string }) => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '20px', width, height }}>
    <img src={src} style={{ width: '100%', height: '100%', objectFit: 'contain', maxHeight }} alt="" />
  </div>
);

interface SlideData {
  id: number;
  content: string;
  speaker: string;
  expression: string;
  script: string;
}

const renderContent = (content: string) => {
  if (!content) return <div>No content</div>;
  const lines = content.split('\n');
  console.log('Rendering content:', content.substring(0, 50));
  
  // Chapter slide logic
  if (content.includes('章タイトル') || content.includes('Chapter')) {
    const chapterLine = lines.find(l => l.includes('Chapter') || l.includes('章タイトル')) || '';
    const title = chapterLine.replace(/章タイトル：|Chapter \d+/, '').trim();
    const chapterNumMatch = chapterLine.match(/Chapter (\d+)/);
    const otherLines = lines.filter(l => l !== chapterLine);

    return (
      <div className="chapter-content">
        <h2>{chapterNumMatch ? `Chapter ${chapterNumMatch[1]}` : 'Chapter'}</h2>
        <h1>{title}</h1>
        {otherLines.map((line, i) => <p key={i}>{line}</p>)}
      </div>
    );
  }

  // Common mapping for specific slides
  if (content.includes('評価項目について')) return <img src="/slides/common/評価項目について.png" alt="" />;
  if (content.includes('評価ランクの基準について')) return <img src="/slides/common/評価ランクの基準について.png" alt="" />;
  if (content.includes('評価は独断と偏見')) return <img src="/slides/common/評価は独断と偏見.png" alt="" />;
  if (content.includes('プランやキャンペーンは投稿時点')) return <img src="/slides/common/プランやキャンペーンは投稿時点のもの注意喚起.png" alt="" />;
  if (content.includes('ブログもやってます')) return <img src="/slides/common/ブログもやってます.png" alt="" />;
  if (content.includes('チャンネル登録と高評価')) return <img src="/slides/common/チャンネル登録と高評価よろしくお願いします.png" alt="" />;

  // Chart detection
  if (content.includes('レーダーチャート') || content.includes('成績表')) {
    if (content.includes('HISモバイル')) return <ImageBox src="/slides/charts/HISモバイル.png" />;
    if (content.includes('日本通信')) return <ImageBox src="/slides/charts/日本通信SIM.png" />;
    if (content.includes('IIJmio')) return <ImageBox src="/slides/charts/IIJmio.png" />;
    if (content.includes('LINEMO')) return <ImageBox src="/slides/charts/LINEMO.png" />;
  }

  return (
    <div style={{ textAlign: 'center', width: '100%' }}>
      {lines.map((line, i) => {
        if (line.startsWith('タイトルロゴ：')) {
          return <h1 key={i}>{line.replace('タイトルロゴ：', '')}</h1>;
        }
        if (line.startsWith('テキスト：') || line.startsWith('テキスト一覧：') || line.startsWith('リスト表示')) {
          const text = line.replace(/テキスト：|テキスト一覧：|リスト表示/, '').trim();
          if (text.includes('\n') || text.includes('・')) {
            const items = text.split(/\n|・/).filter(it => it.trim());
            return (
              <ul key={i} style={{ textAlign: 'left', display: 'inline-block' }}>
                {items.map((item, j) => <li key={j}>{item.trim()}</li>)}
              </ul>
            );
          }
          return <p key={i}>{text}</p>;
        }
        if (line.startsWith('比較表スライド表示：')) {
           return <Placeholder key={i} text="[IMAGE_PROMPT] 比較表の画像を生成または作成してください" height="500px" />;
        }
        if (line.startsWith('イラスト：') || line.startsWith('画像：') || line.startsWith('背景：') || line.startsWith('テロップ：')) {
          const prompt = line;
          if (line.includes('ロゴ') || line.includes('チャート') || line.includes('表') || line.includes('図解')) {
             return <Placeholder key={i} text={`[IMAGE_PROMPT] ${prompt}`} />;
          }
          return <p key={i} className="accent-text">{line.split('：')[1]}</p>;
        }
        return <p key={i}>{line}</p>;
      })}
    </div>
  );
};

export const GeneratedSlidesViewer = ({ slides }: { slides: SlideData[] }) => {
  return (
    <div className="slide-viewer-container">
      <style>{cssStyles}</style>
      {slides.map((slide) => {
        let className = '';
        if (slide.content.includes('Chapter')) className += ' chapter-slide';
        
        // Check for image-only
        const isImageOnly = [
          '評価項目について', 
          '評価ランクの基準について', 
          '評価は独断と偏見', 
          'プランやキャンペーン', 
          'ブログもやってます', 
          'チャンネル登録と高評価'
        ].some(key => slide.content.includes(key));
        
        if (isImageOnly) className += ' image-only-slide';

        return (
          <Slide key={slide.id} id={slide.id.toString()} className={className}>
            {renderContent(slide.content)}
          </Slide>
        );
      })}
    </div>
  );
};
