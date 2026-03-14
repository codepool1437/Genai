import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { analyzeProfile, FinalReport, Resource, RoadmapStep } from "@/lib/api";
import {
    ArrowLeft,
    BookOpen,
    ChevronDown,
    ChevronUp,
    Loader2,
    Map,
    MessageSquare,
    Sparkles,
    Target,
    Zap
} from "lucide-react";
import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import type { UserProfile } from "./ProfileSetup";

function PhaseCard({ step, index }: { step: RoadmapStep; index: number }) {
  const [open, setOpen] = useState(index === 0);

  return (
    <div className="relative flex gap-4">
      {/* Timeline connector */}
      <div className="flex flex-col items-center">
        <div className="w-9 h-9 rounded-full bg-teal flex items-center justify-center text-teal-foreground font-bold text-sm shrink-0 z-10">
          {step.step_number}
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
              <span className="font-display font-semibold text-foreground">{step.title}</span>
              <Badge variant="outline" className="text-xs">{step.timeline}</Badge>
            </div>
            <p className="text-sm text-foreground mt-2">{step.description}</p>
          </div>
          {open ? (
            <ChevronUp className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
          )}
        </button>
      </Card>
    </div>
  );
}

const RoadmapPage = () => {
  const navigate = useNavigate();
  const [report, setReport] = useState<FinalReport | null>(() => {
    try {
      const saved = localStorage.getItem("career-report");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(false);

  const [profile, setProfile] = useState<UserProfile | null>(() => {
    try {
      const s = localStorage.getItem("career-profile");
      return s ? JSON.parse(s) : null;
    } catch { return null; }
  });

  const generate = useCallback(async () => {
    if (!profile) {
      toast.error("Please set up your profile first.");
      navigate("/profile");
      return;
    }
    
    setLoading(true);
    setReport(null);
    
    const rawText = `
      Name: ${profile.name}
      Current Role: ${profile.currentRole}
      Education: ${profile.education}
      Skills: ${profile.skills}
      Experience: ${profile.experience}
      Goals: ${profile.goals}
      Industries: ${profile.industries}
      Bio: ${profile.bio}
    `;

    try {
      // Re-run the analysis
      const res = await analyzeProfile(rawText);
      setReport(res.report);
      localStorage.setItem("career-report", JSON.stringify(res.report));
      localStorage.setItem("career-session-id", res.session_id);
      toast.success("Roadmap generated!");
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
              {report ? "Regenerate" : "Generate Roadmap"}
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
        {profile && !report && !loading && (
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
            <div className="text-center pb-4 text-sm text-muted-foreground font-semibold">
              Agents are analyzing your profile, identifying skill gaps, and fetching RAG data...
            </div>
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-28 rounded-xl bg-muted" />
            ))}
          </div>
        )}

        {/* Roadmap Final Output */}
        {report && (
          <div className="space-y-6">
            
            {/* Encouraging AI Message */}
            <div className="bg-teal/10 text-teal-foreground px-5 py-4 rounded-xl text-sm border border-teal/20">
              <Sparkles className="w-5 h-5 inline mr-2" />
              <span className="font-medium text-foreground">{report.summary_message}</span>
            </div>

            {/* Summary header */}
            <div className="bg-card border border-border rounded-xl p-5 space-y-4">
              <div className="flex items-start justify-between gap-3 flex-wrap">
                <div>
                  <h2 className="font-display font-bold text-xl text-foreground flex items-center gap-2">
                    <Target className="w-5 h-5 text-teal" />
                    Target Role: {report.profile.career_goal}
                  </h2>
                </div>
              </div>

              {/* Gaps */}
              {report.skill_gaps?.missing_skills?.length > 0 && (
                <div className="pt-2">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                    <Zap className="w-3 h-3 inline mr-1" />Skills to Acquire (Skill Gaps)
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {report.skill_gaps.missing_skills.map((s, i) => (
                      <Badge key={i} variant="destructive" className="text-xs">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Existing */}
              {report.profile?.current_skills?.length > 0 && (
                <div className="pt-2">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                    Your Current Arsenal
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {report.profile.current_skills.map((s, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Phase timeline */}
            <div>
              <h3 className="font-display font-semibold text-foreground mb-4">
                Learning Roadmap ({report.roadmap?.steps?.length ?? 0} Steps)
              </h3>
              {report.roadmap?.steps?.map((step: RoadmapStep, i: number) => (
                <PhaseCard key={step.step_number || i} step={step} index={i} />
              ))}
            </div>

            {/* Recommended Resources (RAG DB) */}
            <div className="mt-8">
              <h3 className="font-display font-semibold text-foreground mb-4">
                Recommended Resources
              </h3>
              <div className="space-y-3">
                {report.resources?.resources.map((res: Resource, i: number) => (
                  <Card key={i} className="p-4 border-border hover:border-teal/40 transition-colors">
                    <div className="flex items-center gap-3">
                      <BookOpen className="w-5 h-5 text-teal shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-foreground flex items-center gap-2">
                          {res.title}
                          <Badge variant="outline" className="text-[10px] uppercase">{res.resource_type}</Badge>
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">
                          {res.description}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>

            {/* CTA */}
            <div className="flex gap-3 pt-6 flex-col sm:flex-row">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => navigate("/chat")}
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Discuss with AI Advisor
              </Button>
              <Button
                className="flex-1 bg-teal text-teal-foreground hover:bg-teal/90"
                onClick={generate}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Regenerate Roadmap
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default RoadmapPage;
