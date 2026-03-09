import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiPost } from "@/lib/api";
import {
    ArrowLeft,
    BookOpen,
    CheckCircle2,
    ChevronDown,
    ChevronUp,
    ExternalLink,
    Loader2,
    Map,
    Sparkles,
    Target,
    Zap,
} from "lucide-react";
import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import type { UserProfile } from "./ProfileSetup";

interface Course {
  title: string;
  platform: string;
  url: string;
  duration: string;
  free: boolean;
}

interface Phase {
  phase: number;
  title: string;
  duration: string;
  description: string;
  skills: string[];
  courses: Course[];
  milestones: string[];
}

interface Roadmap {
  target_role: string;
  current_level: string;
  total_duration: string;
  gap_skills: string[];
  phases: Phase[];
}

const LEVEL_COLOR: Record<string, string> = {
  beginner:     "bg-teal/10 text-teal border-teal/20",
  intermediate: "bg-amber-500/10 text-amber-500 border-amber-500/20",
  advanced:     "bg-destructive/10 text-destructive border-destructive/20",
};

function PhaseCard({ phase, index }: { phase: Phase; index: number }) {
  const [open, setOpen] = useState(index === 0);

  return (
    <div className="relative flex gap-4">
      {/* Timeline connector */}
      <div className="flex flex-col items-center">
        <div className="w-9 h-9 rounded-full bg-teal flex items-center justify-center text-teal-foreground font-bold text-sm shrink-0 z-10">
          {phase.phase}
        </div>
        {/* vertical line */}
        <div className="w-px flex-1 bg-border mt-1" />
      </div>

      <Card className="flex-1 mb-6 border-border overflow-hidden">
        {/* Header */}
        <button
          className="w-full flex items-start gap-3 p-4 text-left hover:bg-muted/30 transition-colors"
          onClick={() => setOpen((o) => !o)}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-display font-semibold text-foreground">{phase.title}</span>
              <Badge variant="outline" className="text-xs">{phase.duration}</Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{phase.description}</p>
          </div>
          {open ? (
            <ChevronUp className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
          )}
        </button>

        {open && (
          <div className="px-4 pb-4 space-y-4 border-t border-border pt-4">
            {/* Skills */}
            {phase.skills?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Skills to Learn
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {phase.skills.map((s) => (
                    <Badge key={s} variant="secondary" className="text-xs">{s}</Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Courses */}
            {phase.courses?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Recommended Courses
                </p>
                <div className="space-y-2">
                  {phase.courses.map((c, i) => (
                    <a
                      key={i}
                      href={c.url || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-2.5 rounded-lg border border-border hover:border-teal/40 hover:bg-teal/5 transition-colors group"
                    >
                      <BookOpen className="w-4 h-4 text-teal shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate group-hover:text-teal transition-colors">
                          {c.title}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {c.platform} · {c.duration}
                          {c.free && (
                            <span className="ml-1.5 text-teal font-medium">FREE</span>
                          )}
                        </p>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Milestones */}
            {phase.milestones?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Milestones
                </p>
                <ul className="space-y-1.5">
                  {phase.milestones.map((m, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                      <CheckCircle2 className="w-4 h-4 text-teal shrink-0 mt-0.5" />
                      {m}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}

const RoadmapPage = () => {
  const navigate = useNavigate();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(false);

  const profile: UserProfile | null = (() => {
    try {
      const saved = localStorage.getItem("career-profile");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  })();

  const generate = useCallback(async () => {
    if (!profile) {
      toast.error("Please set up your profile first.");
      navigate("/profile");
      return;
    }
    setLoading(true);
    setRoadmap(null);
    try {
      const res = await apiPost<{ roadmap: Roadmap; error?: string }>(
        "/api/roadmap",
        { profile }
      );
      if (res.error || !res.roadmap) {
        toast.error(res.error ?? "Failed to generate roadmap. Try again.");
      } else {
        setRoadmap(res.roadmap);
        toast.success("Roadmap generated!");
      }
    } catch (e: any) {
      toast.error(e.message ?? "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }, [profile, navigate]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 sm:px-6 py-4 border-b border-border bg-card sticky top-0 z-20">
        <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="w-8 h-8 rounded-lg bg-teal flex items-center justify-center">
          <Map className="w-4 h-4 text-teal-foreground" />
        </div>
        <div>
          <h1 className="font-display font-semibold text-foreground text-sm">Career Roadmap</h1>
          <p className="text-xs text-muted-foreground">Personalized, AI-generated learning path</p>
        </div>
        <Button
          className="ml-auto bg-teal text-teal-foreground hover:bg-teal/90"
          size="sm"
          onClick={generate}
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
              Generating…
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5 mr-1.5" />
              {roadmap ? "Regenerate" : "Generate Roadmap"}
            </>
          )}
        </Button>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        {/* No profile warning */}
        {!profile && (
          <Card className="p-6 text-center border-dashed">
            <Target className="w-10 h-10 mx-auto text-muted-foreground mb-3" />
            <p className="font-medium text-foreground mb-1">No profile set up yet</p>
            <p className="text-sm text-muted-foreground mb-4">
              Add your current role, skills and career goals for a personalised roadmap.
            </p>
            <Button size="sm" onClick={() => navigate("/profile")}>
              Set Up Profile
            </Button>
          </Card>
        )}

        {/* Empty state */}
        {profile && !roadmap && !loading && (
          <div className="text-center py-16 space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-teal/10 flex items-center justify-center mx-auto">
              <Map className="w-8 h-8 text-teal" />
            </div>
            <div>
              <p className="font-display font-semibold text-foreground text-lg">
                Ready to map your path to{" "}
                <span className="text-teal">{profile.goals?.split(" ").slice(0, 4).join(" ")}</span>
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Click <strong>Generate Roadmap</strong> to get a personalised, phase-by-phase learning plan.
              </p>
            </div>
            <Button
              className="bg-teal text-teal-foreground hover:bg-teal/90"
              onClick={generate}
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Generate My Roadmap
            </Button>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="space-y-4 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-28 rounded-xl bg-muted" />
            ))}
          </div>
        )}

        {/* Roadmap */}
        {roadmap && (
          <div className="space-y-6">
            {/* Summary header */}
            <div className="bg-card border border-border rounded-xl p-5 space-y-3">
              <div className="flex items-start justify-between gap-3 flex-wrap">
                <div>
                  <h2 className="font-display font-bold text-xl text-foreground flex items-center gap-2">
                    <Target className="w-5 h-5 text-teal" />
                    {roadmap.target_role}
                  </h2>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Total duration: <span className="font-medium text-foreground">{roadmap.total_duration}</span>
                  </p>
                </div>
                <Badge
                  variant="outline"
                  className={`capitalize ${LEVEL_COLOR[roadmap.current_level] ?? ""}`}
                >
                  {roadmap.current_level}
                </Badge>
              </div>

              {roadmap.gap_skills?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                    <Zap className="w-3 h-3 inline mr-1" />Skills to Acquire
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {roadmap.gap_skills.map((s) => (
                      <Badge key={s} variant="secondary" className="text-xs">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Phase timeline */}
            <div>
              <h3 className="font-display font-semibold text-foreground mb-4">
                Learning Phases ({roadmap.phases?.length ?? 0})
              </h3>
              {roadmap.phases?.map((phase, i) => (
                <PhaseCard key={phase.phase} phase={phase} index={i} />
              ))}
            </div>

            {/* CTA */}
            <div className="flex gap-3 pt-2">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => navigate("/chat")}
              >
                Discuss with AI Advisor
              </Button>
              <Button
                className="flex-1 bg-teal text-teal-foreground hover:bg-teal/90"
                onClick={generate}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Regenerate
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default RoadmapPage;
