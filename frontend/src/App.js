import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <iframe
  src="http://localhost:8501"
  width="100%"
  height="800px"
  style={{ border: 'none' }}
  title="Coach Alan Wu"
/>

      </header>
    </div>
  );
}

export default App;
