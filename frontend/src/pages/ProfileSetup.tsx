import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiGet, apiPost } from "@/lib/api";
import { ArrowRight, FileUp, Loader2, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export interface UserProfile {
  name: string;
  currentRole: string;
  education: string;
  skills: string;
  experience: string;
  goals: string;
  industries: string;
  bio: string;
}

const emptyProfile: UserProfile = {
  name: "",
  currentRole: "",
  education: "",
  skills: "",
  experience: "",
  goals: "",
  industries: "",
  bio: "",
};

const ProfileSetup = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile>(() => {
    try {
      const saved = localStorage.getItem("career-profile");
      return saved ? JSON.parse(saved) : emptyProfile;
    } catch { return emptyProfile; }
  });
  const [saving, setSaving] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleCVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setExtracting(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
      const resp = await fetch(`${API_BASE}/api/profile/extract`, { method: "POST", body: formData });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: "Extraction failed" }));
        throw new Error(err.detail || "Extraction failed");
      }
      const extracted = await resp.json();
      setProfile((prev) => ({
        ...prev,
        ...Object.fromEntries(Object.entries(extracted).filter(([, v]) => v)),
      }));
      toast.success("CV parsed! Review the fields below and edit if needed.");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Could not parse CV. Please fill manually.");
    } finally {
      setExtracting(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // Hydrate from server on first load (overwrites localStorage if server has newer data)
  useEffect(() => {
    apiGet<{ profile: UserProfile | null }>("/api/profile")
      .then(({ profile: serverProfile }) => {
        if (serverProfile) {
          setProfile({ ...emptyProfile, ...serverProfile });
          localStorage.setItem("career-profile", JSON.stringify(serverProfile));
        }
      })
      .catch(() => { /* offline — use localStorage value */ });
  }, []);

  const handleChange = (field: keyof UserProfile, value: string) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    // Save to localStorage immediately for instant availability
    localStorage.setItem("career-profile", JSON.stringify(profile));
    try {
      await apiPost("/api/profile", profile);
    } catch {
      toast.error("Could not save profile to server — saved locally only.");
    } finally {
      setSaving(false);
    }
    navigate("/chat");
  };

  const isValid = profile.name && profile.goals;

  return (
    <div className="min-h-screen bg-background">
      <nav className="flex items-center justify-between px-6 py-5 max-w-4xl mx-auto">
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2"
        >
          <div className="w-8 h-8 rounded-lg bg-teal flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-teal-foreground" />
          </div>
          <span className="font-display font-bold text-lg text-foreground">
            PathFinder AI
          </span>
        </button>
      </nav>

      <main className="max-w-2xl mx-auto px-6 py-10">
        <div className="text-center mb-10">
          <h1 className="font-display text-3xl font-bold text-foreground mb-3">
            Tell Us About You
          </h1>
          <p className="text-muted-foreground">
            The more you share, the more personalized your career guidance will be.
          </p>
        </div>

        <div className="space-y-6 bg-card rounded-xl p-6 sm:p-8 border border-border shadow-sm">

          {/* ── CV auto-fill ────────────────────────────────────────── */}
          <div className="rounded-lg border border-dashed border-border bg-muted/40 p-4 flex flex-col sm:flex-row items-center gap-4">
            <div className="flex-1">
              <p className="font-semibold text-sm text-foreground">Auto-fill from your CV / Resume</p>
              <p className="text-xs text-muted-foreground mt-0.5">Upload a PDF, DOCX, or TXT — our AI will extract your details and fill the form instantly.</p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md"
              className="hidden"
              onChange={handleCVUpload}
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={extracting}
              onClick={() => fileInputRef.current?.click()}
              className="shrink-0"
            >
              {extracting
                ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Parsing CV…</>
                : <><FileUp className="w-4 h-4 mr-2" />Upload CV</>}
            </Button>
          </div>

          {/* ── form fields ─────────────────────────────────────────── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                placeholder="Your name"
                value={profile.name}
                onChange={(e) => handleChange("name", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="currentRole">Current Role</Label>
              <Input
                id="currentRole"
                placeholder="e.g. Junior Developer"
                value={profile.currentRole}
                onChange={(e) => handleChange("currentRole", e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="education">Education</Label>
            <Input
              id="education"
              placeholder="e.g. B.Sc. Computer Science, XYZ University"
              value={profile.education}
              onChange={(e) => handleChange("education", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="skills">Skills</Label>
            <Textarea
              id="skills"
              placeholder="e.g. Python, JavaScript, React, SQL, Data Analysis, Communication..."
              value={profile.skills}
              onChange={(e) => handleChange("skills", e.target.value)}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="experience">Work Experience</Label>
            <Textarea
              id="experience"
              placeholder="Briefly describe your work experience and key achievements..."
              value={profile.experience}
              onChange={(e) => handleChange("experience", e.target.value)}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="goals">Career Goals *</Label>
            <Textarea
              id="goals"
              placeholder="Where do you want to be in 1-5 years? What roles interest you?"
              value={profile.goals}
              onChange={(e) => handleChange("goals", e.target.value)}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="industries">Industries of Interest</Label>
            <Input
              id="industries"
              placeholder="e.g. Tech, Finance, Healthcare, Gaming..."
              value={profile.industries}
              onChange={(e) => handleChange("industries", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="bio">Tell us about yourself (optional)</Label>
            <Textarea
              id="bio"
              placeholder="Describe your background in your own words — e.g. 'I'm a 3rd year CS student who knows some Python and wants to break into AI. I've built a few small projects but never worked professionally...'"
              value={profile.bio}
              onChange={(e) => handleChange("bio", e.target.value)}
              rows={4}
            />
            <p className="text-xs text-muted-foreground">Our AI reads this directly to understand your background and tailor your roadmap.</p>
          </div>

          <Button
            size="lg"
            className="w-full bg-teal text-teal-foreground hover:bg-teal/90 font-display font-semibold"
            disabled={!isValid || saving}
            onClick={handleSubmit}
          >
            {saving ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving…</>
            ) : (
              <>Get My Career Plan <ArrowRight className="w-4 h-4 ml-2" /></>
            )}
          </Button>
        </div>
      </main>
    </div>
  );
};

export default ProfileSetup;
