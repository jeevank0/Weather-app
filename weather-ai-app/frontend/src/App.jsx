import { Navigate, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import HistoryPage from './pages/HistoryPage';
import HomePage from './pages/HomePage';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export default App;
