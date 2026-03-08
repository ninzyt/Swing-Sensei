import { useState } from 'react'
import './App.css'
import placeholder from './assets/alan-placeholder.svg'
import BubbleMenu from './assets/BubbleMenu.jsx'

function makeItems(setPage) {
  return [
    {
      label: 'resources',
      href: '#',
      ariaLabel: 'Resources',
      rotation: -8,
      hoverStyles: { bgColor: '#3b82f6', textColor: '#ffffff' },
      onClick: () => setPage('coaching')
    },
    {
      label: 'training',
      href: '#',
      ariaLabel: 'Training',
      rotation: 8,
      hoverStyles: { bgColor: '#10b981', textColor: '#ffffff' },
      onClick: () => setPage('coaching')
    },
    {
      label: 'summary',
      href: '#',
      ariaLabel: 'Summary',
      rotation: 8,
      hoverStyles: { bgColor: '#f59e0b', textColor: '#ffffff' },
      onClick: () => setPage('coaching')
    }
  ];
}

function App() {
  const [page, setPage] = useState('home') // 'home' or 'coaching'

  if (page === 'home') {
    return (
      <div className="home-page">
        <h1>Ready to train?</h1>
        {/* <button onClick={() => setPage('coaching')}>Resources</button>
        <button onClick={() => setPage('coaching')}>Start Coaching</button>
        <button onClick={() => setPage('coaching')}>See Summary</button> */}
        <div className="yes-no-wrapper">
          <BubbleMenu
            logo={<span style={{ fontWeight: 700 }}>RB</span>}
            items={makeItems(setPage)}
            menuAriaLabel="Toggle navigation"
            menuBg="#ffffff"
            menuContentColor="#111111"
            useFixedPosition={false}
            className="inline"
            animationEase="back.out(1.5)"
            animationDuration={0.5}
            staggerDelay={0.12}
          />
        </div>

        <img src={placeholder} alt="badminton" className='home-image'/>
      </div>
    )
  }

  return (
    <div className='training-page'> 
      <button onClick={() => setPage('home')}>← Back to Home</button>
      <iframe
        src="http://localhost:8501"
        width="100%"
        height="800px"
        style={{ border: 'none' }}
      />
    </div>
  )
}

export default App
