import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { analyzeProfile, extractCV } from "@/lib/api";
import { ArrowRight, Loader2, Sparkles, Upload } from "lucide-react";
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
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [profile, setProfile] = useState<UserProfile>(() => {
    try {
      const saved = localStorage.getItem("career-profile");
      return saved ? JSON.parse(saved) : emptyProfile;
    } catch { return emptyProfile; }
  });
  const [saving, setSaving] = useState(false);
  const [extracting, setExtracting] = useState(false);

  // Remove server hydration since we're using one-shot pipeline
  useEffect(() => {
    // Just ensure the window scrolls to top
    window.scrollTo(0, 0);
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      toast.error("Please upload a purely PDF file.");
      return;
    }

    setExtracting(true);
    toast.info("Extracting data from CV...");

    try {
      const response = await extractCV(file);
      
      const { 
        name, 
        current_role, 
        education, 
        skills, 
        experience, 
        goals, 
        industries 
      } = response.extracted_data;

      // Update the React state gracefully, prefer extracted values if they exist,
      // without completely wiping what the user might have already typed unless it was empty.
      setProfile((prev) => ({
        ...prev,
        name: name || prev.name,
        currentRole: current_role || prev.currentRole,
        education: education || prev.education,
        skills: skills || prev.skills,
        experience: experience || prev.experience,
        goals: goals || prev.goals,
        industries: industries || prev.industries,
        bio: prev.bio // Leave Bio untouched since we mapped the actual fields
      }));

      toast.success("CV Extracted! The fields have been auto-filled appropriately.");
    } catch (err: any) {
      toast.error(err.message || "Failed to extract CV.");
    } finally {
      setExtracting(false);
      // Reset input so they can upload again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleChange = (field: keyof UserProfile, value: string) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    // Save locally for persistence
    localStorage.setItem("career-profile", JSON.stringify(profile));

    // Construct the free-text representation of the profile for the LLM
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
      const response = await analyzeProfile(rawText);
      // Save the generated report and session ID so Roadmap can read it
      localStorage.setItem("career-report", JSON.stringify(response.report));
      localStorage.setItem("career-session-id", response.session_id);
      
      toast.success("Profile analyzed! Redirecting to your Roadmap...");
      navigate("/roadmap");
    } catch (err: any) {
      toast.error(err.message || "Failed to generate roadmap.");
    } finally {
      setSaving(false);
    }
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

          {/* ── Auto-fill CV Upload ─────────────────────────────────── */}
          <div className="bg-primary/5 rounded-lg p-5 border border-primary/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h3 className="font-medium text-foreground mb-1">
                Have a resume?
              </h3>
              <p className="text-sm text-muted-foreground">
                Upload your CV and we'll extract the details for you. (PDF only)
              </p>
            </div>
            <input 
              type="file" 
              accept=".pdf" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              disabled={extracting}
            />
            <Button 
              variant="outline" 
              className="shrink-0" 
              onClick={() => fileInputRef.current?.click()}
              disabled={extracting}
            >
              {extracting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Upload className="w-4 h-4 mr-2" />
              )}
              {extracting ? "Extracting..." : "Upload CV"}
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
