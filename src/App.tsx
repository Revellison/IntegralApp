import { HashRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Sidebar from './components/sidebar/sidebar'
import Home from './pages/home/Home'
import Drawpad from './pages/drawpad/Drawpad'

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/drawpad" element={<Drawpad />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App 