import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
    ArrowLeft,
    BarChart3,
    ChevronDown,
    ChevronUp,
    Download,
    Loader2,
    Play,
    RefreshCw,
    Sparkles,
} from "lucide-react";
import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    LabelList,
    Legend,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { toast } from "sonner";

// ── Types ────────────────────────────────────────────────────────────────────

interface EvalResult {
  question: string;
  context_snippet: string;
  answer: string;
  sources_count: number;
  context_relevance: number;
  answer_faithfulness: number;
  answer_relevance: number;
  latency_s: number;
}

interface EvalAggregate {
  context_relevance: number;
  answer_faithfulness: number;
  answer_relevance: number;
  avg_latency_s: number;
  num_questions: number;
}

interface EvalResponse {
  results: EvalResult[];
  aggregate: EvalAggregate;
}

// ── Constants ────────────────────────────────────────────────────────────────

const METRIC_LABELS: Record<string, string> = {
  context_relevance:   "Context Relevance",
  answer_faithfulness: "Answer Faithfulness",
  answer_relevance:    "Answer Relevance",
};

const METRIC_DESCRIPTIONS: Record<string, string> = {
  context_relevance:   "How relevant is the retrieved context to the question?",
  answer_faithfulness: "How grounded is the answer in the retrieved context?",
  answer_relevance:    "How directly does the answer address the question?",
};

// Score colour thresholds
function scoreColor(v: number): string {
  if (v >= 0.7) return "#14b8a6";   // teal — good
  if (v >= 0.45) return "#f59e0b";  // amber — moderate
  return "#ef4444";                  // red — poor
}

function scoreBadge(v: number): { label: string; className: string } {
  if (v >= 0.7)  return { label: "Good",     className: "bg-teal/10 text-teal border-teal/30" };
  if (v >= 0.45) return { label: "Moderate", className: "bg-amber-500/10 text-amber-600 border-amber-500/30" };
  return               { label: "Weak",      className: "bg-red-500/10 text-red-500 border-red-500/30" };
}

function pct(v: number) {
  return `${Math.round(v * 100)}%`;
}

// ── Custom tooltip for recharts ─────────────────────────────────────────────

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="font-semibold text-foreground mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} style={{ color: p.fill }}>
          {METRIC_LABELS[p.dataKey] ?? p.dataKey}: {pct(p.value)}
        </p>
      ))}
    </div>
  );
};

// ── Main Component ────────────────────────────────────────────────────────────

const EvalDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading]     = useState(false);
  const [data, setData]           = useState<EvalResponse | null>(null);
  const [expanded, setExpanded]   = useState<number | null>(null);

  const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

  const runEval = async () => {
    setLoading(true);
    setData(null);
    try {
      const resp = await fetch(`${API}/api/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_questions: 8 }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail ?? "Evaluation failed");
      }
      const result: EvalResponse = await resp.json();
      setData(result);
      toast.success("Evaluation complete!");
    } catch (e: any) {
      toast.error(e.message ?? "Failed to run evaluation");
    } finally {
      setLoading(false);
    }
  };

  const exportJson = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `rag-eval-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Exported eval results as JSON");
  };

  // Per-question bar chart data
  const perQuestionData = data?.results.map((r, i) => ({
    name: `Q${i + 1}`,
    context_relevance:   r.context_relevance,
    answer_faithfulness: r.answer_faithfulness,
    answer_relevance:    r.answer_relevance,
  })) ?? [];

  // Aggregate bar chart data
  const aggregateData = data
    ? [
        { metric: "Context Relevance",   value: data.aggregate.context_relevance,   key: "context_relevance" },
        { metric: "Ans Faithfulness",     value: data.aggregate.answer_faithfulness, key: "answer_faithfulness" },
        { metric: "Answer Relevance",     value: data.aggregate.answer_relevance,    key: "answer_relevance" },
      ]
    : [];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div
        className="relative overflow-hidden"
        style={{ background: "var(--gradient-hero)" }}
      >
        <div className="max-w-5xl mx-auto px-6 py-10">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-primary-foreground/70 hover:text-primary-foreground text-sm mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </button>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-teal/20 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-teal" />
            </div>
            <h1 className="font-display text-3xl font-bold text-primary-foreground">
              RAG Evaluation Dashboard
            </h1>
          </div>
          <p className="text-primary-foreground/70 text-sm max-w-xl">
            Measures how well the retrieval-augmented generation pipeline performs
            using cosine similarity on context relevance, answer faithfulness, and
            answer relevance — no external library needed.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10 space-y-8">

        {/* Run controls */}
        <div className="flex flex-wrap gap-3 items-center">
          <Button
            onClick={runEval}
            disabled={loading}
            className="bg-teal text-teal-foreground hover:bg-teal/90 font-display font-semibold"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Running Evaluation…</>
            ) : (
              <><Play className="w-4 h-4 mr-2" />Run Evaluation</>
            )}
          </Button>
          {data && (
            <>
              <Button variant="outline" onClick={runEval} disabled={loading}>
                <RefreshCw className="w-4 h-4 mr-2" />Re-run
              </Button>
              <Button variant="outline" onClick={exportJson}>
                <Download className="w-4 h-4 mr-2" />Export JSON
              </Button>
              <span className="text-sm text-muted-foreground ml-auto">
                {data.aggregate.num_questions} questions · avg {data.aggregate.avg_latency_s}s/query
              </span>
            </>
          )}
        </div>

        {/* Loading skeleton */}
        {loading && (
          <Card className="p-8 text-center">
            <Sparkles className="w-8 h-8 text-teal mx-auto mb-3 animate-pulse" />
            <p className="font-display font-semibold text-foreground mb-1">Evaluating RAG pipeline…</p>
            <p className="text-sm text-muted-foreground">
              Running {8} questions through retrieve → generate → score.
              <br />This takes ~1 min on a local LLM.
            </p>
            <Progress className="mt-5 h-1.5" value={undefined} />
          </Card>
        )}

        {/* Aggregate score cards */}
        {data && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {aggregateData.map(({ metric, value, key }) => {
                const badge = scoreBadge(value);
                return (
                  <Card key={key} className="p-5">
                    <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">{metric}</p>
                    <div className="flex items-end gap-2 mb-2">
                      <span
                        className="font-display text-4xl font-bold"
                        style={{ color: scoreColor(value) }}
                      >
                        {pct(value)}
                      </span>
                      <Badge variant="outline" className={`mb-1 text-xs ${badge.className}`}>{badge.label}</Badge>
                    </div>
                    <Progress
                      value={value * 100}
                      className="h-1.5"
                      style={{ "--progress-color": scoreColor(value) } as React.CSSProperties}
                    />
                    <p className="text-xs text-muted-foreground mt-2">{METRIC_DESCRIPTIONS[key]}</p>
                  </Card>
                );
              })}
            </div>

            {/* Aggregate bar chart */}
            <Card className="p-6">
              <h2 className="font-display font-semibold text-lg text-card-foreground mb-5 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-teal" />
                Aggregate Scores
              </h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={aggregateData} margin={{ top: 16, right: 16, bottom: 0, left: -16 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="metric" tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                  <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {aggregateData.map((entry) => (
                      <Cell key={entry.key} fill={scoreColor(entry.value)} />
                    ))}
                    <LabelList
                      dataKey="value"
                      position="top"
                      formatter={(v: number) => pct(v)}
                      style={{ fontSize: 11, fill: "hsl(var(--foreground))" }}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>

            {/* Per-question grouped bar chart */}
            <Card className="p-6">
              <h2 className="font-display font-semibold text-lg text-card-foreground mb-5 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-teal" />
                Per-Question Breakdown
              </h2>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={perQuestionData} margin={{ top: 16, right: 16, bottom: 0, left: -16 }} barCategoryGap="25%">
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                  <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend formatter={(v) => <span className="text-xs text-muted-foreground">{METRIC_LABELS[v] ?? v}</span>} />
                  <Bar dataKey="context_relevance"   fill="#14b8a6" radius={[3, 3, 0, 0]} name="context_relevance" />
                  <Bar dataKey="answer_faithfulness" fill="#f59e0b" radius={[3, 3, 0, 0]} name="answer_faithfulness" />
                  <Bar dataKey="answer_relevance"    fill="#6366f1" radius={[3, 3, 0, 0]} name="answer_relevance" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            {/* Question/Context/Answer triplets */}
            <div className="space-y-3">
              <h2 className="font-display font-semibold text-lg text-foreground flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-teal" />
                Question / Context / Answer Triplets
              </h2>
              {data.results.map((r, i) => {
                const open = expanded === i;
                const avgScore = (r.context_relevance + r.answer_faithfulness + r.answer_relevance) / 3;
                const badge = scoreBadge(avgScore);
                return (
                  <Card key={i} className="overflow-hidden">
                    <button
                      className="w-full text-left px-5 py-4 flex items-start gap-3 hover:bg-muted/40 transition-colors"
                      onClick={() => setExpanded(open ? null : i)}
                    >
                      <span className="shrink-0 w-7 h-7 rounded-full bg-teal/10 text-teal text-xs font-bold flex items-center justify-center mt-0.5">
                        Q{i + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-card-foreground leading-snug">{r.question}</p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          <span className="text-xs text-muted-foreground">
                            Context: <strong style={{ color: scoreColor(r.context_relevance) }}>{pct(r.context_relevance)}</strong>
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Faithfulness: <strong style={{ color: scoreColor(r.answer_faithfulness) }}>{pct(r.answer_faithfulness)}</strong>
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Relevance: <strong style={{ color: scoreColor(r.answer_relevance) }}>{pct(r.answer_relevance)}</strong>
                          </span>
                          <Badge variant="outline" className={`text-xs ${badge.className}`}>{badge.label}</Badge>
                          <span className="text-xs text-muted-foreground">{r.sources_count} sources · {r.latency_s}s</span>
                        </div>
                      </div>
                      {open
                        ? <ChevronUp className="w-4 h-4 text-muted-foreground shrink-0 mt-1" />
                        : <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0 mt-1" />
                      }
                    </button>

                    {open && (
                      <div className="border-t border-border bg-muted/20 px-5 py-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Retrieved Context (snippet)</p>
                          <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                            {r.context_snippet || "(nothing retrieved)"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Generated Answer</p>
                          <p className="text-card-foreground leading-relaxed">{r.answer}</p>
                        </div>
                      </div>
                    )}
                  </Card>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default EvalDashboard;
