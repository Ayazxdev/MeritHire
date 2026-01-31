import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { api } from '../api/backend';

export default function CandidateApply({ roleId, roleData: propRoleData, onExit, onComplete }) {
    const [step, setStep] = useState('form');
    const [formData, setFormData] = useState({
        resumeFile: null,
        github: '',
        leetcode: '',
        codeforces: '',
        linkedinFile: null
    });
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [toggles, setToggles] = useState({
        leetcode: false,
        codeforces: false,
        linkedin: false
    });

    // Mock role data
    const roleData = {
        title: propRoleData?.title || 'Frontend Engineer',
        skills: propRoleData?.tags || ['React', 'JavaScript', 'System Thinking']
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validation
        if (!formData.resumeFile) {
            setError("Resume is required");
            return;
        }
        
        if (!formData.github || formData.github.trim() === '') {
            setError("GitHub username/URL is required");
            return;
        }
        
        setStep('submitting');
        setError(null);

        const anonId = localStorage.getItem("fhn_candidate_anon_id");
        if (!anonId) {
            setError("You are not logged in. Please login again.");
            setStep('error');
            return;
        }

        // Create FormData for file upload
        const formDataToSend = new FormData();
        formDataToSend.append('job_id', roleId);
        formDataToSend.append('anon_id', anonId);
        formDataToSend.append('resume', formData.resumeFile);
        
        if (formData.github) {
            formDataToSend.append('github', formData.github);
        }
        
        if (formData.leetcode && toggles.leetcode) {
            formDataToSend.append('leetcode', formData.leetcode);
        }
        
        if (formData.codeforces && toggles.codeforces) {
            formDataToSend.append('codeforces', formData.codeforces);
        }
        
        if (formData.linkedinFile && toggles.linkedin) {
            formDataToSend.append('linkedin_pdf', formData.linkedinFile);
        }

        try {
            // Call backend with FormData
            const resp = await api.applyToJobWithFiles(formDataToSend);
            
            if (resp.application_id) {
                setStep('success');
                
                // Redirect to status page after delay
                setTimeout(() => {
                    if (onComplete) {
                        onComplete(resp.application_id);
                    }
                }, 1500);
            } else {
                throw new Error("Application submission failed");
            }
            
        } catch (err) {
            console.error(err);
            setError(err?.message || "Application failed. Please try again.");
            setStep('error');
        }
    };

    const handleResumeChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate PDF
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                setError("Resume must be a PDF file");
                return;
            }
            
            setUploading(true);
            // Simulate upload delay
            setTimeout(() => {
                setFormData({ ...formData, resumeFile: file });
                setUploading(false);
                setError(null);
            }, 800);
        }
    };

    const handleLinkedInChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate PDF
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                setError("LinkedIn profile must be a PDF file");
                return;
            }
            
            setFormData({ ...formData, linkedinFile: file });
            setError(null);
        }
    };

    return createPortal(
        <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
            className="fixed inset-0 z-[200] bg-[#E6E6E3] text-[#1c1c1c] overflow-y-auto selection:bg-black selection:text-white"
            style={{ isolation: 'isolate' }}
            data-lenis-prevent
        >
            {/* STICKY HEADER */}
            <header className="sticky top-0 left-0 w-full bg-[#E6E6E3] border-b-[3px] border-[#1c1c1c] z-[100] px-6 md:px-12 py-6 flex justify-between items-center bg-opacity-95 backdrop-blur-sm">
                <div className="flex items-center gap-6">
                    <button
                        onClick={onExit}
                        className="px-6 py-3 border-[2px] border-[#1c1c1c] font-grotesk text-[11px] font-black uppercase tracking-[0.2em] hover:bg-[#1c1c1c] hover:text-[#E6E6E3] transition-all flex items-center gap-2 group"
                    >
                        <span className="group-hover:-translate-x-1 transition-transform inline-block">←</span> [ ESCAPE ]
                    </button>
                    <div className="h-10 w-[2px] bg-[#1c1c1c]/10 hidden md:block"></div>
                    <span className="font-montreal font-black text-sm md:text-base tracking-[0.2em] uppercase text-[#1c1c1c]">
                        APPLICATION INTERFACE
                    </span>
                </div>
                <div className="font-grotesk text-[10px] font-black tracking-widest uppercase opacity-40">
                    ID: {roleId?.toString().slice(0, 8) || 'REF-882'}
                </div>
            </header>

            <main className="max-w-[1440px] mx-auto px-6 md:px-12 pt-0 pb-20 min-h-screen">
                <AnimatePresence mode="wait">
                    {step === 'form' ? (
                        <motion.div
                            key="apply-form"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="space-y-16 relative"
                        >
                            {/* HERO SECTION */}
                            <section className="space-y-6 pb-12 border-b border-black/10 pt-16">
                                <div className="space-y-4">
                                    <h1 className="font-montreal font-bold text-6xl md:text-8xl uppercase tracking-tighter leading-[0.9]">
                                        Apply for<br />{roleData.title}
                                    </h1>
                                    <p className="font-inter text-xs uppercase tracking-widest opacity-60">
                                        Bias-free evaluation · Skill-first matching
                                    </p>
                                </div>
                            </section>

                            {/* ERROR MESSAGE */}
                            {error && (
                                <div className="bg-red-100 border-2 border-red-600 p-6">
                                    <p className="font-grotesk text-sm font-black uppercase text-red-600">
                                        {error}
                                    </p>
                                </div>
                            )}

                            <form onSubmit={handleSubmit}>
                                <div className="space-y-16">
                                    {/* MANDATORY SIGNALS */}
                                    <section className="space-y-8">
                                        <h2 className="font-grotesk text-base font-black uppercase tracking-[0.3em]">
                                            MANDATORY SIGNALS
                                        </h2>

                                        {/* Resume Upload */}
                                        <div className="space-y-4">
                                            <div className="flex items-center gap-4">
                                                <span className="font-montreal font-black text-5xl opacity-10">01.</span>
                                                <div>
                                                    <h3 className="font-grotesk text-sm font-black uppercase tracking-widest">
                                                        RESUME (PDF ONLY)
                                                        <span className="text-red-600 ml-2">REQUIRED</span>
                                                    </h3>
                                                </div>
                                            </div>
                                            <div className="relative group">
                                                <input
                                                    type="file"
                                                    accept=".pdf"
                                                    onChange={handleResumeChange}
                                                    className="absolute inset-0 opacity-0 cursor-pointer z-20"
                                                    required
                                                />
                                                <div className={`h-64 border-4 border-black ${formData.resumeFile ? 'bg-black text-[#E6E6E3]' : 'bg-transparent hover:bg-black/5'} transition-all flex flex-col items-center justify-center p-8 text-center gap-4 relative z-10`}>
                                                    {uploading ? (
                                                        <div className="font-grotesk text-lg font-black uppercase tracking-[0.2em]">
                                                            UPLOADING...
                                                        </div>
                                                    ) : formData.resumeFile ? (
                                                        <div className="space-y-2">
                                                            <div className="font-grotesk text-lg font-black uppercase tracking-[0.2em]">
                                                                ✓ {formData.resumeFile.name}
                                                            </div>
                                                            <div className="font-inter text-[10px] font-black uppercase opacity-60">
                                                                {(formData.resumeFile.size / 1024 / 1024).toFixed(2)} MB
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <>
                                                            <div className="font-grotesk text-lg font-black uppercase tracking-[0.2em]">
                                                                + SELECT PDF FILE
                                                            </div>
                                                            <div className="font-inter text-[10px] font-black uppercase opacity-40">
                                                                Drag PDF here or click to browse
                                                            </div>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        {/* GitHub Username */}
                                        <div className="space-y-4">
                                            <div className="flex items-center gap-4">
                                                <span className="font-montreal font-black text-5xl opacity-10">02.</span>
                                                <div>
                                                    <h3 className="font-grotesk text-sm font-black uppercase tracking-widest">
                                                        GITHUB USERNAME
                                                        <span className="text-red-600 ml-2">REQUIRED</span>
                                                    </h3>
                                                    <p className="font-inter text-[10px] font-black uppercase opacity-60 mt-1">
                                                        Our agents will audit your repositories
                                                    </p>
                                                </div>
                                            </div>
                                            <input
                                                type="text"
                                                placeholder="USERNAME OR URL"
                                                value={formData.github}
                                                onChange={(e) => setFormData({ ...formData, github: e.target.value })}
                                                className="w-full bg-transparent border-b-4 border-black py-6 font-montreal text-3xl uppercase tracking-tight focus:outline-none placeholder:text-black/20 font-bold"
                                                required
                                            />
                                        </div>
                                    </section>

                                    {/* PROTOCOL INFO */}
                                    <section className="bg-black text-[#E6E6E3] p-8 space-y-4">
                                        <h3 className="font-grotesk text-xs font-black uppercase tracking-[0.3em]">
                                            EVALUATION PROTOCOL
                                        </h3>
                                        <ul className="space-y-2 font-inter text-[11px] font-bold uppercase opacity-80">
                                            <li>&gt;Primary focus on real project work</li>
                                            <li>&gt;Bias masking applied to all identifiers</li>
                                            <li>&gt;Direct matching with team requirements</li>
                                            <li>&gt;Zero-tolerance for bot-generated resumes</li>
                                        </ul>
                                    </section>

                                    {/* OPTIONAL SIGNALS */}
                                    <section className="space-y-8">
                                        <div className="flex items-center justify-between">
                                            <h2 className="font-grotesk text-base font-black uppercase tracking-[0.3em]">
                                                OPTIONAL EXTRA SIGNALS
                                            </h2>
                                            <span className="font-inter text-[10px] font-black uppercase opacity-40">
                                                SELECT TO ENABLE
                                            </span>
                                        </div>

                                        <div className="space-y-6">
                                            {/* LeetCode Toggle */}
                                            <div className="space-y-4">
                                                <button
                                                    type="button"
                                                    onClick={() => setToggles(t => ({ ...t, leetcode: !t.leetcode }))}
                                                    className={`w-full flex justify-between items-center p-5 border-2 transition-all ${toggles.leetcode ? 'bg-black text-white border-black' : 'border-black/10 hover:border-black'}`}
                                                >
                                                    <span className="font-grotesk font-black text-xs uppercase tracking-widest">LEETCODE PROFILE</span>
                                                    <span className="font-montreal font-black text-xl">{toggles.leetcode ? '-' : '+'}</span>
                                                </button>
                                                <AnimatePresence>
                                                    {toggles.leetcode && (
                                                        <motion.div
                                                            initial={{ height: 0, opacity: 0 }}
                                                            animate={{ height: 'auto', opacity: 1 }}
                                                            exit={{ height: 0, opacity: 0 }}
                                                            className="overflow-hidden"
                                                        >
                                                            <div className="py-4">
                                                                <input
                                                                    type="text"
                                                                    placeholder="PROFILE URL"
                                                                    value={formData.leetcode}
                                                                    onChange={(e) => setFormData({ ...formData, leetcode: e.target.value })}
                                                                    className="w-full bg-transparent border-b-2 border-black py-4 font-montreal text-2xl uppercase tracking-tight focus:outline-none placeholder:text-black/10 font-bold"
                                                                />
                                                            </div>
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </div>

                                            {/* Codeforces Toggle */}
                                            <div className="space-y-4">
                                                <button
                                                    type="button"
                                                    onClick={() => setToggles(t => ({ ...t, codeforces: !t.codeforces }))}
                                                    className={`w-full flex justify-between items-center p-5 border-2 transition-all ${toggles.codeforces ? 'bg-black text-white border-black' : 'border-black/10 hover:border-black'}`}
                                                >
                                                    <span className="font-grotesk font-black text-xs uppercase tracking-widest">CODEFORCES ID</span>
                                                    <span className="font-montreal font-black text-xl">{toggles.codeforces ? '-' : '+'}</span>
                                                </button>
                                                <AnimatePresence>
                                                    {toggles.codeforces && (
                                                        <motion.div
                                                            initial={{ height: 0, opacity: 0 }}
                                                            animate={{ height: 'auto', opacity: 1 }}
                                                            exit={{ height: 0, opacity: 0 }}
                                                            className="overflow-hidden"
                                                        >
                                                            <div className="py-4">
                                                                <input
                                                                    type="text"
                                                                    placeholder="HANDLE"
                                                                    value={formData.codeforces}
                                                                    onChange={(e) => setFormData({ ...formData, codeforces: e.target.value })}
                                                                    className="w-full bg-transparent border-b-2 border-black py-4 font-montreal text-2xl uppercase tracking-tight focus:outline-none placeholder:text-black/10 font-bold"
                                                                />
                                                            </div>
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </div>

                                            {/* LinkedIn Toggle */}
                                            <div className="space-y-4">
                                                <button
                                                    type="button"
                                                    onClick={() => setToggles(t => ({ ...t, linkedin: !t.linkedin }))}
                                                    className={`w-full flex justify-between items-center p-5 border-2 transition-all ${toggles.linkedin ? 'bg-black text-white border-black' : 'border-black/10 hover:border-black'}`}
                                                >
                                                    <span className="font-grotesk font-black text-xs uppercase tracking-widest">LINKEDIN PROFILE</span>
                                                    <span className="font-montreal font-black text-xl">{toggles.linkedin ? '-' : '+'}</span>
                                                </button>
                                                <AnimatePresence>
                                                    {toggles.linkedin && (
                                                        <motion.div
                                                            initial={{ height: 0, opacity: 0 }}
                                                            animate={{ height: 'auto', opacity: 1 }}
                                                            exit={{ height: 0, opacity: 0 }}
                                                            className="overflow-hidden"
                                                        >
                                                            <div className="py-4 space-y-4">
                                                                <div className="relative group">
                                                                    <input
                                                                        type="file"
                                                                        accept=".pdf"
                                                                        onChange={handleLinkedInChange}
                                                                        className="absolute inset-0 opacity-0 cursor-pointer z-20"
                                                                    />
                                                                    <div className={`h-48 border-4 border-black ${formData.linkedinFile ? 'bg-black text-[#E6E6E3]' : 'bg-transparent hover:bg-black/10'} transition-all flex flex-col items-center justify-center p-8 text-center gap-4 relative z-10`}>
                                                                        <div className="font-grotesk text-sm font-black uppercase tracking-[0.2em]">
                                                                            {formData.linkedinFile ? `FILE: ${formData.linkedinFile.name}` : '+ SELECT LINKEDIN PDF'}
                                                                        </div>
                                                                        {!formData.linkedinFile && (
                                                                            <div className="font-inter text-[10px] font-black uppercase opacity-40">
                                                                                Save your LinkedIn profile as PDF and upload
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </div>
                                        </div>
                                    </section>

                                    {/* SUBMIT BUTTON */}
                                    <div className="mt-24 pt-12 border-t-8 border-black flex justify-center">
                                        <button
                                            type="submit"
                                            disabled={uploading}
                                            className="w-full md:max-w-xl py-8 bg-black text-white border border-black font-grotesk font-black text-xl tracking-[0.4em] uppercase hover:bg-white hover:text-black transition-all shadow-[6px_6px_0px_#ccc] active:translate-x-[3px] active:translate-y-[3px] active:shadow-none disabled:opacity-50 disabled:cursor-not-allowed mb-24"
                                        >
                                            PUSH APPLICATION
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </motion.div>
                    ) : step === 'submitting' ? (
                        <motion.div
                            key="submitting-state"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="h-[60vh] flex flex-col items-center justify-center space-y-12 text-center"
                        >
                            <div className="relative">
                                <motion.div
                                    className="w-24 h-24 border border-black/5 rounded-full"
                                    animate={{ scale: [1, 1.1, 1], opacity: [0.1, 0.2, 0.1] }}
                                    transition={{ repeat: Infinity, duration: 2 }}
                                />
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="w-2 h-2 bg-black rounded-full animate-pulse" />
                                </div>
                            </div>
                            <div className="space-y-4">
                                <h2 className="font-montreal font-bold text-3xl uppercase tracking-tighter">
                                    VERIFYING SIGNALS
                                </h2>
                                <p className="font-inter text-xs opacity-40 uppercase tracking-widest">
                                    Our agents are processing your application...
                                </p>
                            </div>
                        </motion.div>
                    ) : step === 'success' ? (
                        <motion.div
                            key="success-state"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="h-[60vh] flex flex-col items-center justify-center space-y-12 text-center"
                        >
                            <div className="text-6xl">✓</div>
                            <div className="space-y-4">
                                <h2 className="font-montreal font-bold text-3xl uppercase tracking-tighter">
                                    SUCCESSFULLY APPLIED
                                </h2>
                                <p className="font-inter text-xs opacity-40 uppercase tracking-widest">
                                    Redirecting to status dashboard...
                                </p>
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="error-state"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="h-[60vh] flex flex-col items-center justify-center space-y-12 text-center"
                        >
                            <div className="text-6xl text-red-600">✕</div>
                            <div className="space-y-4">
                                <h2 className="font-montreal font-bold text-3xl uppercase tracking-tighter text-red-600">
                                    APPLICATION FAILED
                                </h2>
                                <p className="font-inter text-xs opacity-60 uppercase tracking-widest">
                                    {error}
                                </p>
                                <button
                                    onClick={() => setStep('form')}
                                    className="mt-8 px-8 py-4 bg-black text-white font-grotesk text-sm font-black uppercase tracking-widest hover:bg-black/80"
                                >
                                    TRY AGAIN
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

            <style>{`
                input::placeholder { opacity: 0.2; color: black; }
            `}</style>
        </motion.div>,
        document.body
    );
}
