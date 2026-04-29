import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Cpu, LogIn, UserPlus, Lock, Mail, AlertTriangle, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

type Mode = 'login' | 'register';

export default function Login() {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const toast = useToast();

  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) { 
      toast.warning('VALIDATION_ERROR', 'Both fields are required.'); 
      return; 
    }

    setIsSubmitting(true);
    try {
      if (mode === 'login') {
        await login(email, password);
        toast.success('ACCESS_GRANTED', 'Authentication successful.');
      } else {
        await register(email, password);
        toast.success('ACCOUNT_CREATED', 'System registration complete.');
      }
      navigate('/profile');
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || 'An unexpected error occurred.';
      toast.error('ACCESS_DENIED', msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-[#030712] flex items-center justify-center font-mono">
      {/* Background glow blobs */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-neon-cyan/5 blur-[150px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full bg-neon-purple/5 blur-[120px] animate-pulse" />
      </div>
      {/* Scanlines */}
      <div className="scanlines fixed inset-0 pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="relative z-10 w-full max-w-md px-4"
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <div className="relative p-2">
            <Cpu className="h-8 w-8 text-neon-cyan animate-pulse-glow" />
            <svg className="absolute inset-0 w-full h-full text-neon-cyan/40 animate-[spin_10s_linear_infinite]" viewBox="0 0 100 100">
              <polygon points="50 3, 93 28, 93 72, 50 97, 7 72, 7 28" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
          <div>
            <p className="text-xl font-bold tracking-[0.2em] text-white text-glow-cyan">PLACEMENT.OS</p>
            <p className="text-[10px] tracking-widest text-neon-cyan/70 uppercase">Auth Gateway // v2.0</p>
          </div>
        </div>

        {/* Card */}
        <div className="cyber-panel p-8 relative">
          <div className="cyber-brackets" />

          {/* CLI Header */}
          <div className="flex items-center gap-2 mb-8 border-b border-gray-800 pb-3">
            <div className="w-3 h-3 rounded-full bg-red-500/50" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
            <div className="w-3 h-3 rounded-full bg-green-500/50" />
            <span className="ml-3 text-xs text-gray-500">
              root@placement-os:~# {mode === 'login' ? './auth_login.sh' : './auth_register.sh'}
            </span>
          </div>

          {/* Mode Toggle */}
          <div className="flex gap-1 mb-8 border border-gray-800 p-1">
            {(['login', 'register'] as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 py-2 text-xs tracking-widest uppercase transition-all flex items-center justify-center gap-2 ${
                  mode === m
                    ? 'bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/40'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                {m === 'login' ? <LogIn className="w-3 h-3" /> : <UserPlus className="w-3 h-3" />}
                {m}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div className="space-y-2 group">
              <label className="text-xs text-neon-cyan tracking-widest block group-focus-within:text-glow-cyan transition-all">
                <Mail className="inline w-3 h-3 mr-1" /> USER.EMAIL
              </label>
              <input
                type="email"
                id="auth-email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="email"
                className="w-full bg-black/50 border border-gray-800 focus:border-neon-cyan px-4 py-3 text-white placeholder:text-gray-700 focus:outline-none transition-all focus:shadow-[0_0_15px_rgba(0,243,255,0.15)]"
                placeholder="operator@system.io"
              />
            </div>

            {/* Password */}
            <div className="space-y-2 group">
              <label className="text-xs text-neon-purple tracking-widest block group-focus-within:text-glow-purple transition-all">
                <Lock className="inline w-3 h-3 mr-1" /> ACCESS.KEY
              </label>
              <input
                type="password"
                id="auth-password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                className="w-full bg-black/50 border border-gray-800 focus:border-neon-purple px-4 py-3 text-white placeholder:text-gray-700 focus:outline-none transition-all focus:shadow-[0_0_15px_rgba(181,55,242,0.15)]"
                placeholder={mode === 'register' ? 'Min. 6 characters' : '••••••••'}
              />
            </div>

            </div>

            {/* Submit */}
            <button
              type="submit"
              id="auth-submit"
              disabled={isSubmitting}
              className="w-full group relative border border-neon-cyan bg-neon-cyan/10 hover:bg-neon-cyan/20 text-neon-cyan py-3 uppercase tracking-widest text-xs transition-all duration-300 flex items-center justify-center gap-3 overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              <div className="absolute inset-0 w-full h-full bg-neon-cyan/20 -translate-x-full group-hover:animate-[scanline_1s_ease-in-out]" />
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> AUTHENTICATING...</>
              ) : mode === 'login' ? (
                <><LogIn className="w-4 h-4" /> EXECUTE.LOGIN()</>
              ) : (
                <><UserPlus className="w-4 h-4" /> EXECUTE.REGISTER()</>
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-gray-700 text-xs mt-6 tracking-wider">
          // AUTHORIZED PERSONNEL ONLY — PLACEMENT.OS v2.0
        </p>
      </motion.div>
    </div>
  );
}
