/**
 * PetReel Studio — Ferric Memory UI
 * Design philosophy: the darkroom aesthetic applied to a professional AI video studio.
 * Amber on iron-black. Contact-sheet grids. Film-strip chrome.
 */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Upload, Play, Sparkles, Settings, Music, Youtube,
  Zap, Eye, Download, Trash2, GripVertical, CheckCircle,
  AlertCircle, Loader2, Plus, X, RefreshCw, Palette,
  Film, Mic, BookOpen, Camera, FileVideo, TrendingUp,
  Wand2, Clock, Globe, Lock, Unlock, ChevronRight,
} from "lucide-react";
import {
  DndContext, closestCenter, KeyboardSensor,
  PointerSensor, useSensor, useSensors,
} from "@dnd-kit/core";
import {
  arrayMove, SortableContext,
  sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { api } from "./api";

// ── Data ─────────────────────────────────────────────────────────────────────
const STYLE_PRESETS = [
  { id:"cinematic",  label:"CINEMATIC",   dot:"#D4A853", desc:"Gold · dark · film grain · dramatic" },
  { id:"energetic",  label:"ENERGETIC",   dot:"#FF6B35", desc:"Warm orange · bold cuts · high energy" },
  { id:"warm_cozy",  label:"WARM & COZY", dot:"#E8943A", desc:"Golden tones · serif · soft mood" },
  { id:"minimal",    label:"MINIMAL",     dot:"#9A9A9A", desc:"Clean white · helvetica · no clutter" },
  { id:"dramatic",   label:"DRAMATIC",    dot:"#E84040", desc:"High contrast · red · intense" },
  { id:"playful",    label:"PLAYFUL",     dot:"#9B59D0", desc:"Purple teal · rounded · fun" },
];

const FORMULAS = [
  { id:"hook_loop_payoff", label:"HOOK → LOOP → PAYOFF", desc:"Open with best moment, rewind, deliver" },
  { id:"pas",              label:"PROBLEM → AGITATION → SOLUTION", desc:"Relatable struggle → emotional hook" },
  { id:"storytime",        label:"STORY ARC",             desc:"Beginning → climax → resolution" },
  { id:"reaction",         label:"REACTION / COMMENTARY", desc:"Live sports-style narration" },
  { id:"day_in_life",      label:"DAY IN THE LIFE",       desc:"Morning to night slice of life" },
];

const VOICES = [
  { id:"warm_female",   label:"WARM FEMALE",    desc:"Friendly US English" },
  { id:"deep_male",     label:"DEEP MALE",      desc:"Rich UK English" },
  { id:"excited",       label:"EXCITED",        desc:"High-energy Australian" },
  { id:"calm_narrator", label:"CALM NARRATOR",  desc:"Documentary Canadian" },
  { id:"playful",       label:"PLAYFUL",        desc:"Fun Indian-accent English" },
];

const STEPS = ["ASSETS","VISION","SCRIPT","DESIGN","VOICE","VIDEO","YOUTUBE"];

// ── Helpers ───────────────────────────────────────────────────────────────────
function fileType(name: string) {
  const ext = name.split(".").pop()?.toLowerCase() || "";
  if (["jpg","jpeg","png","webp","gif"].includes(ext)) return "image";
  if (["mp4","mov","avi","mkv","webm"].includes(ext)) return "video";
  if (["mp3","wav","aac","ogg"].includes(ext)) return "audio";
  return "other";
}

// ── Sprocket column decoration ────────────────────────────────────────────────
function SprocketCol({ side = "left" }: { side?: "left"|"right" }) {
  return (
    <div className={`hidden lg:flex flex-col items-center py-8 gap-[22px] w-[38px] flex-shrink-0 border-${side === "left" ? "r" : "l"} border-[#1C1C26] bg-[#0A0A11]`}>
      {Array.from({ length: 28 }).map((_, i) => (
        <div key={i} className="w-[18px] h-[18px] rounded-full border border-[#1E1E2A] bg-[#08080D] flex-shrink-0" />
      ))}
    </div>
  );
}

// ── Draggable media item ──────────────────────────────────────────────────────
function MediaItem({ id, file, selected, onSelect, onDelete, apiBase }: any) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });
  const type = fileType(file);
  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition, zIndex: isDragging ? 99 : "auto" }}
      onClick={() => onSelect(file)}
      className={`group relative flex items-center gap-2.5 rounded-sm p-2 cursor-pointer border transition-all duration-200
        ${isDragging ? "opacity-40" : ""}
        ${selected
          ? "border-[#D4A853]/60 bg-[#D4A853]/8"
          : "border-[#1C1C26] bg-[#0D0D14] hover:border-[#2A2A35] hover:bg-[#111118]"}`}
    >
      <button {...attributes} {...listeners} onClick={e => e.stopPropagation()}
        className="text-[#2A2A38] hover:text-[#706A5F] cursor-grab active:cursor-grabbing flex-shrink-0">
        <GripVertical size={13} />
      </button>
      <div className="w-10 h-10 rounded-sm overflow-hidden bg-[#111118] flex items-center justify-center flex-shrink-0 border border-[#1C1C26]">
        {type === "image" ? (
          <img src={`${apiBase}/media/${file}`} alt="" className="w-full h-full object-cover" />
        ) : type === "video" ? (
          <video src={`${apiBase}/media/${file}`} className="w-full h-full object-cover" muted />
        ) : (
          <Music size={14} className="text-[#D4A853]/50" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[10px] font-mono text-[#706A5F] truncate">{file}</p>
        <span className={`text-[8px] font-bold uppercase tracking-[0.15em]
          ${type === "image" ? "text-[#D4A853]/70" : type === "video" ? "text-[#E8E4DC]/40" : "text-[#706A5F]/60"}`}>
          {type}
        </span>
      </div>
      {selected && <div className="w-1.5 h-1.5 rounded-full bg-[#D4A853] flex-shrink-0" />}
      <button onClick={e => { e.stopPropagation(); onDelete(file); }}
        className="opacity-0 group-hover:opacity-100 p-1 text-[#2A2A38] hover:text-red-500/80 transition-all flex-shrink-0">
        <Trash2 size={11} />
      </button>
    </div>
  );
}

// ── Section label ─────────────────────────────────────────────────────────────
function SectionLabel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`text-[9px] font-bold uppercase tracking-[0.2em] text-[#706A5F] flex items-center gap-2 mb-3 ${className}`}>
      <div className="h-px flex-1 bg-[#1C1C26] max-w-[24px]" />
      {children}
    </div>
  );
}

// ── Amber button ──────────────────────────────────────────────────────────────
function AmberButton({ onClick, disabled, loading, children, className = "" }: any) {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      className={`flex items-center justify-center gap-2.5 font-bold uppercase tracking-[0.12em] transition-all duration-200
        ${disabled
          ? "bg-[#1A1A22] text-[#2A2A38] cursor-not-allowed border border-[#1C1C26]"
          : "bg-[#D4A853] hover:bg-[#E8BE6A] text-[#08080D] border border-[#D4A853]/80 shadow-lg shadow-[#D4A853]/10"
        } ${className}`}
    >
      {loading ? <Loader2 size={15} className="animate-spin" /> : children}
    </motion.button>
  );
}

// ── Step bar ──────────────────────────────────────────────────────────────────
function StepBar({ step, status }: { step: number; status: string }) {
  const pct = Math.min(Math.round(step / STEPS.length * 100), 100);
  const isDone = status === "done";
  const isErr  = status === "error";
  return (
    <div className="space-y-2.5">
      <div className="flex justify-between items-center">
        <span className={`text-[9px] font-bold uppercase tracking-[0.2em]
          ${isDone ? "text-[#D4A853]" : isErr ? "text-red-500/80" : "text-[#706A5F]"}`}>
          {isDone ? "COMPLETE" : isErr ? "ERROR" : STEPS[Math.min(step, STEPS.length - 1)] || "QUEUED"}
        </span>
        <span className="text-[9px] font-mono text-[#35353F]">{pct}%</span>
      </div>
      {/* Track */}
      <div className="h-[2px] bg-[#1C1C26] rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${isDone ? "bg-[#D4A853]" : isErr ? "bg-red-500/60" : "bg-[#D4A853]"}`}
          animate={{ width: `${pct}%` }} transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
      {/* Step dots — sprocket-hole style */}
      <div className="flex gap-1.5 items-center">
        {STEPS.map((s, i) => (
          <React.Fragment key={s}>
            <div title={s}
              className={`w-2.5 h-2.5 rounded-full border transition-all duration-300
                ${i < step ? "border-[#D4A853] bg-[#D4A853]"
                : i === step && status === "running" ? "border-[#D4A853] bg-transparent animate-pulse"
                : "border-[#252535] bg-transparent"}`}
            />
            {i < STEPS.length - 1 && (
              <div className={`flex-1 h-px transition-colors duration-300
                ${i < step - 1 ? "bg-[#D4A853]/40" : "bg-[#1C1C26]"}`} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

// ── Log line renderer ─────────────────────────────────────────────────────────
function LogLine({ line }: { line: string }) {
  let cls = "text-[#35353F]";
  if (line.includes("ERROR") || line.includes("failed")) cls = "text-red-500/70";
  else if (line.includes("WARN")) cls = "text-amber-500/60";
  else if (line.match(/✅|complete|ready/i)) cls = "text-[#D4A853]";
  else if (line.match(/\[\d+\/\d+\]/)) cls = "text-[#E8E4DC]/70 font-semibold";
  else if (line.includes("INFO")) cls = "text-[#706A5F]";
  return <span className={cls}>{line}{"\n"}</span>;
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [apiKey,       setApiKey]       = useState("");
  const [elKey,        setElKey]        = useState("");
  const [backendUrl,   setBackendUrl]   = useState(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");
  const [channelName,  setChannelName]  = useState("PetReels");
  const [brandVoice,   setBrandVoice]   = useState("warm and energetic");
  const [brandCta,     setBrandCta]     = useState("Follow for daily cuteness!");
  const [topic,        setTopic]        = useState("My puppy's funniest moments");
  const [formula,      setFormula]      = useState("hook_loop_payoff");
  const [style,        setStyle]        = useState("cinematic");
  const [voicePreset,  setVoicePreset]  = useState("warm_female");
  const [musicFile,    setMusicFile]    = useState("");
  const [refinement,   setRefinement]   = useState("");
  const [noUpload,     setNoUpload]     = useState(true);
  const [ytPrivacy,    setYtPrivacy]    = useState("unlisted");
  const [exportFmts,   setExportFmts]   = useState<string[]>(["shorts"]);
  const [elVoiceId,    setElVoiceId]    = useState("21m00Tcm4TlvDq8ikWAM");

  const [mediaFiles,   setMediaFiles]   = useState<string[]>([]);
  const [musicFiles,   setMusicFiles]   = useState<string[]>([]);
  const [selectedMedia,setSelectedMedia]= useState<string[]>([]);
  const [analysisData, setAnalysisData] = useState<any[]>([]);
  const [isAnalyzing,  setIsAnalyzing]  = useState(false);
  const [uploading,    setUploading]    = useState(false);

  const [activeJobId,  setActiveJobId]  = useState<string|null>(null);
  const [activeJob,    setActiveJob]    = useState<any>(null);
  const [jobHistory,   setJobHistory]   = useState<any[]>([]);
  const [outputFiles,  setOutputFiles]  = useState<string[]>([]);

  const [activeTab,    setActiveTab]    = useState<"studio"|"brand"|"history">("studio");
  const [activePanel,  setActivePanel]  = useState<"style"|"script"|"voice"|"publish">("style");
  const [plan,         setPlan]         = useState<any>(null);
  const [connected,    setConnected]    = useState<boolean|null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const logEndRef = useRef<HTMLDivElement>(null);
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const checkHealth = useCallback(async () => {
    try { await api.health(); setConnected(true); } catch { setConnected(false); }
  }, []);

  const refresh = useCallback(async () => {
    try {
      const [media, music, output] = await Promise.all([api.listMedia(), api.listMusic(), api.listOutput()]);
      setMediaFiles(media); setMusicFiles(music); setOutputFiles(output);
    } catch {}
  }, []);

  useEffect(() => { checkHealth(); refresh(); }, []);

  useEffect(() => {
    if (!activeJobId) return;
    const iv = setInterval(async () => {
      try {
        const j = await api.getJob(activeJobId);
        setActiveJob(j);
        if (j.plan) setPlan(j.plan);
        if (j.status === "done" || j.status === "error") {
          clearInterval(iv); refresh();
          api.listJobs().then(setJobHistory);
        }
      } catch {}
    }, 1500);
    return () => clearInterval(iv);
  }, [activeJobId]);

  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [activeJob?.logs]);

  const handleDragEnd = (e: any) => {
    const { active, over } = e;
    if (over && active.id !== over.id)
      setMediaFiles(items => arrayMove(items, items.indexOf(active.id), items.indexOf(over.id)));
  };

  const handleUploadMedia = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    setUploading(true);
    try { await api.uploadMedia(files); await refresh(); }
    finally { setUploading(false); e.target.value = ""; }
  };

  const handleUploadMusic = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; if (!file) return;
    try { await api.uploadMusic(file); await refresh(); }
    finally { e.target.value = ""; }
  };

  const toggleSelect = (f: string) =>
    setSelectedMedia(s => s.includes(f) ? s.filter(x => x !== f) : [...s, f]);

  const deleteFile = async (f: string) => {
    if (!confirm(`Delete ${f}?`)) return;
    await api.deleteMedia(f); await refresh();
  };

  const runAnalysis = async () => {
    if (!apiKey) return alert("Enter your Gemini API key first");
    const toAnalyze = selectedMedia.length ? selectedMedia : mediaFiles;
    if (!toAnalyze.length) return alert("Upload some media first");
    setIsAnalyzing(true);
    try { const r = await api.analyzeMedia(toAnalyze, apiKey); setAnalysisData(r); }
    catch (e: any) { alert("Vision analysis failed: " + e.message); }
    finally { setIsAnalyzing(false); }
  };

  const startGeneration = async () => {
    if (!apiKey) return alert("Gemini API key required");
    if (!mediaFiles.length) return alert("Upload media first");
    const payload = {
      api_key: apiKey, elevenlabs_key: elKey, elevenlabs_voice_id: elVoiceId,
      topic, formula, style, voice_preset: voicePreset, music_file: musicFile,
      refinement, no_upload: noUpload, yt_privacy: ytPrivacy,
      export_formats: exportFmts,
      media_list: selectedMedia.length ? selectedMedia : mediaFiles,
      media_analysis: analysisData,
      brand: { channel_name: channelName, voice: brandVoice, cta: brandCta },
    };
    try {
      const { job_id } = await api.startGeneration(payload);
      setActiveJobId(job_id);
      setActiveJob({ id: job_id, status: "queued", step: 0, logs: ["Pipeline started…"], outputs: {} });
    } catch (e: any) { alert("Failed to start: " + e.message); }
  };

  const isRunning   = activeJob?.status === "running" || activeJob?.status === "queued";
  const isDone      = activeJob?.status === "done";
  const hasError    = activeJob?.status === "error";
  const latestVideo = isDone && activeJob?.outputs?.video;
  const BASE        = backendUrl;

  return (
    <div className="h-screen bg-[#08080D] text-[#E8E4DC] flex flex-col overflow-hidden" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      {/* Fonts */}
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* Grain overlay */}
      <div className="fixed inset-0 pointer-events-none z-50 opacity-[0.025]"
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
          backgroundRepeat: "repeat", backgroundSize: "128px" }} />

      {/* Scan-line overlay */}
      <div className="fixed inset-0 pointer-events-none z-40"
        style={{ backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.06) 3px, rgba(0,0,0,0.06) 4px)" }} />

      {/* ── Topbar ──────────────────────────────────────────────────────── */}
      <header className="flex items-center justify-between px-5 py-2.5 border-b border-[#1C1C26] bg-[#0A0A11] flex-shrink-0 z-30">
        {/* Wordmark */}
        <div className="flex items-center gap-3">
          <div className="flex gap-px">
            {[...Array(4)].map((_,i) => (
              <div key={i} className="w-[5px] h-[22px] rounded-full" style={{ backgroundColor: i % 2 === 0 ? "#D4A853" : "#1C1C26" }} />
            ))}
          </div>
          <div>
            <span className="text-sm font-bold tracking-[0.18em] uppercase text-[#E8E4DC]"
              style={{ fontFamily: "'DM Mono', monospace", letterSpacing: "0.2em" }}>
              PETREEL
            </span>
            <span className="text-sm font-bold tracking-[0.18em] uppercase text-[#D4A853] ml-2"
              style={{ fontFamily: "'DM Mono', monospace" }}>
              STUDIO
            </span>
          </div>
          <div className="h-4 w-px bg-[#1C1C26]" />
          <span className="text-[9px] font-mono uppercase tracking-[0.25em] text-[#35353F]">Ferric Memory v2.0</span>
        </div>

        {/* Nav tabs */}
        <div className="flex items-center gap-1">
          {(["studio","brand","history"] as const).map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 text-[10px] font-bold uppercase tracking-[0.18em] transition-all duration-200
                ${activeTab === tab
                  ? "text-[#D4A853] border-b-2 border-[#D4A853]"
                  : "text-[#35353F] hover:text-[#706A5F] border-b-2 border-transparent"}`}>
              {tab === "studio" ? "STUDIO" : tab === "brand" ? "BRAND KIT" : "HISTORY"}
            </button>
          ))}
        </div>

        {/* Status */}
        <div className="flex items-center gap-3">
          <button onClick={() => setShowSettings(s => !s)}
            className={`p-1.5 transition-colors ${showSettings ? "text-[#D4A853]" : "text-[#35353F] hover:text-[#706A5F]"}`}>
            <Settings size={15} />
          </button>
          <div className="flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full ${connected === true ? "bg-[#D4A853]" : connected === false ? "bg-red-500/60" : "bg-[#35353F] animate-pulse"}`} />
            <span className={`text-[9px] font-mono uppercase tracking-[0.2em]
              ${isRunning ? "text-[#D4A853] animate-pulse" : isDone ? "text-[#D4A853]" : hasError ? "text-red-500/70" : "text-[#35353F]"}`}>
              {isRunning ? "GENERATING" : isDone ? "COMPLETE" : hasError ? "ERROR" : "READY"}
            </span>
          </div>
        </div>
      </header>

      {/* Settings dropdown */}
      <AnimatePresence>
        {showSettings && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} className="overflow-hidden border-b border-[#1C1C26] bg-[#0A0A11] flex-shrink-0 z-20">
            <div className="grid grid-cols-3 gap-4 px-5 py-4">
              <div className="space-y-1.5">
                <label className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#35353F]">Gemini API Key</label>
                <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)}
                  placeholder="AIza…"
                  className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-3 py-2 text-xs font-mono text-[#D4A853] focus:outline-none focus:border-[#D4A853]/40 placeholder-[#252535]" />
              </div>
              <div className="space-y-1.5">
                <label className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#35353F]">Railway Backend URL</label>
                <input value={backendUrl} onChange={e => setBackendUrl(e.target.value)}
                  className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-3 py-2 text-xs font-mono text-[#E8E4DC]/60 focus:outline-none focus:border-[#D4A853]/40" />
              </div>
              <div className="space-y-1.5">
                <label className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#35353F]">ElevenLabs Key (optional)</label>
                <input type="password" value={elKey} onChange={e => setElKey(e.target.value)}
                  placeholder="For premium TTS voices"
                  className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-3 py-2 text-xs font-mono text-[#E8E4DC]/40 focus:outline-none focus:border-[#D4A853]/40 placeholder-[#252535]" />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Main body ────────────────────────────────────────────────────── */}
      <div className="flex-1 flex overflow-hidden">

        {/* ════════════════════════════════════════════════════════════════
            STUDIO TAB
        ════════════════════════════════════════════════════════════════ */}
        {activeTab === "studio" && (
          <>
            {/* Film strip left */}
            <SprocketCol side="left" />

            {/* ── MEDIA LIBRARY ──────────────────────────────────────── */}
            <aside className="w-64 border-r border-[#1C1C26] bg-[#0A0A11] flex flex-col flex-shrink-0">
              <div className="px-4 pt-4 pb-3 border-b border-[#1C1C26]">
                <div className="flex items-center justify-between mb-3">
                  <SectionLabel className="mb-0">
                    <Camera size={10} className="text-[#D4A853]" />
                    ARCHIVE
                    <span className="ml-1 px-1.5 py-0.5 bg-[#D4A853]/10 text-[#D4A853] font-mono text-[8px] border border-[#D4A853]/20">
                      {mediaFiles.length.toString().padStart(2, "0")}
                    </span>
                  </SectionLabel>
                  <div className="flex gap-1.5">
                    <label className="p-1.5 border border-[#1C1C26] text-[#35353F] hover:border-[#D4A853]/30 hover:text-[#D4A853]/60 transition-all cursor-pointer rounded-sm" title="Upload music">
                      <Music size={12} />
                      <input type="file" accept=".mp3,.wav,.aac" onChange={handleUploadMusic} className="hidden" />
                    </label>
                    <label className="p-1.5 border border-[#D4A853]/30 bg-[#D4A853]/8 text-[#D4A853]/80 hover:bg-[#D4A853]/15 transition-all cursor-pointer rounded-sm" title="Upload media">
                      <Plus size={12} />
                      <input type="file" multiple accept="image/*,video/*" onChange={handleUploadMedia} className="hidden" />
                    </label>
                  </div>
                </div>

                {mediaFiles.length > 0 && (
                  <div className="flex gap-2">
                    <button onClick={() => setSelectedMedia(s => s.length === mediaFiles.length ? [] : [...mediaFiles])}
                      className="flex-1 text-[9px] font-mono uppercase tracking-[0.15em] py-1.5 border border-[#1C1C26] text-[#35353F] hover:border-[#2A2A35] hover:text-[#706A5F] transition-all rounded-sm">
                      {selectedMedia.length === mediaFiles.length ? "DESELECT" : "SELECT ALL"}
                    </button>
                    <button onClick={runAnalysis} disabled={isAnalyzing}
                      className="flex-1 text-[9px] font-mono uppercase tracking-[0.15em] py-1.5 border border-[#D4A853]/30 bg-[#D4A853]/8 text-[#D4A853]/70 hover:bg-[#D4A853]/15 transition-all rounded-sm flex items-center justify-center gap-1.5 disabled:opacity-50">
                      {isAnalyzing ? <Loader2 size={9} className="animate-spin" /> : <Eye size={9} />}
                      {isAnalyzing ? "SCANNING" : "VISION AI"}
                    </button>
                  </div>
                )}
              </div>

              <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1.5 custom-scrollbar">
                {uploading && (
                  <div className="flex items-center gap-2 text-[9px] font-mono uppercase tracking-[0.15em] text-[#D4A853]/70 bg-[#D4A853]/5 border border-[#D4A853]/15 px-3 py-2 mb-2">
                    <Loader2 size={10} className="animate-spin" /> UPLOADING
                  </div>
                )}
                {mediaFiles.length === 0 ? (
                  <label className="flex flex-col items-center justify-center min-h-[180px] border border-dashed border-[#1C1C26] cursor-pointer hover:border-[#D4A853]/20 transition-all gap-3 text-[#35353F]">
                    <Upload size={28} strokeWidth={1.5} />
                    <span className="text-[9px] font-mono uppercase tracking-[0.2em] text-center">DROP PHOTOS<br />& VIDEOS</span>
                    <input type="file" multiple accept="image/*,video/*" onChange={handleUploadMedia} className="hidden" />
                  </label>
                ) : (
                  <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                    <SortableContext items={mediaFiles} strategy={verticalListSortingStrategy}>
                      {mediaFiles.map(f => (
                        <MediaItem key={f} id={f} file={f}
                          selected={selectedMedia.includes(f)}
                          onSelect={toggleSelect}
                          onDelete={deleteFile}
                          apiBase={BASE} />
                      ))}
                    </SortableContext>
                  </DndContext>
                )}
              </div>

              {analysisData.length > 0 && (
                <div className="px-4 py-3 border-t border-[#1C1C26] space-y-2">
                  <div className="flex items-center gap-2 text-[8px] font-mono uppercase tracking-[0.2em] text-[#D4A853]/70">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#D4A853]" /> VISION READY
                  </div>
                  <div className="space-y-1 max-h-24 overflow-y-auto custom-scrollbar">
                    {analysisData.map((a, i) => (
                      <div key={i} className="text-[8px] font-mono flex gap-2 text-[#35353F]">
                        <span className="text-[#D4A853]/60 truncate max-w-[80px]">{a.filename?.split("-").pop() || a.filename}</span>
                        <span className="text-[#252535]">·</span>
                        <span>{a.mood}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </aside>

            {/* ── INSTRUMENT PANEL ───────────────────────────────────── */}
            <main className="flex-1 flex flex-col overflow-hidden min-w-0 border-r border-[#1C1C26]">

              {/* Panel tabs */}
              <div className="flex border-b border-[#1C1C26] bg-[#0A0A11] flex-shrink-0">
                {([
                  ["style",   <Palette size={11}/>,   "STYLE"],
                  ["script",  <BookOpen size={11}/>,  "SCRIPT"],
                  ["voice",   <Mic size={11}/>,       "VOICE"],
                  ["publish", <Youtube size={11}/>,   "PUBLISH"],
                ] as const).map(([id, icon, label]) => (
                  <button key={id} onClick={() => setActivePanel(id as any)}
                    className={`flex items-center gap-2 px-5 py-3 text-[9px] font-bold uppercase tracking-[0.2em] border-r border-[#1C1C26] transition-all
                      ${activePanel === id
                        ? "text-[#D4A853] border-b-2 border-b-[#D4A853] bg-[#0D0D14]"
                        : "text-[#35353F] hover:text-[#706A5F] border-b-2 border-b-transparent"}`}>
                    {icon} {label}
                  </button>
                ))}
              </div>

              <div className="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar">

                {/* ── STYLE PANEL ─────────────────────────────────────── */}
                {activePanel === "style" && <>
                  <div>
                    <SectionLabel><Wand2 size={10} className="text-[#D4A853]" />VIDEO STYLE PRESET</SectionLabel>
                    <div className="grid grid-cols-2 gap-2">
                      {STYLE_PRESETS.map(s => (
                        <button key={s.id} onClick={() => setStyle(s.id)}
                          className={`text-left p-3 border rounded-sm transition-all duration-200 group
                            ${style === s.id
                              ? "border-[#D4A853]/60 bg-[#D4A853]/6"
                              : "border-[#1C1C26] bg-[#0D0D14] hover:border-[#2A2A35]"}`}>
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.dot }} />
                              <span className={`text-[10px] font-bold uppercase tracking-[0.15em]
                                ${style === s.id ? "text-[#D4A853]" : "text-[#706A5F]"}`}>{s.label}</span>
                            </div>
                            {style === s.id && <div className="w-1.5 h-1.5 rounded-full bg-[#D4A853]" />}
                          </div>
                          <p className="text-[9px] text-[#35353F] leading-tight">{s.desc}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <SectionLabel><TrendingUp size={10} className="text-[#D4A853]" />REEL TOPIC</SectionLabel>
                    <input value={topic} onChange={e => setTopic(e.target.value)}
                      placeholder="e.g. My golden retriever's morning chaos"
                      className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-4 py-3 text-sm text-[#E8E4DC] placeholder-[#252535] focus:outline-none focus:border-[#D4A853]/40 transition-colors" />
                  </div>

                  <div>
                    <SectionLabel>REFINEMENT / CORRECTION</SectionLabel>
                    <textarea value={refinement} onChange={e => setRefinement(e.target.value)}
                      placeholder="Tell the AI what to change on re-run…"
                      className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-4 py-3 text-xs text-[#706A5F] placeholder-[#252535] focus:outline-none focus:border-[#D4A853]/30 min-h-[56px] resize-none transition-colors" />
                  </div>

                  {musicFiles.length > 0 && (
                    <div>
                      <SectionLabel><Music size={10} className="text-[#D4A853]" />BACKGROUND MUSIC</SectionLabel>
                      <select value={musicFile} onChange={e => setMusicFile(e.target.value)}
                        className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-4 py-2.5 text-sm text-[#E8E4DC]/70 focus:outline-none focus:border-[#D4A853]/40 appearance-none transition-colors">
                        <option value="">None</option>
                        {musicFiles.map(f => <option key={f} value={f}>{f}</option>)}
                      </select>
                    </div>
                  )}
                </>}

                {/* ── SCRIPT PANEL ─────────────────────────────────────── */}
                {activePanel === "script" && <>
                  <div>
                    <SectionLabel><Film size={10} className="text-[#D4A853]" />INVIDEO VIRAL FORMULA</SectionLabel>
                    <div className="space-y-2">
                      {FORMULAS.map(f => (
                        <button key={f.id} onClick={() => setFormula(f.id)}
                          className={`w-full text-left p-3.5 border rounded-sm transition-all flex items-start gap-3
                            ${formula === f.id ? "border-[#D4A853]/50 bg-[#D4A853]/6" : "border-[#1C1C26] bg-[#0D0D14] hover:border-[#2A2A35]"}`}>
                          <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${formula === f.id ? "bg-[#D4A853]" : "bg-[#252535]"}`} />
                          <div>
                            <p className={`text-[10px] font-bold uppercase tracking-[0.12em] ${formula === f.id ? "text-[#D4A853]" : "text-[#706A5F]"}`}>{f.label}</p>
                            <p className="text-[9px] text-[#35353F] mt-0.5">{f.desc}</p>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {plan && (
                    <div className="border border-[#D4A853]/20 bg-[#D4A853]/4 rounded-sm p-4 space-y-3">
                      <div className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#D4A853]/60 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#D4A853]" /> GENERATED SCRIPT
                      </div>
                      <p className="text-sm font-semibold text-[#E8E4DC]">{plan.title}</p>
                      <div className="space-y-2 max-h-44 overflow-y-auto custom-scrollbar">
                        {(plan.script_segments || []).map((seg: any, i: number) => (
                          <div key={i} className="flex gap-3 text-[10px] border-l border-[#D4A853]/30 pl-3 py-0.5">
                            <span className="text-[#D4A853]/60 font-mono uppercase w-16 flex-shrink-0">{seg.role}</span>
                            <span className="text-[#706A5F]">{seg.voiceover_text}</span>
                          </div>
                        ))}
                      </div>
                      {plan.hook_options?.length > 0 && (
                        <div className="pt-2 border-t border-[#1C1C26]">
                          <p className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#35353F] mb-1.5">HOOK OPTIONS</p>
                          {plan.hook_options.map((h: string, i: number) => (
                            <p key={i} className="text-[10px] text-[#35353F] flex gap-2 mb-1">
                              <span className="text-[#D4A853]/50 font-mono">{String.fromCharCode(65+i)}</span>{h}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </>}

                {/* ── VOICE PANEL ──────────────────────────────────────── */}
                {activePanel === "voice" && <>
                  <div>
                    <SectionLabel><Mic size={10} className="text-[#D4A853]" />VOICE PRESET (gTTS FREE)</SectionLabel>
                    <div className="space-y-1.5">
                      {VOICES.map(v => (
                        <button key={v.id} onClick={() => setVoicePreset(v.id)}
                          className={`w-full text-left px-4 py-3 border rounded-sm flex items-center gap-3 transition-all
                            ${voicePreset === v.id ? "border-[#D4A853]/50 bg-[#D4A853]/6" : "border-[#1C1C26] bg-[#0D0D14] hover:border-[#2A2A35]"}`}>
                          <div className={`w-1.5 h-1.5 rounded-full ${voicePreset === v.id ? "bg-[#D4A853]" : "bg-[#252535]"}`} />
                          <div className="flex-1">
                            <p className={`text-[10px] font-bold uppercase tracking-[0.15em] ${voicePreset === v.id ? "text-[#D4A853]" : "text-[#706A5F]"}`}>{v.label}</p>
                            <p className="text-[9px] text-[#35353F]">{v.desc}</p>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="border-t border-[#1C1C26] pt-5 space-y-3">
                    <SectionLabel>ELEVENLABS (PREMIUM — OPTIONAL)</SectionLabel>
                    <input value={elVoiceId} onChange={e => setElVoiceId(e.target.value)}
                      placeholder="Voice ID (21m00Tcm4TlvDq8ikWAM = Rachel)"
                      className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-3 py-2 text-xs font-mono text-[#706A5F] focus:outline-none focus:border-[#D4A853]/30 placeholder-[#252535]" />
                    <p className="text-[9px] text-[#252535]">Find voice IDs at elevenlabs.io/voice-library · Enter ElevenLabs key in Settings</p>
                  </div>
                </>}

                {/* ── PUBLISH PANEL ────────────────────────────────────── */}
                {activePanel === "publish" && <>
                  <div className="space-y-3">
                    <SectionLabel><Youtube size={10} className="text-[#D4A853]" />YOUTUBE UPLOAD</SectionLabel>
                    <label className={`flex items-center gap-3 p-3.5 border rounded-sm cursor-pointer transition-all
                      ${noUpload ? "border-[#D4A853]/30 bg-[#D4A853]/5" : "border-[#1C1C26] bg-[#0D0D14] hover:border-[#2A2A35]"}`}>
                      <div className={`w-3.5 h-3.5 rounded-sm border-2 flex items-center justify-center
                        ${noUpload ? "border-[#D4A853] bg-[#D4A853]" : "border-[#252535]"}`}>
                        {noUpload && <X size={9} className="text-[#08080D]" />}
                      </div>
                      <input type="checkbox" checked={noUpload} onChange={e => setNoUpload(e.target.checked)} className="hidden" />
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#E8E4DC]/80">LOCAL ONLY (SKIP YOUTUBE)</p>
                        <p className="text-[9px] text-[#35353F]">Save video locally — no upload</p>
                      </div>
                    </label>

                    {!noUpload && <>
                      <SectionLabel>PRIVACY</SectionLabel>
                      {(["unlisted","private","public"] as const).map(p => (
                        <label key={p} className="flex items-center gap-3 py-2 cursor-pointer">
                          <div className={`w-2.5 h-2.5 rounded-full border-2 ${ytPrivacy === p ? "border-[#D4A853] bg-[#D4A853]" : "border-[#252535]"}`}
                            onClick={() => setYtPrivacy(p)} />
                          <input type="radio" name="privacy" value={p} checked={ytPrivacy === p} onChange={() => setYtPrivacy(p)} className="hidden" />
                          <span className={`text-[10px] font-bold uppercase tracking-[0.15em] ${ytPrivacy === p ? "text-[#E8E4DC]/80" : "text-[#35353F]"}`}>{p}</span>
                        </label>
                      ))}
                      <div className="p-3 border border-[#2A2010] bg-[#1A1208] rounded-sm text-[9px] font-mono text-[#706A5F]">
                        Place client_secrets.json in Railway /data/ folder for YouTube auth.
                      </div>
                    </>}

                    <div className="pt-2">
                      <SectionLabel>EXPORT FORMATS (SMART RESIZE)</SectionLabel>
                      {(["shorts","instagram"] as const).map(f => (
                        <label key={f} className="flex items-center gap-3 py-1.5 cursor-pointer">
                          <div className={`w-2.5 h-2.5 rounded-sm border-2 flex items-center justify-center
                            ${exportFmts.includes(f) ? "border-[#D4A853] bg-[#D4A853]" : "border-[#252535]"}`}
                            onClick={() => setExportFmts(prev => prev.includes(f) ? prev.filter(x=>x!==f) : [...prev,f])}>
                            {exportFmts.includes(f) && <X size={8} className="text-[#08080D]" />}
                          </div>
                          <input type="checkbox" checked={exportFmts.includes(f)}
                            onChange={e => setExportFmts(prev => e.target.checked ? [...prev,f] : prev.filter(x=>x!==f))}
                            className="hidden" />
                          <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#706A5F]">
                            {f === "shorts" ? "9:16 — YOUTUBE SHORTS" : "1:1 — INSTAGRAM SQUARE"}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                </>}
              </div>

              {/* Generate block */}
              <div className="flex-shrink-0 p-4 border-t border-[#1C1C26] bg-[#0A0A11] space-y-3">
                {!showSettings && (
                  <input value={apiKey} onChange={e => setApiKey(e.target.value)} type="password"
                    placeholder="GEMINI API KEY REQUIRED"
                    className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-3 py-2 text-[10px] font-mono text-[#D4A853] placeholder-[#252535] focus:outline-none focus:border-[#D4A853]/40" />
                )}
                <AmberButton onClick={startGeneration}
                  disabled={isRunning || !mediaFiles.length}
                  loading={isRunning}
                  className="w-full py-3.5 rounded-sm text-[11px]">
                  <Sparkles size={14} />
                  {isRunning ? "GENERATING…" : "CREATE REEL"}
                </AmberButton>
                {activeJob && <StepBar step={activeJob.step || 0} status={activeJob.status} />}
              </div>
            </main>

            {/* ── REVELATION PANEL ─────────────────────────────────────── */}
            <aside className="w-72 flex flex-col overflow-hidden">
              {/* 9:16 preview */}
              <div className="relative bg-[#080810] flex items-center justify-center border-b border-[#1C1C26] flex-shrink-0"
                style={{ aspectRatio: "9/16", maxHeight: "42%" }}>
                {latestVideo ? (
                  <>
                    <video key={latestVideo} src={`${BASE}/output/${latestVideo}?t=${Date.now()}`}
                      controls className="w-full h-full object-contain" />
                    <div className="absolute top-2 left-2 bg-[#D4A853] text-[#08080D] text-[7px] font-bold px-2 py-0.5 font-mono uppercase tracking-[0.18em]">
                      LATEST REEL
                    </div>
                    <a href={`${BASE}/output/${latestVideo}`} download
                      className="absolute top-2 right-2 p-1.5 border border-[#D4A853]/30 text-[#D4A853]/70 hover:bg-[#D4A853]/10 transition-all">
                      <Download size={11} />
                    </a>
                  </>
                ) : (
                  <div className="text-center text-[#252535] space-y-3">
                    <Play size={32} strokeWidth={1} className="mx-auto" />
                    <p className="text-[9px] font-mono uppercase tracking-[0.2em]">REVELATION</p>
                  </div>
                )}
              </div>

              {/* Output links */}
              {isDone && activeJob?.outputs && (
                <div className="flex-shrink-0 border-b border-[#1C1C26]">
                  {Object.entries(activeJob.outputs).map(([k, v]: any) => (
                    <a key={k} href={`${BASE}/output/${v}`} download target="_blank"
                      className="flex items-center justify-between text-[9px] font-mono uppercase tracking-[0.15em] px-4 py-2.5 border-b border-[#1C1C26] text-[#35353F] hover:text-[#D4A853] hover:bg-[#D4A853]/3 transition-all">
                      <span>{k.replace("_", " ")}</span>
                      <Download size={10} />
                    </a>
                  ))}
                  {activeJob?.youtube_url && (
                    <a href={activeJob.youtube_url} target="_blank"
                      className="flex items-center gap-2 text-[9px] font-mono uppercase tracking-[0.15em] px-4 py-2.5 text-red-500/60 hover:text-red-400 hover:bg-red-500/5 transition-all">
                      <Youtube size={10} /> WATCH ON YOUTUBE
                    </a>
                  )}
                </div>
              )}

              {/* Pipeline console */}
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-[#1C1C26] bg-[#0A0A11] flex-shrink-0">
                  <div className="flex items-center gap-2 text-[8px] font-mono uppercase tracking-[0.25em] text-[#35353F]">
                    <Zap size={9} className="text-[#D4A853]/50" /> PIPELINE LOG
                  </div>
                  <button onClick={() => setActiveJob((j: any) => j ? {...j, logs: []} : j)}
                    className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#252535] hover:text-[#35353F] transition-colors">
                    CLEAR
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto p-4 bg-[#08080D] custom-scrollbar">
                  <pre className="font-mono text-[9px] leading-relaxed whitespace-pre-wrap break-all">
                    {activeJob?.logs?.length
                      ? activeJob.logs.map((l: string, i: number) => <LogLine key={i} line={l} />)
                      : <span className="text-[#1C1C26]">WAITING FOR PIPELINE…</span>}
                    <div ref={logEndRef} />
                  </pre>
                </div>
              </div>
            </aside>

            {/* Film strip right */}
            <SprocketCol side="right" />
          </>
        )}

        {/* ════════════════════════════════════════════════════════════════
            BRAND KIT TAB
        ════════════════════════════════════════════════════════════════ */}
        {activeTab === "brand" && (
          <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
            <div className="max-w-xl mx-auto space-y-8">
              <div>
                <p className="text-[9px] font-mono uppercase tracking-[0.25em] text-[#35353F] mb-1">INSTRUMENT</p>
                <h2 className="text-2xl font-bold tracking-[-0.01em] text-[#E8E4DC]">Brand Kit</h2>
                <p className="text-sm text-[#706A5F] mt-1">Your identity applied to every generated video — like Canva Enterprise Brand Kit.</p>
              </div>

              {[
                {
                  title: "CHANNEL IDENTITY",
                  fields: [
                    { label: "Channel Name", value: channelName, set: setChannelName, type: "text" },
                    { label: "Brand Voice / Tone", value: brandVoice, set: setBrandVoice, placeholder: "e.g. warm, energetic, funny" },
                    { label: "Call-to-Action", value: brandCta, set: setBrandCta },
                  ],
                },
              ].map(section => (
                <div key={section.title} className="border border-[#1C1C26] rounded-sm p-5 space-y-4 bg-[#0A0A11]">
                  <SectionLabel>{section.title}</SectionLabel>
                  {section.fields.map(f => (
                    <div key={f.label} className="space-y-1.5">
                      <label className="text-[9px] font-mono uppercase tracking-[0.2em] text-[#35353F]">{f.label}</label>
                      <input value={f.value} onChange={e => f.set(e.target.value)} placeholder={f.placeholder || ""}
                        className="w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-3 py-2.5 text-sm text-[#E8E4DC] focus:outline-none focus:border-[#D4A853]/40 placeholder-[#252535] transition-colors" />
                    </div>
                  ))}
                </div>
              ))}

              <div className="border border-[#1C1C26] rounded-sm p-5 space-y-4 bg-[#0A0A11]">
                <SectionLabel>VISUAL IDENTITY</SectionLabel>
                <div className="space-y-1.5">
                  <label className="text-[9px] font-mono uppercase tracking-[0.2em] text-[#35353F]">Logo (PNG transparent)</label>
                  <label className="flex items-center gap-3 px-4 py-3 border border-dashed border-[#1C1C26] hover:border-[#D4A853]/30 cursor-pointer transition-all text-[#35353F] hover:text-[#D4A853]/60 rounded-sm">
                    <Upload size={14} />
                    <span className="text-[10px] font-mono uppercase tracking-[0.2em]">Upload Logo</span>
                    <input type="file" accept=".png,.svg" onChange={async e => {
                      const f = e.target.files?.[0]; if (!f) return;
                      await api.uploadLogo(f); alert("Logo uploaded!");
                    }} className="hidden" />
                  </label>
                </div>
              </div>

              <div className="border border-[#1C1C26] rounded-sm p-5 space-y-4 bg-[#0A0A11]">
                <SectionLabel>API KEYS</SectionLabel>
                {[
                  { label: "Gemini API Key (required)", value: apiKey, set: setApiKey, placeholder: "AIza…", color: "text-[#D4A853]" },
                  { label: "Railway Backend URL", value: backendUrl, set: setBackendUrl, placeholder: "https://your-app.railway.app", color: "text-[#E8E4DC]/50" },
                  { label: "ElevenLabs API Key (optional)", value: elKey, set: setElKey, placeholder: "Premium TTS voices", color: "text-[#706A5F]" },
                ].map(f => (
                  <div key={f.label} className="space-y-1.5">
                    <label className="text-[9px] font-mono uppercase tracking-[0.2em] text-[#35353F]">{f.label}</label>
                    <input type="password" value={f.value} onChange={e => f.set(e.target.value)} placeholder={f.placeholder}
                      className={`w-full bg-[#0D0D14] border border-[#1C1C26] rounded-sm px-3 py-2 text-xs font-mono ${f.color} focus:outline-none focus:border-[#D4A853]/40 placeholder-[#252535] transition-colors`} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════════
            HISTORY TAB
        ════════════════════════════════════════════════════════════════ */}
        {activeTab === "history" && (
          <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
            <div className="max-w-2xl mx-auto">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <p className="text-[9px] font-mono uppercase tracking-[0.25em] text-[#35353F] mb-1">ARCHIVE</p>
                  <h2 className="text-2xl font-bold text-[#E8E4DC]">Job History</h2>
                </div>
                <button onClick={async () => { const all = await api.listJobs(); setJobHistory(all); }}
                  className="p-2 border border-[#1C1C26] text-[#35353F] hover:text-[#D4A853] hover:border-[#D4A853]/30 transition-all">
                  <RefreshCw size={14} />
                </button>
              </div>

              {jobHistory.length === 0 ? (
                <div className="text-center text-[#252535] py-20 space-y-4">
                  <Film size={36} strokeWidth={1} className="mx-auto" />
                  <p className="text-[9px] font-mono uppercase tracking-[0.25em]">NO FRAMES DEVELOPED</p>
                  <button onClick={() => setActiveTab("studio")} className="text-[#D4A853]/60 text-xs hover:text-[#D4A853] font-mono uppercase tracking-[0.2em] transition-colors">
                    OPEN STUDIO →
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {jobHistory.map(j => (
                    <div key={j.id} onClick={() => { setActiveJobId(j.id); setActiveJob(j); setActiveTab("studio"); }}
                      className={`border rounded-sm p-4 flex gap-4 items-start cursor-pointer transition-all hover:border-[#2A2A35]
                        ${j.status === "done" ? "border-[#D4A853]/20 bg-[#D4A853]/3"
                        : j.status === "error" ? "border-red-500/15 bg-red-500/3"
                        : "border-[#1C1C26] bg-[#0A0A11]"}`}>
                      {/* Thumbnail */}
                      <div className="w-16 h-28 border border-[#1C1C26] bg-[#08080D] flex-shrink-0 overflow-hidden">
                        {j.outputs?.thumbnail
                          ? <img src={`${BASE}/output/${j.outputs.thumbnail}`} alt="" className="w-full h-full object-cover" />
                          : <div className="w-full h-full flex items-center justify-center text-[#1C1C26]"><Film size={16} strokeWidth={1} /></div>}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0
                            ${j.status === "done" ? "bg-[#D4A853]" : j.status === "error" ? "bg-red-500/60" : "bg-[#35353F] animate-pulse"}`} />
                          <span className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#35353F]">{j.status}</span>
                        </div>
                        <p className="text-sm font-medium text-[#E8E4DC]/80 truncate">{j.plan?.title || "Processing…"}</p>
                        <p className="text-[9px] font-mono text-[#35353F] mt-1">{j.created_at ? new Date(j.created_at).toLocaleString() : ""}</p>
                        {j.outputs && (
                          <div className="flex flex-wrap gap-1.5 mt-3">
                            {Object.entries(j.outputs).map(([k, v]: any) => (
                              <a key={k} href={`${BASE}/output/${v}`} download onClick={e => e.stopPropagation()}
                                className="text-[8px] font-mono uppercase tracking-[0.15em] px-2 py-1 border border-[#1C1C26] text-[#35353F] hover:text-[#D4A853] hover:border-[#D4A853]/20 transition-all flex items-center gap-1">
                                <Download size={8} /> {k}
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 3px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1C1C26; border-radius: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #D4A853; }
        select option { background: #0A0A11; color: #E8E4DC; }
      `}</style>
    </div>
  );
}
