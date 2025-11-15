import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import OperatorDashboard from "./pages/OperatorDashboard";
import ListenerDashboard from "./pages/ListenerDashboard";
import NotFound from "./pages/NotFound";
import { useBroadcasts } from "@/lib/BroadcastProvider";
import { BroadcastFeed } from "@/components/BroadcastFeed";

const queryClient = new QueryClient();

const AppLayout = () => {
  const { isConnected } = useBroadcasts();
  
  return (
    <BrowserRouter>
      <div className="absolute top-4 right-4 z-50 w-80 p-4 bg-card border rounded-lg shadow-lg">
        <h3 className="font-bold">Live Feed</h3>
        <p className="text-sm">
          Status:
          <span className={isConnected ? 'text-green-500' : 'text-red-500'}>
            {isConnected ? ' Connected' : ' Disconnected'}
          </span>
        </p>
        <div className="mt-2 border-t pt-2 max-h-96 overflow-y-auto">
          <BroadcastFeed />
        </div>
      </div>
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/operator" element={<OperatorDashboard />} />
        <Route path="/listener" element={<ListenerDashboard />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AppLayout />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
