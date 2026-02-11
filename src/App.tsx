import { useState } from 'react';
import { GeneratedSlidesViewer } from './generated/GeneratedSlidesViewer';
import slideData from './data/slides.json';

function App() {
  const [scale, setScale] = useState(0.6);

  return (
    <div className="App" style={{ backgroundColor: '#111', minHeight: '100vh' }}>
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '60px',
        backgroundColor: '#222',
        display: 'flex',
        alignItems: 'center',
        padding: '0 20px',
        zIndex: 1000,
        borderBottom: '1px solid #444',
        color: 'white',
        gap: '20px'
      }}>
        <h1 style={{ fontSize: '20px', margin: 0 }}>YouTube Slide Generator</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <label>Scale: {Math.round(scale * 100)}%</label>
          <input 
            type="range" 
            min="0.1" 
            max="1" 
            step="0.05" 
            value={scale} 
            onChange={(e) => setScale(parseFloat(e.target.value))} 
          />
        </div>
      </div>
      <div style={{ 
        paddingTop: '80px', 
        transform: `scale(${scale})`, 
        transformOrigin: 'top center',
        width: `${100 / scale}%`
      }}>
        <GeneratedSlidesViewer slides={slideData} />
      </div>
    </div>
  );
}

export default App;