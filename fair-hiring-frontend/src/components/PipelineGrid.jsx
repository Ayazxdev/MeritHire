import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

export default function PipelineGrid({ columns }) {
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  return (
    <div className="relative">
      <div className="flex gap-8 overflow-x-auto pb-12 no-scrollbar scroll-smooth snap-x">
        {columns.map((column) => (
          <div key={column.id} className="min-w-[320px] md:min-w-[380px] flex flex-col gap-6 snap-start">
            <div className="flex items-center justify-between border-b-4 border-black pb-4">
              <h3 className="font-montreal font-black text-xl uppercase tracking-tighter text-[#1c1c1c]">
                {column.title}
              </h3>
              <span className="font-grotesk text-[10px] font-black bg-black text-white px-2 py-1">
                {String(column.candidates.length).padStart(2, '0')}
              </span>
            </div>

            <div className="flex flex-col gap-6">
              {column.candidates.map((cand) => (
                <motion.div
                  key={cand.id}
                  layoutId={cand.id}
                  whileHover={{ y: -4, x: -2 }}
                  onClick={() => setSelectedCandidate(cand)}
                  className="relative group cursor-pointer"
                >
                  <div className="absolute inset-0 bg-black translate-x-1 translate-y-1 transition-transform group-hover:translate-x-2 group-hover:translate-y-2 opacity-10" />
                  <div className="relative bg-white border-2 border-black p-6 space-y-6 transition-all group-hover:shadow-[4px_4px_0px_#000]">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <label className="font-grotesk text-[9px] font-black opacity-30 uppercase tracking-widest block">IDENTIFIER</label>
                        <div className="font-montreal font-black text-sm text-black tracking-widest">
                          {cand.id}
                        </div>
                      </div>
                      <div className="text-right">
                        <label className="font-grotesk text-[9px] font-black opacity-30 uppercase tracking-widest block">SCORE</label>
                        <div className="font-montreal font-black text-2xl text-black">
                          {cand.confidence}%
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="h-1.5 w-full bg-black/5 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${cand.confidence}%` }}
                          className={`h-full ${cand.confidence > 80 ? 'bg-green-500' : cand.confidence > 50 ? 'bg-yellow-400' : 'bg-red-500'}`}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-black/5">
                      <div className="flex gap-2">
                        <span className="font-grotesk text-[8px] font-black border border-black/10 px-2 py-0.5 uppercase">
                          {cand.bias || 'VERIFIED'}
                        </span>
                      </div>
                      <div className="font-grotesk text-[9px] font-black text-black opacity-100 transition-opacity uppercase tracking-widest">
                        DETAILS →
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}

              {column.candidates.length === 0 && (
                <div className="py-20 border-2 border-dashed border-black/10 flex flex-col items-center justify-center opacity-20">
                  <div className="w-8 h-8 border-2 border-black rounded-full mb-4 opacity-20" />
                  <span className="font-grotesk text-[9px] uppercase tracking-[0.2em]">Void Stream</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* DETAIL MODAL */}
      <AnimatePresence>
        {selectedCandidate && (
          <div className="fixed inset-0 z-[300] flex items-center justify-center p-6 md:p-12">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedCandidate(null)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="relative w-full max-w-4xl bg-[#E6E6E3] border-4 border-black p-8 md:p-12 overflow-y-auto max-h-[90vh] shadow-[24px_24px_0px_rgba(0,0,0,0.2)]"
            >
              <div className="flex justify-between items-start mb-12">
                <div className="space-y-4">
                  <span className={`inline-block px-4 py-1.5 font-grotesk font-black text-[10px] tracking-[0.2em] uppercase ${selectedCandidate.confidence >= 60 ? 'bg-[#A7FF2E] text-black' : 'bg-[#FF4D4D] text-white'}`}>
                    {selectedCandidate.confidence >= 60 ? 'SELECTED' : 'REJECTED'}
                  </span>
                  <div className="space-y-1">
                    <h3 className="font-montreal font-black text-4xl uppercase tracking-tighter">{selectedCandidate.job_title}</h3>
                    <p className="font-inter text-sm font-bold opacity-60 uppercase">
                      {selectedCandidate.confidence >= 60 ? 'OFFER EXTENDED • VERIFIED BY FH-AGENT' : 'AUDIT COMPLETED'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedCandidate(null)}
                  className="font-grotesk font-black text-xs uppercase tracking-[0.3em] bg-black text-white px-6 py-3 hover:bg-white hover:text-black transition-all"
                >
                  [ CLOSE ]
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-1 gap-12">
                <div className="bg-white border-4 border-black p-8 space-y-8">
                  <div className="flex flex-col md:flex-row justify-between items-start gap-8 pb-8 border-b-2 border-black/5">
                    <div className="space-y-1">
                      <label className="font-grotesk text-[10px] font-black opacity-30 uppercase tracking-widest block mb-1">CANDIDATE ID</label>
                      <span className="font-montreal font-black text-2xl uppercase tracking-widest text-black">{selectedCandidate.id}</span>
                    </div>
                    <div className="text-right">
                      <label className="font-grotesk text-[10px] font-black opacity-30 uppercase tracking-widest block mb-2">FINAL SCORE</label>
                      <div className="font-montreal font-black text-5xl tracking-tighter">{selectedCandidate.confidence}<span className="text-sm opacity-50 ml-1">/100</span></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <div className="space-y-6">
                      <label className="font-grotesk text-[11px] font-black opacity-40 uppercase tracking-widest block">TECHNICAL REPERTOIRE</label>
                      <div className="flex flex-wrap gap-2 text-[10px] font-bold uppercase font-inter">
                        {(selectedCandidate.feedback?.matched_skills || ["GENERAL ARCHITECTURE", "SYSTEMS THINKING"]).map(s => (
                          <span key={s} className="border-2 border-black px-3 py-1 bg-black/5">{s}</span>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-6">
                      <label className="font-grotesk text-[11px] font-black opacity-40 uppercase tracking-widest block">MATCHING FEEDBACK</label>
                      <div className="bg-[#101218] p-6 text-white rounded-sm">
                        <p className="font-inter text-xs font-bold leading-relaxed uppercase tracking-tight opacity-80">
                          {selectedCandidate.feedback?.recommendation || "Evaluation completed with bias-neutral protocols."}
                        </p>
                      </div>
                    </div>
                  </div>

                  {selectedCandidate.confidence < 60 && (
                    <div className="pt-8 border-t-2 border-black/5">
                      <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.2em] text-[#FF4D4D] block mb-4">LACKING AREAS: DEVELOPMENTAL GAPS</label>
                      <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3 font-inter text-[11px] font-bold text-black/60 uppercase tracking-tight list-disc pl-5">
                        {(selectedCandidate.feedback?.missing_skills || ["System architecture evidence", "Direct technical verification"]).map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Scroll indicator for horizontal layout */}
      <div className="flex justify-center mt-12 gap-4">
        <div className="w-12 h-1 bg-black/10 rounded-full overflow-hidden">
          <motion.div
            animate={{ x: [-12, 12, -12] }}
            transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
            className="w-1/2 h-full bg-black/40"
          />
        </div>
      </div>
    </div>
  );
}
