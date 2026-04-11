import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Database, Code2, ArrowRight, ShieldCheck, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const steps = [
  { id: 1, name: 'ID_CONFIG', icon: Terminal },
  { id: 2, name: 'ACADEMIC_DATA', icon: Database },
  { id: 3, name: 'SKILL_MATRIX', icon: Code2 },
];

export default function ProfileForm() {
  const [activeStep, setActiveStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [warnings, setWarnings] = useState<Record<string, string>>({});
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: '',
    target_designation: '',
    cgpa: '',
    grad_year: '2024',
    branch: '',
    skills: '',
    internships_count: '',
    projects_count: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    let filteredValue = value;
    if (['full_name', 'target_designation', 'branch'].includes(name)) {
      filteredValue = value.replace(/[\d]/g, ''); // Strip numbers
    } else if (['internships_count', 'projects_count'].includes(name)) {
      filteredValue = value.replace(/[^\d]/g, ''); // Strip non-numbers
    } else if (name === 'cgpa') {
      filteredValue = value.replace(/[^\d.]/g, ''); // Allow only digits and decimal
      const parts = filteredValue.split('.');
      if (parts.length > 2) {
        filteredValue = parts[0] + '.' + parts.slice(1).join('');
      }
    }
    
    setFormData({ ...formData, [name]: filteredValue });

    const newWarnings = { ...warnings };
    if (['full_name', 'target_designation', 'branch'].includes(name)) {
      if (/\d/.test(value)) {
        newWarnings[name] = 'WARNING: Digits blocked. Alphabetic only.';
      } else {
        delete newWarnings[name];
      }
    } else if (['cgpa', 'internships_count', 'projects_count'].includes(name)) {
      if (/[a-zA-Z]/.test(value)) {
        newWarnings[name] = 'WARNING: Alphabets blocked. Numeric only.';
      } else {
        delete newWarnings[name];
      }
    }
    setWarnings(newWarnings);
  };

  const handleSubmit = async () => {
    if (activeStep < steps.length) {
      setActiveStep(activeStep + 1);
      return;
    }

    setIsSubmitting(true);
    try {
      // Process skills into array, filter empty strings
      const processedData = {
        ...formData,
        skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean)
      };

      const baseUrl = import.meta.env.VITE_API_URL.replace(/\/api\/?$/, '');
      const response = await axios.post(`${baseUrl}/api/submit-profile`, processedData);
      
      if (response.data && response.data.user_id) {
        localStorage.setItem('user_id', response.data.user_id.toString());
      }
      
      // Navigate to dashboard on success
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to submit profile:', error);
      alert('SYSTEM_ERROR: Database connection failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto min-h-full flex flex-col font-mono text-gray-300">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 border-l-4 border-neon-cyan pl-4"
      >
        <h1 className="text-3xl font-bold tracking-widest text-white text-glow-cyan uppercase">
          UserProfile::Init()
        </h1>
        <p className="text-gray-500 mt-2 text-xs">
          /* Input required parameters for system calibration and AI matching */
        </p>
      </motion.div>

      {/* Cyber Stepper */}
      <div className="flex justify-between items-center mb-12 relative px-4">
        {/* Connection Line */}
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-[1px] bg-gray-800 z-0" />
        <motion.div 
          className="absolute left-0 top-1/2 -translate-y-1/2 h-[2px] bg-neon-cyan z-0 origin-left drop-shadow-[0_0_8px_rgba(0,243,255,0.8)]"
          initial={{ scaleX: 0 }}
          animate={{ scaleX: (activeStep - 1) / (steps.length - 1) }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
        />
        
        {steps.map((step) => {
          const Icon = step.icon;
          const isActive = step.id === activeStep;
          const isCompleted = step.id < activeStep;

          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center gap-3 bg-[#030712] px-4">
              <motion.div 
                initial={false}
                animate={{
                  borderColor: isActive || isCompleted ? 'hsl(var(--primary))' : '#1f2937',
                  backgroundColor: isActive ? 'rgba(0, 243, 255, 0.1)' : '#030712',
                }}
                className={cn(
                  "w-10 h-10 border-2 flex items-center justify-center transition-colors duration-300 rotate-45",
                  (isActive || isCompleted) && "border-neon-cyan shadow-[0_0_15px_rgba(0,243,255,0.3)]"
                )}
              >
                <div className="-rotate-45">
                  {(isCompleted && !isActive) ? (
                    <ShieldCheck className="w-5 h-5 text-neon-cyan" />
                  ) : (
                    <Icon className={cn("w-4 h-4", isActive ? "text-neon-cyan animate-pulse-glow" : "text-gray-600")} />
                  )}
                </div>
              </motion.div>
              <span className={cn(
                "text-[10px] uppercase tracking-widest transition-colors",
                isActive ? "text-neon-cyan text-glow-cyan font-bold" : "text-gray-600"
              )}>
                [{step.name}]
              </span>
            </div>
          );
        })}
      </div>

      {/* Terminal Form Container */}
      <motion.div 
        layout
        className="cyber-panel p-8 relative flex-1 min-h-[400px]"
      >
        <div className="cyber-brackets" />
        {/* CLI Header */}
        <div className="flex items-center gap-2 mb-8 border-b border-gray-800 pb-2">
          <div className="w-3 h-3 rounded-full bg-red-500/50" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
          <div className="w-3 h-3 rounded-full bg-green-500/50" />
          <span className="ml-4 text-xs text-gray-500">root@placement-os:~# ./config_user.sh</span>
        </div>
        
        <form className="space-y-8 pb-6" onSubmit={(e) => e.preventDefault()}>
          <AnimatePresence mode="wait">
            {activeStep === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="space-y-2 group">
                  <label className="text-xs text-neon-cyan tracking-widest block group-focus-within:text-glow-cyan transition-all">
                    &gt; USER.FULL_NAME
                  </label>
                  <input 
                    type="text" 
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className="w-full bg-black/50 border border-gray-800 focus:border-neon-cyan px-4 py-3 text-white placeholder:text-gray-800 focus:outline-none transition-all shadow-[inset_0_0_10px_rgba(0,0,0,0.5)] focus:shadow-[0_0_15px_rgba(0,243,255,0.2)]"
                    placeholder="Enter string value..."
                  />
                  {warnings.full_name && <p className="text-[10px] text-red-500 mt-1 uppercase tracking-widest bg-red-900/20 px-2 py-1 border border-red-500/30 rounded inline-block w-full">! {warnings.full_name}</p>}
                </div>
                <div className="space-y-2 group">
                  <label className="text-xs text-neon-cyan tracking-widest block group-focus-within:text-glow-cyan transition-all">
                    &gt; TARGET.DESIGNATION
                  </label>
                  <input 
                    type="text"
                    name="target_designation" 
                    value={formData.target_designation}
                    onChange={handleChange}
                    className="w-full bg-black/50 border border-gray-800 focus:border-neon-cyan px-4 py-3 text-white placeholder:text-gray-800 focus:outline-none transition-all shadow-[inset_0_0_10px_rgba(0,0,0,0.5)] focus:shadow-[0_0_15px_rgba(0,243,255,0.2)]"
                    placeholder="e.g., Software_Engineer"
                  />
                  {warnings.target_designation && <p className="text-[10px] text-red-500 mt-1 uppercase tracking-widest bg-red-900/20 px-2 py-1 border border-red-500/30 rounded inline-block w-full">! {warnings.target_designation}</p>}
                </div>
              </motion.div>
            )}

            {activeStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2 group">
                    <label className="text-xs text-neon-purple tracking-widest block group-focus-within:text-glow-purple transition-all">
                      &gt; METRIC.CGPA
                    </label>
                    <input 
                      type="text" 
                      inputMode="decimal"
                      name="cgpa"
                      value={formData.cgpa}
                      onChange={handleChange}
                      className="w-full bg-black/50 border border-gray-800 focus:border-neon-purple px-4 py-3 text-white placeholder:text-gray-800 focus:outline-none transition-all focus:shadow-[0_0_15px_rgba(181,55,242,0.2)]"
                      placeholder="Float value (0.00-10.00)"
                    />
                    {warnings.cgpa && <p className="text-[10px] text-red-500 mt-1 uppercase tracking-widest bg-red-900/20 px-2 py-1 border border-red-500/30 rounded inline-block w-full">! {warnings.cgpa}</p>}
                  </div>
                  <div className="space-y-2 group">
                    <label className="text-xs text-neon-purple tracking-widest block group-focus-within:text-glow-purple transition-all">
                      &gt; TIMEFRAME.GRAD_YEAR
                    </label>
                    <select 
                      name="grad_year"
                      value={formData.grad_year}
                      onChange={handleChange}
                      className="w-full bg-black/50 border border-gray-800 focus:border-neon-purple px-4 py-3 text-white focus:outline-none transition-all appearance-none cursor-pointer focus:shadow-[0_0_15px_rgba(181,55,242,0.2)]">
                      <option value="2024" className="bg-gray-900 border-none">2024</option>
                      <option value="2025" className="bg-gray-900 border-none">2025</option>
                      <option value="2026" className="bg-gray-900 border-none">2026</option>
                      <option value="2027" className="bg-gray-900 border-none">2027</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-2 group">
                  <label className="text-xs text-neon-purple tracking-widest block group-focus-within:text-glow-purple transition-all">
                    &gt; ACADEMIC.BRANCH
                  </label>
                  <input 
                    type="text" 
                    name="branch"
                    value={formData.branch}
                    onChange={handleChange}
                    className="w-full bg-black/50 border border-gray-800 focus:border-neon-purple px-4 py-3 text-white placeholder:text-gray-800 focus:outline-none transition-all focus:shadow-[0_0_15px_rgba(181,55,242,0.2)]"
                    placeholder="e.g., Computer_Science"
                  />
                  {warnings.branch && <p className="text-[10px] text-red-500 mt-1 uppercase tracking-widest bg-red-900/20 px-2 py-1 border border-red-500/30 rounded inline-block w-full">! {warnings.branch}</p>}
                </div>
              </motion.div>
            )}

            {activeStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="space-y-2 group">
                  <label className="text-xs text-neon-pink tracking-widest block transition-all">
                    &gt; ARRAY.SKILLS [csv]
                  </label>
                  <textarea 
                    rows={3}
                    name="skills"
                    value={formData.skills}
                    onChange={handleChange}
                    className="w-full bg-black/50 border border-gray-800 focus:border-neon-pink px-4 py-3 text-white placeholder:text-gray-800 focus:outline-none transition-all resize-none focus:shadow-[0_0_15px_rgba(241,44,138,0.2)]"
                    placeholder="React, Node.js, Python..."
                  />
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2 group">
                    <label className="text-xs text-neon-pink tracking-widest block transition-all">
                      &gt; COUNT.INTERNSHIPS
                    </label>
                    <input 
                      type="text" 
                      inputMode="numeric"
                      name="internships_count"
                      value={formData.internships_count}
                      onChange={handleChange}
                      className="w-full bg-black/50 border border-gray-800 focus:border-neon-pink px-4 py-3 text-white placeholder:text-gray-800 focus:outline-none transition-all focus:shadow-[0_0_15px_rgba(241,44,138,0.2)]"
                      placeholder="Int >= 0"
                    />
                    {warnings.internships_count && <p className="text-[10px] text-red-500 mt-1 uppercase tracking-widest bg-red-900/20 px-2 py-1 border border-red-500/30 rounded inline-block w-full">! {warnings.internships_count}</p>}
                  </div>
                  <div className="space-y-2 group">
                    <label className="text-xs text-neon-pink tracking-widest block transition-all">
                      &gt; COUNT.PROJECTS
                    </label>
                    <input 
                      type="text" 
                      inputMode="numeric"
                      name="projects_count"
                      value={formData.projects_count}
                      onChange={handleChange}
                      className="w-full bg-black/50 border border-gray-800 focus:border-neon-pink px-4 py-3 text-white placeholder:text-gray-800 focus:outline-none transition-all focus:shadow-[0_0_15px_rgba(241,44,138,0.2)]"
                      placeholder="Int >= 0"
                    />
                    {warnings.projects_count && <p className="text-[10px] text-red-500 mt-1 uppercase tracking-widest bg-red-900/20 px-2 py-1 border border-red-500/30 rounded inline-block w-full">! {warnings.projects_count}</p>}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="pt-8 mt-12 pb-2 mb-2 flex justify-between border-t border-gray-800">
            <button
              type="button"
              onClick={() => setActiveStep(Math.max(1, activeStep - 1))}
              className={cn(
                "px-6 py-2 uppercase tracking-widest text-xs border transition-all duration-300",
                activeStep === 1 
                  ? "opacity-0 pointer-events-none" 
                  : "border-gray-800 text-gray-500 hover:text-white hover:border-gray-500"
              )}
            >
              &lt;_Abort
            </button>
            
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting || Object.keys(warnings).length > 0}
              className="group relative border border-neon-cyan bg-neon-cyan/10 hover:bg-neon-cyan/20 text-neon-cyan px-8 py-2 uppercase tracking-widest text-xs transition-all duration-300 flex items-center gap-3 overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 w-full h-full bg-neon-cyan/20 -translate-x-full group-hover:animate-[scanline_1s_ease-in-out]" />
              {isSubmitting ? (
                 <><Loader2 className="w-4 h-4 animate-spin" /> COMPILING...</>
              ) : activeStep === steps.length ? (
                 'EXECUTE.COMPILE()' 
              ) : (
                 'EXECUTE.NEXT()'
              )}
              {(!isSubmitting && activeStep !== steps.length) && <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
