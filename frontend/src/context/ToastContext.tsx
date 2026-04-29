import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertTriangle, Info, Database, X } from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────
type ToastType = 'success' | 'error' | 'warning' | 'info' | 'cached';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  toast: {
    success: (title: string, message?: string) => void;
    error:   (title: string, message?: string) => void;
    warning: (title: string, message?: string) => void;
    info:    (title: string, message?: string) => void;
    cached:  (title: string, message?: string) => void;
  };
}

// ─── Context ──────────────────────────────────────────────────────────────────
const ToastContext = createContext<ToastContextType | null>(null);

// ─── Config ───────────────────────────────────────────────────────────────────
const TOAST_CONFIG: Record<ToastType, {
  icon: typeof CheckCircle;
  color: string;
  border: string;
  bg: string;
  glow: string;
}> = {
  success: {
    icon: CheckCircle,
    color: 'text-neon-cyan',
    border: 'border-neon-cyan/40',
    bg: 'bg-neon-cyan/5',
    glow: 'shadow-[0_0_20px_rgba(0,243,255,0.15)]',
  },
  error: {
    icon: XCircle,
    color: 'text-neon-pink',
    border: 'border-neon-pink/40',
    bg: 'bg-neon-pink/5',
    glow: 'shadow-[0_0_20px_rgba(255,16,120,0.15)]',
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-400',
    border: 'border-yellow-400/40',
    bg: 'bg-yellow-400/5',
    glow: 'shadow-[0_0_20px_rgba(250,204,21,0.15)]',
  },
  info: {
    icon: Info,
    color: 'text-neon-purple',
    border: 'border-neon-purple/40',
    bg: 'bg-neon-purple/5',
    glow: 'shadow-[0_0_20px_rgba(181,55,242,0.15)]',
  },
  cached: {
    icon: Database,
    color: 'text-neon-cyan',
    border: 'border-neon-cyan/20',
    bg: 'bg-neon-cyan/3',
    glow: '',
  },
};

// ─── Individual Toast Component ───────────────────────────────────────────────
function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
  const cfg = TOAST_CONFIG[toast.type];
  const Icon = cfg.icon;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 80, scale: 0.95 }}
      animate={{ opacity: 1, x: 0,  scale: 1 }}
      exit={{    opacity: 0, x: 80, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
      className={`
        relative flex items-start gap-3 px-4 py-3 font-mono text-xs
        border backdrop-blur-md min-w-[280px] max-w-[360px]
        ${cfg.border} ${cfg.bg} ${cfg.glow}
      `}
    >
      {/* Left accent bar */}
      <div className={`absolute left-0 top-0 w-0.5 h-full ${cfg.color.replace('text-', 'bg-')}`} />

      <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${cfg.color}`} />

      <div className="flex-1 min-w-0">
        <p className={`font-bold tracking-widest uppercase text-[10px] ${cfg.color}`}>
          {toast.title}
        </p>
        {toast.message && (
          <p className="text-gray-400 mt-0.5 leading-relaxed">{toast.message}</p>
        )}
      </div>

      <button
        onClick={() => onRemove(toast.id)}
        className="text-gray-600 hover:text-gray-400 transition-colors shrink-0 mt-0.5"
      >
        <X className="w-3 h-3" />
      </button>
    </motion.div>
  );
}

// ─── Provider ─────────────────────────────────────────────────────────────────
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addToast = useCallback((type: ToastType, title: string, message?: string, duration = 4000) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    setToasts(prev => [...prev.slice(-4), { id, type, title, message, duration }]); // max 5 at once
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }
  }, [removeToast]);

  const toast = {
    success: (title: string, msg?: string) => addToast('success', title, msg),
    error:   (title: string, msg?: string) => addToast('error',   title, msg, 6000),
    warning: (title: string, msg?: string) => addToast('warning', title, msg),
    info:    (title: string, msg?: string) => addToast('info',    title, msg),
    cached:  (title: string, msg?: string) => addToast('cached',  title, msg, 2500),
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {/* Toast Container — fixed bottom-right, above everything */}
      <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2 items-end pointer-events-none">
        <AnimatePresence mode="popLayout">
          {toasts.map(t => (
            <div key={t.id} className="pointer-events-auto">
              <ToastItem toast={t} onRemove={removeToast} />
            </div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────
export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>');
  return ctx.toast;
}
