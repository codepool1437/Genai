import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import ChatPage from "./pages/ChatPage";
import CoverLetterGenerator from "./pages/CoverLetterGenerator";
import EvalDashboard from "./pages/EvalDashboard";
import Index from "./pages/Index";
import KnowledgeBase from "./pages/KnowledgeBase";
import MockInterview from "./pages/MockInterview";
import NotFound from "./pages/NotFound";
import ProfileSetup from "./pages/ProfileSetup";
import ResumeAnalyzer from "./pages/ResumeAnalyzer";
import RoadmapPage from "./pages/Roadmap";
import SkillQuiz from "./pages/SkillQuiz";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <ErrorBoundary>
          <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/profile" element={<ProfileSetup />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/knowledge-base" element={<KnowledgeBase />} />
          <Route path="/resume-analyzer" element={<ResumeAnalyzer />} />
          <Route path="/cover-letter" element={<CoverLetterGenerator />} />
          <Route path="/skill-quiz" element={<SkillQuiz />} />
          <Route path="/mock-interview" element={<MockInterview />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          <Route path="/eval" element={<EvalDashboard />} />
          <Route path="*" element={<NotFound />} />
          </Routes>
        </ErrorBoundary>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
