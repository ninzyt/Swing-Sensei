import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import placeholder from './assets/alan-placeholder.svg'


function App() {
  const [page, setPage] = useState('home') // 'home' or 'coaching'

  if (page === 'home') {
    return (
      <div className = "home-page">
        <h1>Ready to train?</h1>
        <button onClick={() => setPage('coaching')}>Resources</button>
        <button onClick={() => setPage('coaching')}>Start Coaching</button>
        <button onClick={() => setPage('coaching')}>See Summary</button>
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
