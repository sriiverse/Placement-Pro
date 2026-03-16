import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, UserCircle, Cpu } from 'lucide-react';
import { cn } from '../../lib/utils';

export default function Navbar() {
  const location = useLocation();

  const links = [
    { name: 'SYS.DASHBOARD', path: '/', icon: LayoutDashboard },
    { name: 'USR.PROFILE', path: '/profile', icon: UserCircle },
  ];

  return (
    <header className="relative z-50 w-full border-b border-neon-cyan/30 bg-surface/90 backdrop-blur-md">
      <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
      
      <div className="flex justify-between items-center h-16 px-6">
        {/* Logo Section */}
        <div className="flex items-center space-x-3">
          <div className="relative p-2">
            <Cpu className="h-6 w-6 text-neon-cyan animate-pulse-glow" />
            {/* Hexagon accent */}
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
                {/* HUD Bracket Effects */}
                {isActive && (
                  <>
                    <motion.div
                      layoutId="nav-bracket-left"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-4 border-l-2 border-y-2 border-neon-cyan"
                    />
                    <motion.div
                      layoutId="nav-bracket-right"
                      className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-4 border-r-2 border-y-2 border-neon-cyan"
                    />
                    {/* Glowing highlight under text */}
                    <motion.div 
                      layoutId="nav-bg"
                      className="absolute inset-x-2 bottom-0 h-[2px] bg-neon-cyan blur-[2px]"
                    />
                  </>
                )}
                
                <Icon className={cn("h-4 w-4", isActive ? "animate-pulse-glow" : "")} />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* System Status Indicator */}
        <div className="flex items-center space-x-3 font-mono text-xs">
          <div className="flex flex-col text-right">
            <span className="text-gray-400">SYS_LOAD</span>
            <span className="text-neon-purple text-glow-purple">12.4%</span>
          </div>
          <div className="flex flex-col text-right">
            <span className="text-gray-400">NETWORK</span>
            <span className="text-neon-cyan text-glow-cyan">SECURE</span>
          </div>
          <div className="h-8 w-8 rounded-full border border-neon-cyan/50 flex items-center justify-center relative">
            <div className="absolute inset-1 rounded-full border border-neon-cyan border-t-transparent animate-[spin_2s_linear_infinite]" />
            <div className="absolute inset-2 rounded-full border border-neon-purple border-b-transparent animate-[spin_3s_linear_infinite_reverse]" />
            <div className="h-2 w-2 bg-neon-cyan rounded-full animate-pulse-glow" />
          </div>
        </div>
      </div>
    </header>
  );
}
