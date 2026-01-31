import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Cell,
  Tooltip,
} from "recharts";
import GridPlus from "./GridPlus";

import CandidateApply from "./CandidateApply";
import SkillTestPage from "../candidate/SkillTestPage";
import SkillPassport from "./SkillPassport";
import { api } from "../api/backend";

// Redundant Passport logic removed and moved to SkillPassport.jsx

export default function CandidateExperience({ onExit }) {
  const navigate = useNavigate();
  const [activePage, setActivePage] = useState("dashboard");
  const [selectedRoleForApply, setSelectedRoleForApply] = useState(null);

  const [jobs, setJobs] = useState([]);

  const [dashboardStats, setDashboardStats] = useState({
    skill_passport_status: "Not verified",
    active_applications: 0,
    feedback_count: 0,
    latest_update: "-",
  });
  const [applications, setApplications] = useState([]);
  const [jobsError, setJobsError] = useState("");

  const [statsVisible, setStatsVisible] = useState(false);

  // Candidate auth helpers
  const candidateAnonId = localStorage.getItem("fhn_candidate_anon_id") || "ANON-UNSET";

  const logoutCandidate = () => {
    localStorage.removeItem("fhn_role");
    localStorage.removeItem("fhn_candidate_anon_id");
    localStorage.removeItem("fhn_candidate_email");
    localStorage.removeItem("fhn_candidate_id");
    window.location.href = "/candidate";
  };

  useEffect(() => {
    setStatsVisible(true);
  }, []);


  useEffect(() => {
    const anon = candidateAnonId;
    if (!anon) return;

    (async () => {
      try {
        const s = await api.getCandidateStats(anon);
        setDashboardStats({
          skill_passport_status: s.skill_passport_status ?? "Not verified",
          active_applications: s.active_applications ?? 0,
          feedback_count: s.feedback_count ?? 0,
          latest_update: s.latest_update ?? "-",
        });
      } catch (e) {
        console.warn("Failed to load candidate stats", e);
      }

      try {
        const apps = await api.listCandidateApplications(anon);
        setApplications(Array.isArray(apps) ? apps : []);
      } catch (e) {
        console.warn("Failed to load candidate applications", e);
      }
    })();
  }, [candidateAnonId]);
  useEffect(() => {
    api
      .listPublishedJobs()
      .then(setJobs)
      .catch((e) => setJobsError(e.message || "Failed to load roles"));
  }, []);

  const pageTransition = {
    initial: { x: 20, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -20, opacity: 0 },
    transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] },
  };

  return (
    <motion.div
      initial={{ x: "100%" }}
      animate={{ x: 0 }}
      exit={{ x: "100%" }}
      transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
      className="fixed inset-0 z-[150] bg-[#E6E6E3] text-[#1c1c1c] overflow-y-auto selection:bg-black selection:text-white"
      style={{ willChange: "transform" }}
      data-lenis-prevent
    >
      {/* STICKY HEADER */}
      <header className="sticky top-0 left-0 w-full bg-[#E6E6E3] border-b-[3px] border-[#1c1c1c] z-50 px-6 md:px-12 py-6 flex justify-between items-center bg-opacity-95 backdrop-blur-sm">
        <div className="flex items-center gap-6">
          <button
            onClick={onExit}
            className="px-6 py-3 border-[2px] border-[#1c1c1c] font-grotesk text-[11px] font-black uppercase tracking-[0.2em] hover:bg-[#1c1c1c] hover:text-[#E6E6E3] transition-all flex items-center gap-2 group"
          >
            [ ESCAPE ]
          </button>
          <div className="h-10 w-[2px] bg-[#1c1c1c]/10 hidden md:block"></div>
          <span className="font-montreal font-black text-sm md:text-base tracking-[0.2em] uppercase text-[#1c1c1c]">
            CANDIDATE INTERFACE
          </span>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="font-grotesk text-[10px] font-black uppercase tracking-[0.25em] text-black/50">
            ID: <span className="text-black">{candidateAnonId}</span>
          </div>

          <button
            onClick={logoutCandidate}
            className="px-4 py-2 border-2 border-black/20 font-grotesk text-[10px] font-black uppercase tracking-[0.25em] hover:border-black hover:bg-black hover:text-white transition-all"
          >
            LOGOUT
          </button>
        </div>
      </header>

      <main className="max-w-[1280px] mx-auto px-6 md:px-12 py-12 min-h-[90vh]">
        <AnimatePresence mode="wait">
          {/* PAGE 1: DASHBOARD */}
          {activePage === "dashboard" && (
            <motion.div
              key="dashboard"
              {...pageTransition}
              className="space-y-16 md:space-y-24"
            >
              <div className="flex justify-between items-start">
                <h2 className="font-montreal font-black text-5xl md:text-8xl uppercase tracking-tighter">
                  CANDIDATE DASHBOARD
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-24">
                {[
                  { label: "SKILL PASSPORT", value: dashboardStats.skill_passport_status },
                  { label: "ACTIVE APPLICATIONS", value: String(dashboardStats.active_applications) },
                  { label: "LATEST UPDATE", value: `${dashboardStats.feedback_count} Feedback` },
                ].map((stat, i) => (
                  <div key={stat.label} className="space-y-4">
                    <label className="font-grotesk text-xs tracking-widest uppercase font-black text-black opacity-100">
                      {stat.label}
                    </label>
                    <div className="font-montreal font-black text-2xl uppercase text-[#1c1c1c]">
                      {stat.value}
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-12 border-t border-[#1c1c1c]/10 flex flex-wrap gap-8">
                <button
                  onClick={() => setActivePage("passport")}
                  className="px-10 py-5 bg-black text-white border border-black font-grotesk font-black text-[11px] tracking-[0.3em] uppercase transition-all shadow-[4px_4px_0px_#ccc] hover:bg-white hover:text-black hover:-translate-y-1 hover:shadow-[6px_6px_0px_#bbb] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
                >
                  VIEW SKILL PASSPORT
                </button>
                <button
                  onClick={() => setActivePage("roles")}
                  className="px-10 py-5 bg-black text-white border border-black font-grotesk font-black text-[11px] tracking-[0.3em] uppercase transition-all shadow-[4px_4px_0px_#ccc] hover:bg-white hover:text-black hover:-translate-y-1 hover:shadow-[6px_6px_0px_#bbb] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
                >
                  APPLY TO ROLES
                </button>
                <button
                  onClick={() => setActivePage("status")}
                  className="px-10 py-5 bg-black text-white border border-black font-grotesk font-black text-[11px] tracking-[0.3em] uppercase transition-all shadow-[4px_4px_0px_#ccc] hover:bg-white hover:text-black hover:-translate-y-1 hover:shadow-[6px_6px_0px_#bbb] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
                >
                  APPLICATION STATUS
                </button>
                <button
                  onClick={() => navigate("/candidate/interview")}
                  className="px-10 py-5 bg-black text-white border border-black font-grotesk font-black text-[11px] tracking-[0.3em] uppercase transition-all shadow-[4px_4px_0px_#ccc] hover:bg-white hover:text-black hover:-translate-y-1 hover:shadow-[6px_6px_0px_#bbb] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
                >
                  FAIR HIRING INTERVIEW
                </button>
              </div>
            </motion.div>
          )}

          {/* PAGE 2: SKILL PASSPORT */}
          {activePage === "passport" && (
            <SkillPassport
              onBack={() => setActivePage("dashboard")}
              candidateId={candidateAnonId}
            />
          )}

          {/* PAGE 3: ROLES LISTING */}
          {activePage === "roles" && (
            <motion.div
              key="roles"
              {...pageTransition}
              className="w-full space-y-24"
            >
              <div className="flex justify-between items-end">
                <div className="space-y-2">
                  <h2 className="font-montreal font-black text-6xl uppercase tracking-tighter leading-none">
                    AVAILABLE ROLES
                  </h2>
                  <p className="font-inter text-sm font-bold text-black opacity-70">
                    Direct matching based on your skill passport signatures.
                  </p>
                </div>
                <button
                  onClick={() => setActivePage("dashboard")}
                  className="bg-black text-white px-8 py-3 font-grotesk text-[10px] font-black uppercase tracking-[0.3em] hover:bg-black/90 transition-all shadow-[4px_4px_0px_#ccc] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
                >
                  BACK
                </button>
              </div>

              <div className="space-y-12">
                {jobsError && (
                  <div className="border-2 border-black bg-black text-white px-6 py-4 font-grotesk text-[10px] font-black uppercase tracking-[0.25em]">
                    ROLES LOAD ERROR: {jobsError} (showing mock roles)
                  </div>
                )}
                {(jobs.length
                  ? jobs.map((j) => ({
                    id: String(j.id),
                    title: j.title,
                    alignment: "—",
                    tags: ["FAIRHIRE"],
                    desc: j.description,
                    isNew: true,
                  }))
                  : [
                    {
                      id: "r1",
                      title: "Frontend Engineer",
                      alignment: "94%",
                      tags: ["React", "System Thinking"],
                      desc: "Develop core interface systems with high-fidelity interaction models.",
                    },
                    {
                      id: "r2",
                      title: "Interface Architect",
                      alignment: "82%",
                      tags: ["Three.js", "Motion Design"],
                      desc: "Build spatial computing interfaces and cinematic motion systems.",
                    },
                    {
                      id: "r3",
                      title: "Systems Lead",
                      alignment: "65%",
                      tags: ["Architecture", "Scaling"],
                      desc: "Architect distributed systems and low-latency infrastructure.",
                    },
                  ]
                ).map((role) => (
                  <div key={role.id} className="relative group">
                    <div className="absolute inset-0 bg-black translate-x-1 translate-y-1 transition-transform group-hover:translate-x-2 group-hover:translate-y-2" />
                    <div className="relative bg-white border-2 border-black p-5 md:p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 transition-transform group-hover:-translate-x-0.5 group-hover:-translate-y-0.5">
                      <div className="space-y-4 flex-1">
                        <div className="space-y-1">
                          <h3 className="font-montreal font-black text-xl md:text-2xl uppercase tracking-tighter leading-none text-black">
                            {role.title}{" "}
                            {role.isNew && (
                              <span className="text-[9px] bg-black text-white px-2 py-0.5 ml-2 align-top font-grotesk tracking-widest leading-none">
                                NEW
                              </span>
                            )}
                          </h3>
                          <p className="font-grotesk text-[9px] font-black uppercase tracking-[0.2em] text-black/40">
                            ALIGNMENT: {role.alignment}
                          </p>
                        </div>

                        <p className="font-inter text-[11px] font-bold leading-tight opacity-70 uppercase tracking-tight max-w-xl">
                          {role.desc ||
                            "Agent-verified role requiring specialized technical signatures."}
                        </p>

                        <div className="flex flex-wrap gap-2">
                          {role.tags.map((tag) => (
                            <span
                              key={tag}
                              className="font-grotesk text-[8px] font-black uppercase tracking-[0.1em] border-2 border-black/5 px-2 py-1 bg-[#f8f8f8]"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>

                      <button
                        onClick={() => {
                          setSelectedRoleForApply(role);
                          setActivePage("apply");
                        }}
                        className="bg-black text-white px-8 py-4 font-grotesk text-[10px] font-black uppercase tracking-[0.3em] hover:bg-black/90 transition-all whitespace-nowrap shadow-[0_5px_15px_rgba(0,0,0,0.1)] group-hover:shadow-[0_10px_25px_rgba(0,0,0,0.2)]"
                      >
                        APPLY NOW
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* PAGE: APPLY FLOW */}
          {activePage === "apply" && selectedRoleForApply && (
            <CandidateApply
              roleId={selectedRoleForApply.id}
              roleData={selectedRoleForApply}
              onExit={() => setActivePage("roles")}
              onTakeTest={() => setActivePage("test")}
              onComplete={() => setActivePage("status")}
            />
          )}

          {/* PAGE: SKILL TEST */}
          {activePage === "test" && selectedRoleForApply && (
            <SkillTestPage
              roleId={selectedRoleForApply.id}
              roleData={{
                role: selectedRoleForApply.title,
                level: "Mid",
                skills: selectedRoleForApply.tags || ["React", "JavaScript"],
                jobId: selectedRoleForApply.id,
              }}
              onExit={() => setActivePage("apply")}
              onComplete={(result) => {
                setActivePage("apply");
              }}
            />
          )}

          {/* PAGE 4: STATUS */}
          {activePage === "status" && (
            <motion.div
              key="status"
              {...pageTransition}
              className="max-w-5xl mx-auto space-y-16"
            >
              <div className="flex justify-between items-end border-b-4 border-black pb-8">
                <div className="space-y-2">
                  <label className="font-grotesk text-xs uppercase font-black tracking-widest text-black/50">
                    APPLICATION TRACKING
                  </label>
                  <h2 className="font-montreal font-black text-5xl md:text-7xl uppercase tracking-tighter">
                    YOUR STATUS
                  </h2>
                </div>
                <button
                  onClick={() => setActivePage("dashboard")}
                  className="bg-black text-white px-10 py-4 border border-black font-grotesk text-[11px] font-black uppercase tracking-[0.3em] hover:bg-white hover:text-black transition-all shadow-[6px_6px_0px_#ccc] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none mb-2"
                >
                  DASHBOARD
                </button>
              </div>

              <div className="grid grid-cols-1 gap-12">
                {applications.length === 0 && (
                  <div className="py-20 border-4 border-dashed border-black/10 flex flex-col items-center justify-center opacity-30">
                    <span className="font-grotesk text-sm uppercase tracking-[0.2em]">No applications found</span>
                  </div>
                )}

                {applications.map((app) => {
                  const isOngoing = ["pending", "processing", "verified", "test_required"].includes(app.status);
                  const isSelected = app.status === "matched" || app.status === "selected";
                  const isRejected = app.status === "rejected";
                  const score = app.match_score || 0;
                  const feedback = app.feedback || {};

                  if (isOngoing) {
                    return (
                      <div key={app.application_id} className="relative group/ongoing">
                        <div className="absolute inset-0 bg-yellow-400/20 translate-x-2 translate-y-2" />
                        <div className="relative bg-white border-4 border-black p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
                          <div className="space-y-4">
                            <span className="inline-block px-4 py-1.5 bg-yellow-400 text-black font-grotesk font-black text-[10px] tracking-[0.2em] uppercase">
                              ONGOING
                            </span>
                            <div className="space-y-1">
                              <h3 className="font-montreal font-black text-3xl uppercase tracking-tight">{app.job_title || "Technical Assessment"}</h3>
                              <p className="font-inter text-sm font-bold opacity-60 uppercase">ROLE: {app.job_title} • SUBMITTED {new Date(app.created_at).toLocaleDateString()}</p>
                            </div>
                            <p className="max-w-md font-inter text-xs font-bold leading-relaxed opacity-70 uppercase tracking-tight">
                              {app.status === "test_required"
                                ? "Action Required: Complete the technical signature verification to move to the bias-neutral review stage."
                                : "Your application is active. Our agents are currently evaluating your technical signatures."}
                            </p>
                          </div>
                          <button
                            onClick={() => {
                              setSelectedRoleForApply({ id: app.job_id, title: app.job_title });
                              setActivePage("test");
                            }}
                            className="px-8 py-5 bg-black text-white font-grotesk font-black text-xs tracking-[0.3em] uppercase hover:bg-yellow-400 hover:text-black transition-all shadow-[5px_5px_0px_#bbb] active:translate-y-1 active:shadow-none"
                          >
                            TAKE SKILL TEST
                          </button>
                        </div>
                      </div>
                    );
                  }

                  if (isSelected) {
                    return (
                      <div key={app.application_id} className="relative group/selected">
                        <div className="absolute inset-0 bg-green-500/20 translate-x-2 translate-y-2" />
                        <div className="relative bg-white border-4 border-black p-8">
                          <div className="flex flex-col md:flex-row justify-between items-start gap-8 mb-8 pb-8 border-b-2 border-black/5">
                            <div className="space-y-4">
                              <span className="inline-block px-4 py-1.5 bg-[#A7FF2E] text-black font-grotesk font-black text-[10px] tracking-[0.2em] uppercase">
                                SELECTED
                              </span>
                              <div className="space-y-1">
                                <h3 className="font-montreal font-black text-3xl uppercase tracking-tight">{app.job_title}</h3>
                                <p className="font-inter text-sm font-bold opacity-60 uppercase">OFFER EXTENDED • VERIFIED BY FH-AGENT-SHIELD</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <label className="font-grotesk text-[10px] font-black opacity-30 uppercase tracking-widest block mb-1">CANDIDATE ID</label>
                              <span className="font-montreal font-black text-xl uppercase tracking-widest text-black">{candidateAnonId}</span>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <div className="p-4 bg-black/5 rounded-sm border border-black/5">
                              <label className="font-grotesk text-[9px] font-black opacity-40 uppercase tracking-widest block mb-2">VERIFIED SKILLS</label>
                              <div className="flex flex-wrap gap-2 text-[10px] font-bold uppercase font-inter">
                                {(feedback.matched_skills || ["GENERAL ARCHITECTURE", "SYSTEMS THINKING"]).map(s => (
                                  <span key={s} className="border border-black/10 px-2 py-0.5">{s}</span>
                                ))}
                              </div>
                            </div>
                            <div className="p-4 bg-black/5 rounded-sm border border-black/5">
                              <label className="font-grotesk text-[9px] font-black opacity-40 uppercase tracking-widest block mb-2">STRENGTHS</label>
                              <div className="space-y-1 text-[11px] font-black uppercase font-montreal tracking-tight">
                                <div className="text-green-600">Technical Depth Verified</div>
                                <div className="text-green-600">Bias Safety Passed</div>
                              </div>
                            </div>
                            <div className="p-4 bg-black text-white rounded-sm border border-black">
                              <label className="font-grotesk text-[9px] font-black opacity-40 uppercase tracking-widest block mb-2">FINAL SCORE</label>
                              <div className="font-montreal font-black text-4xl tracking-tighter">{score}<span className="text-sm opacity-50 ml-1">/100</span></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  }

                  if (isRejected) {
                    return (
                      <div key={app.application_id} className="relative group/rejected">
                        <div className="absolute inset-0 bg-red-500/20 translate-x-2 translate-y-2" />
                        <div className="relative bg-white border-4 border-black p-8 flex flex-col md:flex-row justify-between items-start gap-8">
                          <div className="space-y-6 flex-1">
                            <div className="space-y-4">
                              <span className="inline-block px-4 py-1.5 bg-[#FF4D4D] text-white font-grotesk font-black text-[10px] tracking-[0.2em] uppercase">
                                REJECTED
                              </span>
                              <div className="space-y-1">
                                <h3 className="font-montreal font-black text-3xl uppercase tracking-tight">{app.job_title}</h3>
                                <p className="font-inter text-sm font-bold opacity-60 uppercase">AUDIT COMPLETED {new Date(app.created_at).toLocaleDateString()}</p>
                              </div>
                            </div>

                            <div className="bg-[#101218] p-6 text-white space-y-4">
                              <div className="flex items-center gap-3">
                                <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.2em] text-[#FF4D4D]">DEVELOPMENTAL FEEDBACK</label>
                                <div className="h-[1px] flex-1 bg-white/10" />
                              </div>
                              <div className="space-y-4">
                                <div className="space-y-2">
                                  <h4 className="font-montreal font-bold text-sm uppercase text-white/90">Lacking Areas:</h4>
                                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 font-inter text-[11px] font-bold text-white/50 uppercase tracking-tight list-disc pl-4">
                                    {(feedback.missing_skills || ["System architecture evidence", "Direct technical verification"]).map((s, i) => (
                                      <li key={i}>{s}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  }

                  return null;
                })}
              </div>
            </motion.div>
          )}

          {/* PAGE 5: FEEDBACK */}
          {activePage === "feedback" && (
            <motion.div
              key="feedback"
              {...pageTransition}
              className="max-w-5xl mx-auto space-y-16"
            >
              <div className="flex justify-between items-end border-b-4 border-black pb-8">
                <div className="space-y-2">
                  <label className="font-grotesk text-xs uppercase font-black tracking-widest text-[#FF4D4D]">
                    DECISION: POSTPONED
                  </label>
                  <h2 className="font-montreal font-black text-5xl md:text-7xl uppercase tracking-tighter">
                    Growth Insights
                  </h2>
                </div>
                <button
                  onClick={() => setActivePage("status")}
                  className="bg-black text-white px-10 py-4 border border-black font-grotesk text-[11px] font-black uppercase tracking-[0.3em] hover:bg-white hover:text-black transition-all shadow-[6px_6px_0px_#ccc] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none mb-2"
                >
                  BACK
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
                <div className="lg:col-span-7 space-y-12">
                  <div className="bg-[#101218] p-8 shadow-[12px_12px_0px_#ccc] border border-white/5">
                    <div className="flex justify-between items-baseline mb-12 border-b border-white/10 pb-4">
                      <h3 className="font-grotesk text-sm font-black uppercase tracking-widest text-white flex items-center gap-3">
                        <span className="w-2 h-2 bg-[#A7FF2E] rounded-full animate-pulse" />
                        Skill Benchmark
                      </h3>
                      <span className="text-[10px] font-black uppercase text-white/40">
                        You vs. Selected Candidates
                      </span>
                    </div>

                    <div className="h-[300px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={[
                            { skill: "REACT", user: 82, avg: 88 },
                            { skill: "SYS DESIGN", user: 64, avg: 85 },
                            { skill: "TYPESCRIPT", user: 78, avg: 90 },
                            { skill: "INTERFACES", user: 92, avg: 84 },
                          ]}
                        >
                          <XAxis
                            dataKey="skill"
                            stroke="#fff"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            tick={{ fontWeight: 900, opacity: 0.5 }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#0B0D11",
                              border: "2px solid #333",
                              borderRadius: "0",
                              padding: "12px",
                            }}
                            itemStyle={{
                              fontSize: "10px",
                              fontWeight: 900,
                              textTransform: "uppercase",
                              color: "#fff",
                            }}
                            labelStyle={{
                              fontSize: "11px",
                              fontWeight: 900,
                              marginBottom: "8px",
                              color: "#00E5FF",
                              borderBottom: "1px solid #333",
                              paddingBottom: "4px",
                              textTransform: "uppercase",
                            }}
                            cursor={{ fill: "rgba(255,255,255,0.05)" }}
                          />
                          <Bar
                            dataKey="user"
                            radius={[2, 2, 0, 0]}
                            name="YOUR SCORE"
                          >
                            {[
                              { skill: "REACT", user: 82, avg: 88 },
                              { skill: "SYS DESIGN", user: 64, avg: 85 },
                              { skill: "TYPESCRIPT", user: 78, avg: 90 },
                              { skill: "INTERFACES", user: 92, avg: 84 },
                            ].map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={
                                  entry.user >= entry.avg
                                    ? "#A7FF2E"
                                    : "#00E5FF"
                                }
                              />
                            ))}
                          </Bar>
                          <Bar
                            dataKey="avg"
                            fill="#1A1F26"
                            stroke="#ffffff33"
                            strokeWidth={1}
                            radius={[2, 2, 0, 0]}
                            name="TARGET LEVEL"
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="mt-8 flex gap-8 justify-center">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-[#00E5FF]" />
                        <span className="font-grotesk text-[10px] font-black text-white/60">
                          YOUR SIGNATURE
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-[#1A1F26] border border-white/20" />
                        <span className="font-grotesk text-[10px] font-black text-white/60">
                          ROLE BENCHMARK
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="p-8 border-4 border-black space-y-8 bg-white">
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-black rotate-45" />
                        <label className="font-grotesk text-xs font-black uppercase text-black tracking-widest">
                          WHY THIS DATA MATTERS
                        </label>
                      </div>
                      <p className="font-inter text-sm font-bold text-black opacity-60 leading-relaxed uppercase tracking-tight">
                        Our system evaluates your technical signatures globally.
                        The gaps below represent direct differences between your
                        verified evidence and the hiring team's specific
                        requirements.
                      </p>
                    </div>
                  </div>
                </div>

                {/* RIGHT: SPECIFIC GAPS & PLAN */}
                <div className="lg:col-span-5 space-y-12">
                  <section className="space-y-8">
                    <div className="space-y-6">
                      <div className="pb-2 border-b-2 border-black inline-block">
                        <label className="font-grotesk text-[11px] font-black uppercase text-black tracking-widest">
                          GAPS DETECTED
                        </label>
                      </div>
                      <div className="space-y-6">
                        {[
                          {
                            title: "SYSTEM DESIGN DEPTH",
                            desc: "Evidence channel showed architectural gaps in distributed states. Prioritized for Lead levels.",
                          },
                          {
                            title: "ADVANCED TYPESCRIPT",
                            desc: "Utility patterns like conditional types and mapped types were not strongly verified in output.",
                          },
                        ].map((gap) => (
                          <div key={gap.title} className="space-y-2 group">
                            <h4 className="font-montreal font-black text-lg uppercase tracking-tight group-hover:text-[#FF4D4D] transition-colors">
                              {gap.title}
                            </h4>
                            <p className="font-inter text-xs font-bold leading-relaxed opacity-60 uppercase tracking-tight">
                              {gap.desc}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div className="pb-2 border-b-2 border-black inline-block">
                        <label className="font-grotesk text-[11px] font-black uppercase text-black tracking-widest">
                          HOW TO IMPROVE
                        </label>
                      </div>
                      <div className="space-y-6">
                        {[
                          {
                            title: "PRODUCTION-SCALE PROJECT",
                            desc: "Add a project specifically focusing on distributed state synchronization.",
                          },
                          {
                            title: "RE-VERIFICATION",
                            desc: "Attempt the System Design verification challenge again after 30 days.",
                          },
                        ].map((tip) => (
                          <div key={tip.title} className="space-y-2">
                            <h4 className="font-montreal font-black text-lg uppercase tracking-tight">
                              {tip.title}
                            </h4>
                            <p className="font-inter text-xs font-bold leading-relaxed opacity-60 uppercase tracking-tight">
                              {tip.desc}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </section>

                  <div className="pt-12 border-t border-black/10">
                    <button
                      onClick={() => setActivePage("dashboard")}
                      className="w-full py-6 bg-black text-white font-grotesk font-black text-xs tracking-[0.3em] uppercase transition-all shadow-[6px_6px_0px_#ccc] hover:bg-white hover:text-black hover:-translate-y-1 active:shadow-none"
                    >
                      RETURN TO DASHBOARD
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="max-w-[1280px] mx-auto px-6 md:px-12 py-12 border-t border-[#1c1c1c]/10 text-center md:text-left">
        <div className="font-grotesk text-xs tracking-widest uppercase font-black text-[#1c1c1c]">
          POWERED BY FAIR HIRING NETWORK
        </div>
      </footer>

      <GridPlus className="fixed inset-0 pointer-events-none opacity-5 z-0" />
      <style>{`
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>

      {/* SKILL DETAIL MODAL REMOVED (Handled inside SkillPassport) */}
    </motion.div>
  );
}
