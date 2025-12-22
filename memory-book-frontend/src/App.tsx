import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import PublicMemoryList from "./pages/PublicMemoryList";
import MemoryPage from "./pages/MemoryPage";
import CreateMemory from "./pages/CreateMemory";
import MyMemoryList from "./pages/MyMemoryList";

export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/public" element={<PublicMemoryList />} />
        <Route path="/memory/:id" element={<MemoryPage />} />
        <Route path="/create" element={<CreateMemory />} />
        <Route path="/my-pages" element={<MyMemoryList />} />
      </Routes>
    </Router>
  );
}
