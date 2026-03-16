import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './Navbar';

export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen relative overflow-hidden bg-[#030712] text-gray-300 selection:bg-neon-cyan/30">
      {/* Global CSS Scanlines Overlay */}
      <div className="scanlines" />

      {/* Decorative HUD Background Elements (Inspired by uploaded images) */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[20%] left-[10%] w-[600px] h-[600px] rounded-full bg-neon-cyan/5 blur-[150px] mix-blend-screen" />
        <div className="absolute bottom-[20%] right-[10%] w-[500px] h-[500px] rounded-full bg-neon-purple/5 blur-[120px] mix-blend-screen animate-pulse-slow" />
      </div>

      {/* Main Container */}
      <div className="relative z-10 flex flex-col h-screen overflow-hidden">
        <Navbar />
        
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-4 sm:p-6 lg:p-8">
          <div className="max-w-[1600px] mx-auto h-full">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, scale: 0.98, filter: 'blur(5px)' }}
                animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                exit={{ opacity: 0, scale: 1.02, filter: 'blur(5px)' }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="h-full"
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>

        {/* HUD Frame Borders */}
        <div className="fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50 z-50" />
        <div className="fixed bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-neon-purple to-transparent opacity-50 z-50" />
        <div className="fixed top-0 left-0 w-1 h-full bg-gradient-to-b from-transparent via-neon-cyan/30 to-transparent z-50 pointer-events-none" />
        <div className="fixed top-0 right-0 w-1 h-full bg-gradient-to-b from-transparent via-neon-cyan/30 to-transparent z-50 pointer-events-none" />
      </div>
    </div>
  );
}
