"use client";

import { useState, useEffect, useMemo } from "react";
import { AlertCircle, Video, Server, User, DoorClosed, Clock, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { format } from "date-fns";
import axios from "axios";

export interface IncidentDetails {
    incident_id: string;
    upload_date: string;
    video_path: string;
    faces: string[];
  }
  
  export interface SecurityVideoPlayerProps {
    videoPath: string | null;
  }
  
  export interface SecurityLogDetailsProps {
    selectedLogId: string | null;
  }
  
interface SecurityLog {
  id: string; // Unique incident ID
  type: "alert" | "camera" | "system" | "user" | "door" | "schedule"; // Randomized log type
  description: string; // Incident description
  timestamp: string; // Time of the incident
  location: string; // Placeholder for now
}

const getLogIcon = (type: SecurityLog["type"]) => {
  switch (type) {
    case "alert":
      return <AlertCircle size={16} className="text-red-400" />;
    case "camera":
      return <Video size={16} className="text-blue-400" />;
    case "system":
      return <Server size={16} className="text-green-400" />;
    case "user":
      return <User size={16} className="text-purple-400" />;
    case "door":
      return <DoorClosed size={16} className="text-yellow-400" />;
    case "schedule":
      return <Clock size={16} className="text-indigo-400" />;
    default:
      return <AlertCircle size={16} className="text-white/60" />;
  }
};

const getRandomLogType = (): SecurityLog["type"] => {
  const types: SecurityLog["type"][] = ["alert", "camera", "system", "user", "door", "schedule"];
  return types[Math.floor(Math.random() * types.length)];
};

interface SecurityLogEntriesProps {
  onSelectLog: (id: string) => void;
}

export default function SecurityLogEntries({ onSelectLog }: SecurityLogEntriesProps) {
  const [logs, setLogs] = useState<SecurityLog[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLogId, setSelectedLogId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 5;

  // Fetch logs from the backend
  const fetchLogs = async () => {
    try {
      const response = await axios.get("http://localhost:5000/incidents");
      const incidents = response.data.incidents.map((incident: any) => ({
        id: incident.incident_id,
        type: getRandomLogType(), // Assign a random log type
        description: `Incident: ${incident.incident_id}`, // Default description based on ID
        timestamp: incident.upload_date,
        location: "Various Locations", // Placeholder
      }));
      setLogs(incidents);
    } catch (error) {
      console.error("Error fetching logs:", error);
    }
  };

  // Refresh logs every 15 seconds
  useEffect(() => {
    fetchLogs(); // Initial fetch
    const interval = setInterval(() => {
      console.log("Refreshing logs...");
      fetchLogs();
    }, 15000);

    return () => clearInterval(interval); // Cleanup interval
  }, []);

  // Filter logs based on search term
  const filteredLogs = useMemo(() => {
    return logs.filter(
      (log) =>
        log.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.type.toLowerCase().includes(searchTerm.toLowerCase()),
    );
  }, [searchTerm, logs]);

  // Reset to the first page when the search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const totalPages = Math.ceil(filteredLogs.length / logsPerPage);
  const indexOfLastLog = currentPage * logsPerPage;
  const indexOfFirstLog = indexOfLastLog - logsPerPage;
  const currentLogs = filteredLogs.slice(indexOfFirstLog, indexOfLastLog);

  const handleLogClick = (id: string) => {
    setSelectedLogId(id);
    onSelectLog(id);
  };

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-white/10">
        <div className="relative">
          <input
            type="text"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-md py-2 pl-10 pr-4 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50" size={18} />
        </div>
      </div>
      <div className="flex-grow overflow-y-auto">
        {currentLogs.map((log) => (
          <div
            key={log.id}
            className={`border-b border-white/10 cursor-pointer hover:bg-white/5 p-4 ${
              selectedLogId === log.id ? "bg-white/10" : ""
            }`}
            onClick={() => handleLogClick(log.id)}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">{getLogIcon(log.type)}</div>
              <span className="text-xs text-white/60">
                {format(new Date(log.timestamp), "MMM d, HH:mm:ss")}
              </span>
            </div>
            <p className="text-sm text-white/80">{log.description}</p>
          </div>
        ))}
      </div>
      <div className="p-4 border-t border-white/10 flex justify-between items-center">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="text-white/60 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft size={20} />
        </button>
        <span className="text-sm text-white/60">
          Page {currentPage} of {totalPages}
        </span>
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="text-white/60 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronRight size={20} />
        </button>
      </div>
    </div>
  );
}
