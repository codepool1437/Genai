import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCw } from "lucide-react";
import React from "react";

interface Props  { children: React.ReactNode; fallback?: React.ReactNode }
interface State  { hasError: boolean; error?: Error }

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  reset = () => this.setState({ hasError: false, error: undefined });

  render() {
    if (!this.state.hasError) return this.props.children;

    if (this.props.fallback) return this.props.fallback;

    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-5 px-6 text-center">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center">
          <AlertTriangle className="w-8 h-8 text-amber-500" />
        </div>
        <div>
          <p className="font-display font-semibold text-lg text-foreground mb-1">
            Something went wrong
          </p>
          <p className="text-sm text-muted-foreground max-w-sm">
            {this.state.error?.message ?? "An unexpected error occurred. Please try again."}
          </p>
        </div>
        <Button onClick={this.reset} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Try Again
        </Button>
      </div>
    );
  }
}

export default ErrorBoundary;
