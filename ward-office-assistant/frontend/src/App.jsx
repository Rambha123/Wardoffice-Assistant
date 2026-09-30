import { Routes, Route, Link } from "react-router-dom";

import ChatPage from "./pages/ChatPage.jsx";
import ChecklistPage from "./pages/ChecklistPage.jsx";
import DocumentReadinessPage from "./pages/DocumentReadinessPage.jsx";
import WardInfoPage from "./pages/WardInfoPage.jsx";
import AdminPage from "./pages/AdminPage.jsx";

function NavBar() {
  const linkClass = "px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-ward-primary/80";

  return (
    <nav className="bg-ward-primary">
      <div className="max-w-5xl mx-auto flex items-center justify-between px-4 py-3">
        <span className="text-white font-semibold">Ward Office Assistant</span>
        <div className="flex gap-1">
          <Link className={linkClass} to="/">Ask a Question</Link>
          <Link className={linkClass} to="/checklist">Checklist</Link>
          <Link className={linkClass} to="/readiness">Document Check</Link>
          <Link className={linkClass} to="/office-info">Ward Info</Link>
          {/* TODO: hide this link unless the logged-in user has the
              ward_staff/admin role once auth is implemented. */}
          <Link className={linkClass} to="/admin">Admin</Link>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/checklist" element={<ChecklistPage />} />
          <Route path="/readiness" element={<DocumentReadinessPage />} />
          <Route path="/office-info" element={<WardInfoPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </main>
    </div>
  );
}
