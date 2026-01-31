import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GridPlus from './GridPlus';

const MOCK_QUEUE = [
    { id: 'A9F3X', role: 'Frontend Engineer', reason: 'Skill ambiguity', status: 'Pending' },
    { id: 'B2K8Z', role: 'Interface Architect', reason: 'GitHub-Resume mismatch', status: 'Pending' },
    { id: 'C7M1Y', role: 'Systems Lead', reason: 'Evidence lack', status: 'Pending' }
];

const MOCK_CANDIDATE_DATA = {
    A9F3X: {
        skills: ['React', 'JavaScript'],
        evidence: ['GitHub Projects', 'Resume Context'],
        agentInsights: [
            'GitHub signals inconsistent with resume',
            'Advanced React hooks usage verified in 2 repos',
            'Project "Fair-Hiring-Core" shows high structural integrity'
        ],
        biasRisk: 'Low'
    }
};

export default function ReviewerExperience({ onExit }) {
    const [queue, setQueue] = useState(MOCK_QUEUE);

  const companyId = localStorage.getItem("fhn_company_id") || "";

  useEffect(() => {
    if (!companyId) return;
    (async () => {
      try {
        const data = await api.reviewQueue(companyId);
        setQueue(Array.isArray(data) ? data : []);
      } catch (e) {
        console.warn("Failed to load review queue", e);
      }
    })();
  }, [companyId]);
    const [activePage, setActivePage] = useState('dashboard'); // 'dashboard', 'review'
    const [selectedCandidate, setSelectedCandidate] = useState(null);
    const [activeCandidateId, setActiveCandidateId] = useState(null);

    const pageTransition = {
        initial: { x: 20, opacity: 0 },
        animate: { x: 0, opacity: 1 },
        exit: { x: -20, opacity: 0 },
        transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] }
    };

    const handleReview = (candidate) => {
        const detailData = MOCK_CANDIDATE_DATA[candidate.id] || MOCK_CANDIDATE_DATA['A9F3X'];
        setSelectedCandidate({ ...detailData, id: candidate.id });
        setActiveCandidateId(candidate.id);
        setActivePage('review');
    };

    const handleDecision = async (id, decision) => {
    try {
      if (!companyId) throw new Error("Missing company id");
      const action = decision === "Blacklist" ? "blacklist" : "clear";
      await api.reviewAction(companyId, id, { action, note: "Reviewed via UI" });

      // Refresh queue after action
      const data = await api.reviewQueue(companyId);
      setQueue(Array.isArray(data) ? data : []);

      setSelectedCase(null);
      setDecisionModalOpen(false);
    } catch (e) {
      console.error(e);
      alert("Failed to submit decision. See console for details.");
    }
  };

    return (
        <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
            className="fixed inset-0 z-[160] bg-[#E6E6E3] text-[#1c1c1c] overflow-y-auto selection:bg-black selection:text-white custom-scrollbar-reviewer"
            style={{ willChange: 'transform' }}
            data-lenis-prevent
        >
            {/* STICKY HEADER */}
            <header className="sticky top-0 left-0 w-full bg-[#E6E6E3] border-b-[3px] border-[#1c1c1c] z-50 px-6 md:px-12 py-5 flex justify-between items-center bg-opacity-95 backdrop-blur-sm">
                <div className="flex items-center gap-6">
                    <button
                        onClick={onExit}
                        className="px-6 py-2.5 border-[2px] border-[#1c1c1c] font-grotesk text-[10px] font-black uppercase tracking-[0.2em] hover:bg-[#1c1c1c] hover:text-[#E6E6E3] transition-all flex items-center gap-2 group"
                    >
                        <span className="group-hover:-translate-x-1 transition-transform inline-block">←</span> EXIT
                    </button>
                    <div className="h-10 w-[2px] bg-[#1c1c1c]/10 hidden md:block"></div>
                    <span className="font-montreal font-black text-sm tracking-[0.2em] uppercase text-[#1c1c1c]">
                        REVIEW TERMINAL
                    </span>
                </div>
                <div className="font-grotesk text-[11px] font-black tracking-[0.1em] uppercase opacity-100 text-[#1c1c1c]">
                    AUTH: HUMAN_VERIFIER_09
                </div>
            </header>

            <main className="max-w-[1280px] mx-auto px-6 md:px-12 py-16 min-h-[90vh]">
                <AnimatePresence mode="wait">
                    {activePage === 'dashboard' && (
                        <motion.div key="dashboard" {...pageTransition} className="space-y-16">
                            <div className="space-y-4">
                                <h1 className="font-montreal font-black text-5xl md:text-8xl uppercase tracking-tighter leading-none">
                                    PENDING <br />QUEUE
                                </h1>
                                <p className="font-inter text-[11px] font-black opacity-40 uppercase tracking-[0.2em]">
                                    {queue.length} ANOMALIES ESCALATED FOR HUMAN VERIFICATION
                                </p>
                            </div>

                            <div className="grid grid-cols-1 gap-6">
                                {queue.map((item) => (
                                    <div
                                        key={item.id}
                                        className="group bg-white border-[2px] border-[#1c1c1c] p-8 flex flex-col md:flex-row md:items-center justify-between gap-8 hover:shadow-[12px_12px_0px_rgba(0,0,0,0.03)] transition-all duration-300 rounded-sm"
                                    >
                                        <div className="space-y-6">
                                            <div className="space-y-2">
                                                <div className="flex items-center gap-6">
                                                    <span className="font-montreal font-black text-2xl md:text-4xl uppercase tracking-tight text-[#1c1c1c]">{item.role}</span>
                                                    <span className="px-3 py-1 bg-[#1c1c1c] text-white border border-[#1c1c1c] text-[10px] font-grotesk font-black uppercase tracking-widest rounded-sm shadow-[2px_2px_0px_rgba(0,0,0,0.2)]">ROLE REF: {item.id}</span>
                                                </div>
                                                <div className="font-inter text-xs font-bold text-orange-700 uppercase tracking-widest flex items-center gap-2">
                                                    <span className="w-1.5 h-1.5 bg-orange-600 rounded-full animate-pulse" />
                                                    Issue: {item.reason}
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleReview(item)}
                                            className="px-10 py-5 bg-[#1c1c1c] text-white font-grotesk text-[11px] tracking-[0.3em] font-black uppercase hover:bg-black hover:scale-[1.02] transition-all flex items-center gap-3 group/btn"
                                        >
                                            RE-VALIDATE <span className="text-xl group-hover/btn:translate-x-1 transition-transform">→</span>
                                        </button>
                                    </div>
                                ))}

                                {queue.length === 0 && (
                                    <div className="py-24 text-center space-y-4">
                                        <div className="font-montreal font-black text-4xl opacity-20 italic">QUEUE DEPLETED</div>
                                        <p className="font-inter text-[10px] font-black uppercase tracking-widest opacity-40">All system anomalies have been verified.</p>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {activePage === 'review' && selectedCandidate && (
                        <motion.div key="review" {...pageTransition} className="space-y-16 pb-24">
                            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b-[2px] border-[#1c1c1c] pb-8">
                                <div className="space-y-3">
                                    <div className="flex items-center gap-4">
                                        <span className="font-grotesk text-[10px] uppercase font-black tracking-widest opacity-40">ACTIVE SESSION</span>
                                        <span className="w-2 h-2 bg-green-500 rounded-full" />
                                    </div>
                                    <h2 className="font-montreal font-black text-4xl md:text-6xl uppercase tracking-tighter leading-none">CANDIDATE: {selectedCandidate.id}</h2>
                                    <p className="font-inter text-[10px] font-black uppercase tracking-widest opacity-40">Identity Vault: LOCKED (System Policy)</p>
                                </div>
                                <button
                                    onClick={() => {
                                        setActivePage('dashboard');
                                        setSelectedCandidate(null);
                                        setActiveCandidateId(null);
                                    }}
                                    className="px-6 py-3 border-[2px] border-[#1c1c1c] font-grotesk text-[10px] font-black uppercase tracking-widest hover:bg-[#1c1c1c] hover:text-white transition-all"
                                >
                                    ABORT SESSION
                                </button>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                                {/* LEFT: EVIDENCE CLOUD */}
                                <div className="lg:col-span-5 space-y-12">
                                    <div className="space-y-6">
                                        <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] text-[#1c1c1c]/40">VERIFIED CAPABILITY</label>
                                        <div className="flex flex-wrap gap-2">
                                            {selectedCandidate.skills.map(skill => (
                                                <span key={skill} className="px-4 py-2 bg-white border-[2px] border-[#1c1c1c] font-grotesk text-[10px] font-black uppercase tracking-widest shadow-[4px_4px_0px_rgba(0,0,0,0.05)]">
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="p-8 bg-white border-[2px] border-[#1c1c1c] space-y-8 shadow-[8px_8px_0px_rgba(0,0,0,0.02)]">
                                        <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] text-[#1c1c1c]/40">RAW EVIDENCE CHANNELS</label>
                                        <div className="space-y-4">
                                            {selectedCandidate.evidence.map(item => (
                                                <div key={item} className="p-5 bg-[#F9F9F7] border border-[#1c1c1c]/10 flex items-center justify-between group cursor-pointer hover:border-[#1c1c1c] transition-all">
                                                    <span className="font-grotesk text-[11px] font-black uppercase tracking-widest text-[#1c1c1c]">{item}</span>
                                                    <span className="font-mono text-[9px] opacity-20 group-hover:opacity-60 transition-opacity">v2.0.4 AGENT</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* RIGHT: AGENT INTELLIGENCE */}
                                <div className="lg:col-span-7 space-y-12 bg-white border-[2px] border-[#1c1c1c] p-8 md:p-12 shadow-[12px_12px_0px_rgba(0,0,0,0.03)]">
                                    <div className="space-y-10">
                                        <div className="space-y-4">
                                            <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] text-orange-600">SYSTEM ANOMALY ANALYSIS</label>
                                            <div className="space-y-6">
                                                {selectedCandidate.agentInsights.map((insight, i) => (
                                                    <div key={i} className="flex gap-6 items-start">
                                                        <div className="w-1 h-6 bg-orange-600 shrink-0" />
                                                        <p className="font-inter text-base font-bold leading-relaxed text-[#1c1c1c]">
                                                            {insight}
                                                        </p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-8 pt-10 border-t-[2px] border-[#1c1c1c]/5">
                                            <div className="space-y-2">
                                                <label className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">BIAS NEUTRALITY</label>
                                                <div className="font-montreal font-black text-3xl uppercase text-green-700">99.8% SAFE</div>
                                            </div>
                                            <div className="space-y-2">
                                                <label className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">FAIRNESS HASH</label>
                                                <div className="font-mono text-[10px] font-black break-all opacity-60">0x7F2...91C</div>
                                            </div>
                                        </div>

                                        <div className="p-6 bg-[#1c1c1c] text-white space-y-3">
                                            <span className="font-grotesk text-[9px] font-black uppercase tracking-[0.3em] opacity-40">HUMAN PROTOCOL</span>
                                            <p className="font-inter text-xs leading-relaxed font-medium opacity-80">
                                                Infrastructure validation required. Confirm if the raw repository evidence matches the extracted skill metrics. Disregard performance ranking.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* DECISION TERMINAL - INTEGRATED FLOW */}
                            <div className="w-full flex flex-col md:flex-row gap-6 justify-center items-center py-12 border-t-[3px] border-[#1c1c1c] mt-20">
                                <button
                                    onClick={handleDecision}
                                    className="w-full md:w-auto px-16 py-6 bg-green-700 text-white font-grotesk font-black text-xs tracking-[0.4em] uppercase hover:bg-green-800 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[8px_8px_0px_rgba(0,0,0,0.1)]"
                                >
                                    CLEAR EVIDENCE
                                </button>
                                <button
                                    onClick={handleDecision}
                                    className="w-full md:w-auto px-16 py-6 bg-[#1c1c1c] text-white font-grotesk font-black text-xs tracking-[0.4em] uppercase hover:bg-black hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[8px_8px_0px_rgba(0,0,0,0.1)]"
                                >
                                    RE-ESCALATE
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

            <GridPlus className="fixed inset-0 pointer-events-none opacity-5 z-0" />
            <style>{`
                .custom-scrollbar-reviewer::-webkit-scrollbar { width: 6px; }
                .custom-scrollbar-reviewer::-webkit-scrollbar-thumb { background: #1c1c1c; border-radius: 10px; }
                .custom-scrollbar-reviewer::-webkit-scrollbar-track { background: rgba(0,0,0,0.05); }
            `}</style>
        </motion.div>
    );
}
