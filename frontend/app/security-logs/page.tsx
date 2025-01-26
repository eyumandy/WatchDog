"use client";

import { useState } from "react";
import NetworkBackground from "../components/NetworkBackground";
import DashboardHeader from "../components/DashboardHeader";
import SecurityLogEntries from "../components/SecurityLogEntries";
import SecurityLogDetails from "../components/SecurityLogDetails";

export default function SecurityLogs() {
  const [activeTab, setActiveTab] = useState("Security Logs");
  const [selectedLogId, setSelectedLogId] = useState<string | null>(null); // Updated type to match dynamic log IDs

  return (
    <div className="min-h-screen text-white overflow-hidden">
      {/* Network effect in the background */}
      <NetworkBackground
        color="rgba(67, 17, 17, 0.26)"
        nodeColor="rgba(255, 255, 255, 0.4)"
        lineColor="rgba(255, 255, 255, 0.15)"
      />

      {/* Foreground content */}
      <div className="relative z-10">
        <DashboardHeader activeTab={activeTab} setActiveTab={setActiveTab} />

        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-light">Security Logs</h1>
          </div>

          {/* Grid layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-12rem)]">
            {/* Left Pane: Log Entries */}
            <div className="lg:col-span-1 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden flex flex-col">
              <SecurityLogEntries onSelectLog={setSelectedLogId} />
            </div>

            {/* Right Pane: Log Details */}
            <div className="lg:col-span-2 bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 overflow-y-auto">
              <SecurityLogDetails selectedLogId={selectedLogId} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
