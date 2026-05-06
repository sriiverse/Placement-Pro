import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, UserCircle, Cpu, LogOut } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const links = [
    { name: 'SYS.DASHBOARD', path: '/dashboard', icon: LayoutDashboard },
    { name: 'USR.PROFILE', path: '/profile', icon: UserCircle },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="relative z-50 w-full border-b border-neon-cyan/30 bg-surface/90 backdrop-blur-md">
      <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
      
      <div className="flex justify-between items-center h-16 px-6">
        {/* Logo Section */}
        <div className="flex items-center space-x-3">
          <div className="relative p-2">
            <Cpu className="h-6 w-6 text-neon-cyan animate-pulse-glow" />
            <svg className="absolute inset-0 w-full h-full text-neon-cyan/40 animate-[spin_10s_linear_infinite]" viewBox="0 0 100 100">
              <polygon points="50 3, 93 28, 93 72, 50 97, 7 72, 7 28" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="font-mono text-xl font-bold tracking-[0.2em] text-white text-glow-cyan">
              PLACEMENT.OS
            </span>
            <span className="font-mono text-[10px] tracking-widest text-neon-cyan/70 uppercase">
              SkillGap AI v2.0 // Active
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex space-x-4">
          {links.map((link) => {
            const isActive = location.pathname === link.path;
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={cn(
                  "relative px-6 py-2 flex items-center space-x-2 font-mono text-sm tracking-wider transition-all duration-300",
                  isActive ? "text-neon-cyan text-glow-cyan" : "text-gray-400 hover:text-neon-cyan"
                )}
              >
                {isActive && (
                  <>
                    <motion.div layoutId="nav-bracket-left" className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-4 border-l-2 border-y-2 border-neon-cyan" />
                    <motion.div layoutId="nav-bracket-right" className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-4 border-r-2 border-y-2 border-neon-cyan" />
                    <motion.div layoutId="nav-bg" className="absolute inset-x-2 bottom-0 h-[2px] bg-neon-cyan blur-[2px]" />
                  </>
                )}
                <Icon className={cn("h-4 w-4", isActive ? "animate-pulse-glow" : "")} />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right: Operator info + Logout */}
        <div className="flex items-center space-x-4 font-mono text-xs">
          {user && (
            <div className="flex flex-col text-right">
              <span className="text-gray-500 text-[10px]">OPERATOR</span>
              <span className="text-neon-cyan truncate max-w-[160px]">{user.email}</span>
            </div>
          )}
          <button
            onClick={handleLogout}
            title="Logout"
            className="flex items-center gap-1.5 px-3 py-1.5 border border-neon-pink/40 text-neon-pink hover:bg-neon-pink/10 transition-all text-[10px] tracking-widest uppercase"
          >
            <LogOut className="w-3 h-3" />
            EXIT
          </button>
        </div>
      </div>
    </header>
  );
}
