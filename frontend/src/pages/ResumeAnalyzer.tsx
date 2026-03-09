import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiUrl } from "@/lib/api";
import {
    AlertTriangle,
    ArrowLeft,
    BarChart3,
    BookOpen,
    CheckCircle2,
    FileText,
    Lightbulb,
    Loader2,
    Pen,
    Sparkles,
    Target,
    Upload,
    UserCheck,
    Zap
} from "lucide-react";
import { toast } from "sonner";
import type { UserProfile } from "./ProfileSetup";

interface Improvement {
  severity: "critical" | "warning" | "tip";
  category: string;
  issue: string;
  suggestion: string;
}

interface Analysis {
  overall_score: number;
  ats_score: number;
  content_score: number;
  skills_score: number;
  presentation_score: number;
  summary: string;
  strengths: string[];
  improvements: Improvement[];
  missing_keywords: string[];
  detected_skills: string[];
}

const severityConfig = {
  critical: { icon: AlertTriangle, color: "text-destructive", bg: "bg-destructive/10", badge: "destructive" as const },
  warning: { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10", badge: "secondary" as const },
  tip: { icon: Lightbulb, color: "text-teal", bg: "bg-teal/10", badge: "outline" as const },
};

function ScoreRing({ score, label, size = "md" }: { score: number; label: string; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: 72, md: 100, lg: 140 };
  const s = sizes[size];
  const strokeWidth = size === "lg" ? 8 : 6;
  const radius = (s - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? "hsl(var(--success))" : score >= 60 ? "hsl(var(--amber))" : "hsl(var(--destructive))";

  return (
    <div className="flex flex-col items-center gap-1.5">
      <svg width={s} height={s} className="-rotate-90">
        <circle cx={s / 2} cy={s / 2} r={radius} fill="none" stroke="hsl(var(--border))" strokeWidth={strokeWidth} />
        <circle
          cx={s / 2} cy={s / 2} r={radius} fill="none" stroke={color}
          strokeWidth={strokeWidth} strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" className="transition-all duration-1000 ease-out"
        />
        <text
          x={s / 2} y={s / 2}
          textAnchor="middle" dominantBaseline="central"
          className="fill-foreground rotate-90 origin-center"
          style={{ fontSize: size === "lg" ? 28 : size === "md" ? 20 : 16, fontWeight: 700 }}
        >
          {score}
        </text>
      </svg>
      <span className="text-xs text-muted-foreground font-medium text-center">{label}</span>
    </div>
  );
}

const ResumeAnalyzer = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [extractedProfile, setExtractedProfile] = useState<Partial<UserProfile> | null>(null);
  const [profileSaved, setProfileSaved] = useState(false);
  const [addingToKB, setAddingToKB] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    const ok = dropped && (
      dropped.type === "application/pdf" ||
      dropped.type === "text/plain" ||
      dropped.name.endsWith(".md") ||
      dropped.name.endsWith(".docx")
    );
    if (ok) {
      setFile(dropped);
    } else {
      toast.error("Please upload a PDF, DOCX, TXT, or MD file");
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  };

  const analyzeResume = async () => {
    if (!file) return;
    setAnalyzing(true);
    setAnalysis(null);
    setExtractedProfile(null);
    setProfileSaved(false);

    try {
      const isBinary = file.type === "application/pdf" || file.name.endsWith(".docx");
      let pdfBase64: string | undefined;
      let resumeText: string | undefined;

      if (isBinary) {
        const arrayBuffer = await file.arrayBuffer();
        pdfBase64 = btoa(
          new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), "")
        );
      } else {
        resumeText = await file.text();
        if (!resumeText || resumeText.trim().length < 20)
          throw new Error("Could not extract enough text from the file.");
      }

      const payload = { pdfBase64, resumeText, filename: file.name, targetRole: targetRole || undefined };
      const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

      // Run analysis + profile extraction in parallel
      const [analysisResp, profileResp] = await Promise.all([
        fetch(`${API}/api/resume/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }),
        fetch(`${API}/api/resume/extract-profile`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }),
      ]);

      if (!analysisResp.ok) {
        const errData = await analysisResp.json();
        throw new Error(errData.error || "Analysis failed");
      }

      const [analysisResult, profileResult] = await Promise.all([
        analysisResp.json(),
        profileResp.ok ? profileResp.json() : Promise.resolve(null),
      ]);

      setAnalysis(analysisResult.analysis);
      if (profileResult?.profile) setExtractedProfile(profileResult.profile);
      toast.success("Resume analysis complete!");
    } catch (err: any) {
      console.error("Analysis error:", err);
      toast.error(err.message || "Failed to analyze resume");
    } finally {
      setAnalyzing(false);
    }
  };

  const addToKnowledgeBase = async () => {
    if (!file) return;
    setAddingToKB(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("doc_type", "resume");
      const resp = await fetch(apiUrl("/api/documents/upload"), { method: "POST", body: form });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(err.detail ?? "Upload failed");
      }
      toast.success("Resume added to knowledge base! The AI can now reference it in chat.");
    } catch (e: any) {
      toast.error(e.message ?? "Failed to add to knowledge base");
    } finally {
      setAddingToKB(false);
    }
  };

  const saveToProfile = () => {
    if (!extractedProfile) return;
    const existing: Partial<UserProfile> = (() => {
      try { return JSON.parse(localStorage.getItem("career-profile") || "{}"); } catch { return {}; }
    })();
    const merged = { ...existing, ...Object.fromEntries(Object.entries(extractedProfile).filter(([, v]) => v)) };
    localStorage.setItem("career-profile", JSON.stringify(merged));
    setProfileSaved(true);
    toast.success("Profile updated from your resume!");
  };

  const criticalCount = analysis?.improvements.filter((i) => i.severity === "critical").length || 0;
  const warningCount = analysis?.improvements.filter((i) => i.severity === "warning").length || 0;
  const tipCount = analysis?.improvements.filter((i) => i.severity === "tip").length || 0;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-teal flex items-center justify-center">
              <FileText className="w-4 h-4 text-teal-foreground" />
            </div>
            <h1 className="font-display font-bold text-lg text-foreground">Resume Analyzer</h1>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Upload Section */}
        <Card className="p-6">
          <h2 className="font-display font-semibold text-lg text-card-foreground mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5 text-teal" />
            Upload Your Resume
          </h2>

          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              dragOver ? "border-teal bg-teal/5" : "border-border hover:border-teal/50"
            }`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="flex items-center justify-center gap-3">
                <FileText className="w-8 h-8 text-teal" />
                <div className="text-left">
                  <p className="font-medium text-card-foreground">{file.name}</p>
                  <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => { setFile(null); setAnalysis(null); }}>
                  Change
                </Button>
              </div>
            ) : (
              <>
                <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                <p className="text-card-foreground font-medium mb-1">Drop your resume here</p>
                <p className="text-sm text-muted-foreground mb-4">PDF, DOCX, TXT, or MD files</p>
                <label>
                  <input type="file" accept=".pdf,.docx,.txt,.md" className="hidden" onChange={handleFileSelect} />
                  <Button variant="outline" size="sm" asChild><span>Browse Files</span></Button>
                </label>
              </>
            )}
          </div>

          <div className="mt-4 flex flex-col sm:flex-row gap-3">
            <Input
              placeholder="Target role (optional) — e.g. Senior Frontend Engineer"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={analyzeResume}
              disabled={!file || analyzing}
              className="bg-teal text-teal-foreground hover:bg-teal/90 font-display font-semibold"
            >
              {analyzing ? (
                <>
                  <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Analyze Resume
                </>
              )}
            </Button>
            <Button
              variant="outline"
              onClick={addToKnowledgeBase}
              disabled={!file || addingToKB}
            >
              {addingToKB ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Adding...</>
              ) : (
                <><BookOpen className="w-4 h-4 mr-2" />Add to Knowledge Base</>
              )}
            </Button>
          </div>
        </Card>

        {/* Loading Skeleton */}
        {analyzing && (
          <div className="space-y-4 animate-pulse" aria-label="Loading analysis…">
            {/* Score circles row */}
            <Card className="p-6">
              <div className="h-4 bg-muted rounded w-40 mb-5" />
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="flex flex-col items-center gap-2">
                    <div className="w-20 h-20 rounded-full bg-muted" />
                    <div className="h-3 bg-muted rounded w-16" />
                  </div>
                ))}
              </div>
            </Card>
            {/* Strengths + Improvements cards */}
            {[1, 2, 3].map((i) => (
              <Card key={i} className="p-6 space-y-3">
                <div className="h-4 bg-muted rounded w-32" />
                <div className="h-3 bg-muted rounded w-full" />
                <div className="h-3 bg-muted rounded w-3/4" />
                <div className="h-3 bg-muted rounded w-5/6" />
              </Card>
            ))}
          </div>
        )}

        {/* Auto-fill Profile Banner */}
        {extractedProfile && (
          <Card className="p-5 border-teal/40 bg-teal/5">
            <div className="flex items-start gap-4 flex-wrap">
              <UserCheck className="w-6 h-6 text-teal shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="font-display font-semibold text-foreground mb-0.5">
                  Profile data detected in your resume
                </p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mt-1">
                  {extractedProfile.name && <span><strong>Name:</strong> {extractedProfile.name}</span>}
                  {extractedProfile.currentRole && <span><strong>Role:</strong> {extractedProfile.currentRole}</span>}
                  {extractedProfile.education && <span><strong>Education:</strong> {extractedProfile.education}</span>}
                  {extractedProfile.experience && <span><strong>Experience:</strong> {extractedProfile.experience}</span>}
                </div>
              </div>
              <Button
                size="sm"
                onClick={saveToProfile}
                disabled={profileSaved}
                className="bg-teal text-teal-foreground hover:bg-teal/90 shrink-0"
              >
                {profileSaved ? (
                  <><CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />Saved!</>
                ) : (
                  <><UserCheck className="w-3.5 h-3.5 mr-1.5" />Auto-fill Profile</>
                )}
              </Button>
            </div>
          </Card>
        )}

        {/* Results */}
        {analysis && (
          <>
            {/* Score Overview */}
            <Card className="p-6">
              <h2 className="font-display font-semibold text-lg text-card-foreground mb-6 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-teal" />
                Score Overview
              </h2>

              <div className="flex flex-col md:flex-row items-center gap-8">
                <ScoreRing score={analysis.overall_score} label="Overall" size="lg" />
                <div className="flex-1 grid grid-cols-2 sm:grid-cols-4 gap-6">
                  <ScoreRing score={analysis.ats_score} label="ATS" />
                  <ScoreRing score={analysis.content_score} label="Content" />
                  <ScoreRing score={analysis.skills_score} label="Skills" />
                  <ScoreRing score={analysis.presentation_score} label="Presentation" />
                </div>
              </div>

              <p className="mt-6 text-muted-foreground leading-relaxed bg-muted/50 rounded-lg p-4">
                {analysis.summary}
              </p>
            </Card>

            {/* Strengths */}
            <Card className="p-6">
              <h2 className="font-display font-semibold text-lg text-card-foreground mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-success" />
                Strengths
              </h2>
              <ul className="space-y-2">
                {analysis.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-card-foreground">
                    <CheckCircle2 className="w-4 h-4 text-success mt-0.5 shrink-0" />
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </Card>

            {/* Improvements */}
            <Card className="p-6">
              <h2 className="font-display font-semibold text-lg text-card-foreground mb-2 flex items-center gap-2">
                <Pen className="w-5 h-5 text-amber-500" />
                Improvements
              </h2>
              <div className="flex gap-3 mb-4">
                {criticalCount > 0 && (
                  <Badge variant="destructive">{criticalCount} Critical</Badge>
                )}
                {warningCount > 0 && (
                  <Badge variant="secondary">{warningCount} Warnings</Badge>
                )}
                {tipCount > 0 && (
                  <Badge variant="outline">{tipCount} Tips</Badge>
                )}
              </div>

              <Accordion type="multiple" className="space-y-2">
                {analysis.improvements.map((item, i) => {
                  const config = severityConfig[item.severity];
                  const Icon = config.icon;
                  return (
                    <AccordionItem key={i} value={`imp-${i}`} className={`${config.bg} rounded-lg border-none px-4`}>
                      <AccordionTrigger className="hover:no-underline py-3">
                        <div className="flex items-center gap-3 text-left">
                          <Icon className={`w-4 h-4 ${config.color} shrink-0`} />
                          <div>
                            <span className="text-sm font-medium text-card-foreground">{item.issue}</span>
                            <Badge variant={config.badge} className="ml-2 text-xs">{item.category}</Badge>
                          </div>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="text-muted-foreground pb-3 pl-7">
                        {item.suggestion}
                      </AccordionContent>
                    </AccordionItem>
                  );
                })}
              </Accordion>
            </Card>

            {/* Skill Gap Analysis */}
            <Card className="p-6">
              <h2 className="font-display font-semibold text-lg text-card-foreground mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-teal" />
                Skill Gap Analysis
                {targetRole && (
                  <span className="text-sm font-normal text-muted-foreground ml-1">vs. {targetRole}</span>
                )}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-teal" /> You Have ({analysis.detected_skills.length})
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.detected_skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="bg-teal/10 text-teal border-teal/20 text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {analysis.detected_skills.length === 0 && (
                      <p className="text-xs text-muted-foreground">No skills detected</p>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" /> You Need ({analysis.missing_keywords.length})
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.missing_keywords.map((kw) => (
                      <Badge key={kw} variant="outline" className="border-amber-500/30 text-amber-600 text-xs">
                        + {kw}
                      </Badge>
                    ))}
                    {analysis.missing_keywords.length === 0 && (
                      <p className="text-xs text-muted-foreground">Great coverage — no critical keywords missing.</p>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          </>
        )}
      </main>
    </div>
  );
};

export default ResumeAnalyzer;
