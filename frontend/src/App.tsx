import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import ProfileForm from './pages/ProfileForm';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

// ─── Protected Route Guard ────────────────────────────────────────────────────
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  // Still checking sessionStorage / /me endpoint on first load
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center font-mono">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-neon-cyan animate-spin mx-auto" />
          <p className="text-neon-cyan tracking-widest animate-pulse text-xs">VERIFYING_AUTH...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// ─── App Router ───────────────────────────────────────────────────────────────
function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public route — redirect to /profile if already logged in */}
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/profile" replace /> : <Login />}
      />

      {/* Protected routes inside the shared AppLayout */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<ProfileForm />} />
      </Route>

      {/* Catch-all: redirect unknown paths to login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
