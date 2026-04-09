import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Target, Cpu, Activity, ShieldAlert, Crosshair, 
  ChevronRight, Zap, Lock, Map, TrendingUp,
  AlertTriangle, CheckCircle, Clock, Building2, Loader2, Plus
} from 'lucide-react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, CartesianGrid
} from 'recharts';
import axios from 'axios';
import { cn } from '../lib/utils';

const API = import.meta.env.VITE_API_URL.replace(/\/api\/?$/, '') + '/api';

interface DashboardData {
  profile: any;
  prediction: {
    probability: number;
    confidence: string;
    key_factors: string[];
  };
  companies: Array<{
    name: string;
    tier: string;
    match_score: number;
    matched_skills: string[];
    roles: string[];
    package_lpa: string;
    logo_color: string;
  }>;
  skill_gap: {
    missing_skills: string[];
    skill_gaps: Array<{ skill: string; priority: string; reason: string; resources: string[] }>;
    strengths: string[];
    readiness_score: number;
    summary: string;
  };
}

type TabId = 'overview' | 'companies' | 'skills' | 'roadmap';

const TABS: { id: TabId; label: string; icon: typeof Target }[] = [
  { id: 'overview', label: 'OVERVIEW', icon: Crosshair },
  { id: 'companies', label: 'COMPANIES', icon: Building2 },
  { id: 'skills', label: 'SKILL_GAP', icon: Zap },
  { id: 'roadmap', label: 'ROADMAP', icon: Map },
];

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [roadmap, setRoadmap] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [roadmapLoading, setRoadmapLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [simulatedSkills, setSimulatedSkills] = useState<string[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      setIsLoading(false);
      return;
    }
    const userId_int = parseInt(userId);
    
    axios.post(`${API}/dashboard`, { user_id: userId_int })
      .then(res => {
        if (res.data.status === 'success') setData(res.data);
      })
      .catch(err => console.error('Dashboard fetch error:', err))
      .finally(() => setIsLoading(false));
  }, []);

  const loadRoadmap = async () => {
    const userId = localStorage.getItem('user_id');
    if (!userId || roadmapLoading) return;
    setRoadmapLoading(true);
    try {
      const res = await axios.post(`${API}/generate-roadmap`, { user_id: parseInt(userId) });
      if (res.data.status === 'success') setRoadmap(res.data.roadmap);
    } catch (e) {
      console.error(e);
    } finally {
      setRoadmapLoading(false);
    }
  };

  const runSimulation = (newSkill: string) => {
    const userId = localStorage.getItem('user_id');
    if (!userId) return;
    setIsSimulating(true);
    
    // Add new skill to simulated skills
    const updatedSkills = [...simulatedSkills, newSkill];
    setSimulatedSkills(updatedSkills);
    
    // Combine original profile skills with simulated ones
    const baseSkills = data?.profile?.skills ? data.profile.skills.split(',').map((s: string) => s.trim()) : [];
    const combinedSkills = Array.from(new Set([...baseSkills, ...updatedSkills])).join(',');

    axios.post(`${API}/dashboard`, { user_id: parseInt(userId), simulated_skills: combinedSkills })
      .then(res => {
        if (res.data.status === 'success') {
          setData(prev => prev ? {
            ...prev,
            prediction: res.data.prediction,
            companies: res.data.companies,
            skill_gap: res.data.skill_gap
          } : null);
        }
      })
      .catch(err => console.error('Simulation error:', err))
      .finally(() => setIsSimulating(false));
  };

  const prob = data?.prediction?.probability ?? 0;
  const dashOffset = 283 * (1 - prob / 100);

  const trendData = Array.from({ length: 12 }, (_, i) => {
    const w = i + 1;
    const currentProb = data?.prediction?.probability || 50;
    const growth = (95 - currentProb) * (w / 12);
    return { week: `W${w}`, probability: Math.round(currentProb + growth) };
  });

  const radarData = [
    ...(data?.skill_gap?.strengths || []).map(s => ({ subject: s, score: 90, fullMark: 100 })),
    ...(data?.skill_gap?.missing_skills || []).map(s => ({ subject: s, score: 30, fullMark: 100 }))
  ].slice(0, 6);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full font-mono">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-neon-cyan animate-spin mx-auto" />
          <p className="text-neon-cyan tracking-widest animate-pulse">LOADING_CORE_SYSTEMS...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-full font-mono text-center">
        <div className="cyber-panel p-8 max-w-md">
          <AlertTriangle className="w-12 h-12 text-neon-pink mx-auto mb-4" />
          <p className="text-neon-pink tracking-widest">NO_PROFILE_DATA</p>
          <p className="text-gray-500 mt-2 text-xs">Submit your profile to activate the system</p>
          <a href="/profile" className="mt-6 inline-block border border-neon-cyan text-neon-cyan px-6 py-2 text-xs tracking-widest hover:bg-neon-cyan/10 transition-all">
            INIT_PROFILE()
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="font-mono text-sm space-y-6 flex flex-col h-full">
      {/* HUD Header */}
      <div className="flex justify-between items-end border-b border-neon-cyan/20 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-neon-cyan text-glow-cyan tracking-[0.2em] flex items-center gap-3">
            <Crosshair className="w-8 h-8 animate-[spin_4s_linear_infinite]" />
            OVERVIEW_TERMINAL
          </h1>
          <p className="text-gray-400 mt-1 tracking-widest text-xs uppercase">
            // USR: {data.profile?.full_name} | TARGET: {data.profile?.target_designation}
          </p>
        </div>
        <div className="flex gap-4">
          <div className="cyber-panel px-4 py-2 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-neon-pink" />
            <span className="text-neon-pink text-xs">SEC_LEVEL: ALPHA</span>
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => { setActiveTab('roadmap'); if (!roadmap.length) loadRoadmap(); }}
            className="border border-neon-cyan bg-neon-cyan/10 hover:bg-neon-cyan/20 text-neon-cyan px-6 py-2 uppercase tracking-widest text-xs transition-colors flex items-center gap-2 relative overflow-hidden group"
          >
            <div className="absolute inset-0 w-full h-full bg-neon-cyan/20 -translate-x-full group-hover:animate-[scanline_1s_ease-in-out]" />
            <Cpu className="w-4 h-4" />
            INIT_ROADMAP()
          </motion.button>
          {simulatedSkills.length > 0 && (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="border border-neon-pink bg-neon-pink/10 text-neon-pink px-4 py-2 text-xs flex items-center shadow-[0_0_10px_rgba(255,0,255,0.2)]"
            >
              <Activity className="w-4 h-4 mr-2" />
              SIMULATION_ACTIVE ({simulatedSkills.length})
            </motion.div>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 border-b border-gray-800">
        {TABS.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => { setActiveTab(tab.id); if (tab.id === 'roadmap' && !roadmap.length) loadRoadmap(); }}
              className={cn(
                "px-6 py-3 text-xs tracking-widest uppercase transition-all flex items-center gap-2 border-b-2",
                activeTab === tab.id
                  ? "border-neon-cyan text-neon-cyan bg-neon-cyan/5"
                  : "border-transparent text-gray-500 hover:text-gray-300"
              )}
            >
              <Icon className="w-3 h-3" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Main Ring Panel */}
            <div className="lg:col-span-2 cyber-panel p-8 flex justify-center items-center relative min-h-[350px]">
              <div className="cyber-brackets" />
              <div className="absolute top-6 left-6 border border-neon-cyan/30 p-2 text-neon-cyan/70 text-xs">
                [ CONF.LEVEL ]<br />
                <span className="text-neon-cyan text-lg text-glow-cyan">{data.prediction.confidence}</span>
              </div>
              <div className="absolute top-6 right-6 border border-neon-cyan/30 p-2 text-neon-cyan/70 text-xs text-right">
                [ CGPA ]<br />
                <span className="text-neon-cyan text-lg text-glow-cyan">{data.profile?.cgpa}</span>
              </div>
              <div className="absolute bottom-6 left-6 border border-neon-cyan/30 p-2 text-neon-cyan/70 text-xs">
                [ INTERNSHIPS ]<br />
                <span className="text-neon-cyan text-lg text-glow-cyan">{data.profile?.internships_count}</span>
              </div>
              <div className="absolute bottom-6 right-6 border border-neon-cyan/30 p-2 text-neon-cyan/70 text-xs text-right">
                [ PROJECTS ]<br />
                <span className="text-neon-cyan text-lg text-glow-cyan">{data.profile?.projects_count}</span>
              </div>

              {/* SVG Ring */}
              <div className="relative w-72 h-72 flex items-center justify-center">
                <svg className="absolute inset-0 w-full h-full animate-[spin_20s_linear_infinite] opacity-30" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="48" fill="none" stroke="#00f3ff" strokeWidth="0.5" strokeDasharray="4 4" />
                  <circle cx="50" cy="50" r="42" fill="none" stroke="#b537f2" strokeWidth="0.5" strokeDasharray="10 2" />
                </svg>
                <svg className="absolute inset-0 w-full h-full -rotate-90 pointer-events-none" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(0, 243, 255, 0.1)" strokeWidth="3" />
                  <motion.circle
                    cx="50" cy="50" r="45"
                    fill="none"
                    stroke="#00f3ff"
                    strokeWidth="4"
                    strokeDasharray="283"
                    initial={{ strokeDashoffset: 283 }}
                    animate={{ strokeDashoffset: dashOffset }}
                    transition={{ duration: 2, ease: "easeOut" }}
                    className="drop-shadow-[0_0_8px_rgba(0,243,255,0.8)]"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="w-36 h-36 rounded-full border border-neon-purple/50 flex items-center justify-center bg-neon-purple/5 shadow-[0_0_30px_rgba(181,55,242,0.2)]">
                  <div className="text-center">
                    <span className="block text-4xl font-bold text-white text-glow-cyan">{prob}%</span>
                    <span className="block text-[10px] text-neon-purple mt-1 tracking-widest">PLACEMENT_PROB</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats + Key Factors */}
            <div className="space-y-4 flex flex-col">
              {[
                { label: 'READINESS', value: `${data.skill_gap?.readiness_score ?? '--'}%`, color: 'neon-purple', icon: Activity },
                { label: 'COMPANY_MATCHES', value: `${data.companies?.length ?? 0}`, color: 'neon-pink', icon: Building2 },
                { label: 'SKILL_GAPS', value: `${data.skill_gap?.missing_skills?.length ?? 0}`, color: 'neon-cyan', icon: Target },
              ].map((s, i) => {
                const Icon = s.icon;
                return (
                  <motion.div
                    key={s.label}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 + 0.3 }}
                    className="cyber-panel p-4 flex-1 relative"
                  >
                    <div className="cyber-brackets" />
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-[10px] text-${s.color} tracking-widest`}>&gt; {s.label}</span>
                      <Icon className={`w-4 h-4 text-${s.color}`} />
                    </div>
                    <span className={`text-3xl font-bold text-${s.color} text-glow-cyan`}>{s.value}</span>
                  </motion.div>
                );
              })}
              {/* Probability Trend */}
              <div className="cyber-panel p-4 flex-1 relative">
                <div className="cyber-brackets" />
                <p className="text-[10px] text-gray-500 tracking-widest mb-1">&gt; 12W_PROBABILITY_PROJECTION</p>
                <div className="h-[90px] w-full mt-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                      <XAxis dataKey="week" stroke="#4b5563" fontSize={9} tickLine={false} axisLine={false} />
                      <YAxis stroke="#4b5563" fontSize={9} tickLine={false} axisLine={false} domain={['dataMin - 10', 100]} hide />
                      <RechartsTooltip 
                        contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid #00f3ff', borderRadius: '0' }}
                        itemStyle={{ color: '#00f3ff', fontSize: '10px' }}
                        labelStyle={{ color: '#9ca3af', fontSize: '10px' }}
                      />
                      <Line type="monotone" dataKey="probability" stroke="#00f3ff" strokeWidth={2} dot={{ r: 2, fill: '#00f3ff' }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
              {/* Key Factors */}
              <div className="cyber-panel p-4 flex-1 relative">
                <div className="cyber-brackets" />
                <p className="text-[10px] text-gray-500 tracking-widest mb-3">&gt; KEY_FACTORS</p>
                <div className="space-y-2">
                  {data.prediction.key_factors.length > 0 ? data.prediction.key_factors.map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs">
                      {f.includes('No ') || f.includes('below') ? (
                        <AlertTriangle className="w-3 h-3 text-neon-pink mt-0.5 shrink-0" />
                      ) : (
                        <CheckCircle className="w-3 h-3 text-neon-cyan mt-0.5 shrink-0" />
                      )}
                      <span className="text-gray-400">{f}</span>
                    </div>
                  )) : (
                    <p className="text-gray-600 text-xs">Profile looks balanced.</p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'companies' && (
          <motion.div
            key="companies"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {data.companies.length === 0 ? (
              <div className="col-span-3 cyber-panel p-8 text-center">
                <Lock className="w-8 h-8 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 text-xs">No company matches found. Improve your CGPA and skills.</p>
              </div>
            ) : data.companies.map((co, i) => (
              <motion.div
                key={co.name}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.08 }}
                className="cyber-panel p-5 relative group hover:border-neon-cyan/40 transition-all"
              >
                <div className="cyber-brackets" />
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ background: co.logo_color, boxShadow: `0 0 8px ${co.logo_color}` }} />
                    <span className="font-bold text-white tracking-wider">{co.name}</span>
                  </div>
                  <span className={cn(
                    "text-[9px] tracking-widest px-2 py-0.5 border",
                    co.tier === 'TIER_1' ? "text-neon-cyan border-neon-cyan/40 bg-neon-cyan/5" :
                    co.tier === 'TIER_2' ? "text-neon-purple border-neon-purple/40 bg-neon-purple/5" :
                    "text-gray-400 border-gray-600"
                  )}>{co.tier}</span>
                </div>
                <div className="mb-3">
                  <div className="flex justify-between text-[10px] mb-1">
                    <span className="text-gray-500">MATCH_SCORE</span>
                    <span className="text-neon-cyan font-bold">{co.match_score}%</span>
                  </div>
                  <div className="h-1 bg-gray-800 w-full">
                    <motion.div
                      className="h-full bg-gradient-to-r from-neon-cyan to-neon-purple"
                      initial={{ width: 0 }}
                      animate={{ width: `${co.match_score}%` }}
                      transition={{ duration: 1, delay: i * 0.08 }}
                      style={{ boxShadow: '0 0 6px rgba(0,243,255,0.5)' }}
                    />
                  </div>
                </div>
                <div className="space-y-1 text-xs">
                  <p className="text-gray-500">ROLES: <span className="text-gray-300">{co.roles.join(" | ")}</span></p>
                  <p className="text-gray-500">PKG: <span className="text-neon-purple">₹{co.package_lpa} LPA</span></p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {co.matched_skills.slice(0, 3).map(s => (
                      <span key={s} className="text-[9px] bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20 px-1.5 py-0.5">{s}</span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {activeTab === 'skills' && (
          <motion.div
            key="skills"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            {/* Summary + Strengths + Radar */}
            <div className="space-y-4">
              <div className="cyber-panel p-6 relative">
                <div className="cyber-brackets" />
                <h3 className="text-neon-cyan tracking-widest text-xs mb-4 border-b border-neon-cyan/20 pb-2">&gt; AI_ANALYSIS.SUMMARY</h3>
                <p className="text-gray-300 text-sm leading-relaxed">{data.skill_gap?.summary}</p>
                <div className="mt-4 flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-neon-cyan" />
                  <div>
                    <p className="text-[10px] text-gray-500">READINESS_SCORE</p>
                    <p className="text-2xl font-bold text-neon-cyan">{data.skill_gap?.readiness_score}%</p>
                  </div>
                </div>
              </div>
              
              <div className="cyber-panel p-6 relative h-[250px] flex flex-col justify-center">
                <div className="cyber-brackets" />
                <h3 className="text-neon-cyan tracking-widest text-xs mb-2 absolute top-4 left-6">&gt; SKILL_RADAR</h3>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="65%" data={radarData}>
                    <PolarGrid stroke="#1f2937" />
                    <PolarAngleAxis dataKey="subject" stroke="#9ca3af" fontSize={10} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="Candidate" dataKey="score" stroke="#b537f2" fill="#b537f2" fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="cyber-panel p-6 relative">
                <div className="cyber-brackets" />
                <h3 className="text-neon-purple tracking-widest text-xs mb-4 border-b border-neon-purple/20 pb-2">&gt; CURRENT.STRENGTHS</h3>
                <div className="flex flex-wrap gap-2">
                  {data.skill_gap?.strengths?.map(s => (
                    <span key={s} className="flex items-center gap-1 text-xs bg-neon-purple/10 text-neon-purple border border-neon-purple/20 px-3 py-1">
                      <CheckCircle className="w-3 h-3" /> {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Skill Gaps */}
            <div className="cyber-panel p-6 relative overflow-y-auto">
              <div className="cyber-brackets" />
              <h3 className="text-neon-pink tracking-widest text-xs mb-4 border-b border-neon-pink/20 pb-2">&gt; IDENTIFIED_GAPS</h3>
              <div className="space-y-4">
                {data.skill_gap?.skill_gaps?.map((gap, i) => (
                  <motion.div
                    key={gap.skill}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="border border-gray-800 p-4 hover:border-neon-pink/30 transition-all"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-white text-xs">{gap.skill}</span>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => runSimulation(gap.skill)}
                          disabled={isSimulating || simulatedSkills.includes(gap.skill)}
                          className="flex items-center gap-1 text-[9px] border border-neon-cyan/40 text-neon-cyan px-2 hover:bg-neon-cyan/10 disabled:opacity-50 transition-all font-bold tracking-wider"
                        >
                          {simulatedSkills.includes(gap.skill) ? "SIMULATED" : <><Plus className="w-2 h-2" /> SIMULATE</>}
                        </button>
                        <span className={cn(
                          "text-[9px] px-2 py-0.5 border flex items-center",
                          gap.priority === 'HIGH' ? "text-neon-pink border-neon-pink/40" : "text-neon-purple border-neon-purple/40"
                        )}>{gap.priority}</span>
                      </div>
                    </div>
                    <p className="text-gray-400 text-xs mb-2">{gap.reason}</p>
                    <div className="flex flex-wrap gap-1">
                      {gap.resources?.map(r => (
                        <span key={r} className="text-[9px] bg-gray-900 text-gray-400 border border-gray-700 px-2 py-0.5">
                          {r}
                        </span>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'roadmap' && (
          <motion.div
            key="roadmap"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex-1"
          >
            {roadmapLoading ? (
              <div className="flex items-center justify-center h-48">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 text-neon-cyan animate-spin mx-auto mb-3" />
                  <p className="text-neon-cyan text-xs tracking-widest animate-pulse">
                    GENERATING_ROADMAP_SEQUENCE...
                  </p>
                </div>
              </div>
            ) : roadmap.length === 0 ? (
              <div className="cyber-panel p-8 text-center">
                <Map className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-500 text-xs tracking-widest">ROADMAP NOT YET GENERATED</p>
                <button
                  onClick={loadRoadmap}
                  className="mt-4 border border-neon-cyan text-neon-cyan px-6 py-2 text-xs tracking-widest hover:bg-neon-cyan/10 transition-all"
                >
                  INIT_ROADMAP()
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 overflow-y-auto max-h-[600px] pr-1">
                {roadmap.map((week, i) => (
                  <motion.div
                    key={week.week}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="cyber-panel p-4 relative group hover:border-neon-cyan/30 transition-all"
                  >
                    <div className="cyber-brackets" />
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-xs font-bold text-neon-cyan border border-neon-cyan/40 px-2 py-0.5">
                        W{String(week.week).padStart(2, '0')}
                      </span>
                      <span className="text-xs font-bold text-white tracking-wide">{week.theme}</span>
                    </div>
                    <div className="space-y-1 mb-3">
                      {week.topics?.slice(0, 2).map((t: string) => (
                        <div key={t} className="flex items-center gap-1 text-[11px] text-gray-400">
                          <ChevronRight className="w-2.5 h-2.5 text-neon-purple shrink-0" />
                          {t}
                        </div>
                      ))}
                    </div>
                    <div className="flex items-start gap-1 text-[10px] text-neon-cyan/70 border-t border-gray-800 pt-2 mt-2">
                      <Clock className="w-3 h-3 mt-0.5 shrink-0" />
                      <span>{week.milestone}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
