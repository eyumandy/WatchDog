"use client"

import { useState, useEffect, useMemo } from "react"
import { AlertCircle, Video, Server, User, DoorClosed, Clock, Search, ChevronLeft, ChevronRight } from "lucide-react"
import { format } from "date-fns"

interface SecurityLog {
  id: number
  type: "alert" | "camera" | "system" | "user" | "door" | "schedule"
  description: string
  timestamp: string
  severity: "low" | "medium" | "high"
  location: string
  involvedPersons: Array<{ name: string; imageUrl: string }>
  additionalInfo?: string
}

const getLogIcon = (type: SecurityLog["type"]) => {
  switch (type) {
    case "alert":
      return <AlertCircle size={16} className="text-red-400" />
    case "camera":
      return <Video size={16} className="text-blue-400" />
    case "system":
      return <Server size={16} className="text-green-400" />
    case "user":
      return <User size={16} className="text-purple-400" />
    case "door":
      return <DoorClosed size={16} className="text-yellow-400" />
    case "schedule":
      return <Clock size={16} className="text-indigo-400" />
  }
}

const getSeverityColor = (severity: SecurityLog["severity"]) => {
  switch (severity) {
    case "high":
      return "bg-red-500/20 text-red-400"
    case "medium":
      return "bg-yellow-500/20 text-yellow-400"
    case "low":
      return "bg-green-500/20 text-green-400"
  }
}

export const securityLogs: SecurityLog[] = [
  {
    id: 1,
    type: "alert",
    description: "Unauthorized access attempt detected at main entrance",
    timestamp: "2023-06-15T14:30:00Z",
    severity: "high",
    location: "Main Entrance",
    involvedPersons: [{ name: "Unknown Person", imageUrl: "/placeholder.svg?height=50&width=50" }],
    additionalInfo: "Facial recognition failed to identify the individual. Security team notified.",
  },
  {
    id: 2,
    type: "camera",
    description: "Motion detected in restricted area after hours",
    timestamp: "2023-06-15T22:15:00Z",
    severity: "medium",
    location: "Server Room",
    involvedPersons: [{ name: "John Doe", imageUrl: "/placeholder.svg?height=50&width=50" }],
    additionalInfo: "Employee identified. Investigating reason for after-hours access.",
  },
  {
    id: 3,
    type: "door",
    description: "Multiple failed access attempts",
    timestamp: "2023-06-16T09:45:00Z",
    severity: "medium",
    location: "R&D Department",
    involvedPersons: [{ name: "Jane Smith", imageUrl: "/placeholder.svg?height=50&width=50" }],
    additionalInfo: "Employee reported issues with access card. IT support notified.",
  },
  {
    id: 4,
    type: "system",
    description: "Critical system update completed",
    timestamp: "2023-06-16T03:00:00Z",
    severity: "low",
    location: "Central Server",
    involvedPersons: [],
    additionalInfo: "Automatic update process completed successfully. All systems operational.",
  },
  // Add more log entries to demonstrate pagination
  ...Array.from({ length: 16 }, (_, i) => ({
    id: i + 5,
    type: ["alert", "camera", "system", "user", "door", "schedule"][
      Math.floor(Math.random() * 6)
    ] as SecurityLog["type"],
    description: `Sample log entry ${i + 5}`,
    timestamp: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString(),
    severity: ["low", "medium", "high"][Math.floor(Math.random() * 3)] as SecurityLog["severity"],
    location: "Various Locations",
    involvedPersons: [],
  })),
]

interface SecurityLogEntriesProps {
  onSelectLog: (id: number) => void
}

export default function SecurityLogEntries({ onSelectLog }: SecurityLogEntriesProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedLogId, setSelectedLogId] = useState<number | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const logsPerPage = 5

  const filteredLogs = useMemo(() => {
    return securityLogs.filter(
      (log) =>
        log.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.severity.toLowerCase().includes(searchTerm.toLowerCase()),
    )
  }, [searchTerm])

  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm])

  const totalPages = Math.ceil(filteredLogs.length / logsPerPage)
  const indexOfLastLog = currentPage * logsPerPage
  const indexOfFirstLog = indexOfLastLog - logsPerPage
  const currentLogs = filteredLogs.slice(indexOfFirstLog, indexOfLastLog)

  const handleLogClick = (id: number) => {
    setSelectedLogId(id)
    onSelectLog(id)
  }

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber)
  }

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
              <div className="flex items-center space-x-2">
                {getLogIcon(log.type)}
                <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(log.severity)}`}>
                  {log.severity}
                </span>
              </div>
              <span className="text-xs text-white/60">{format(new Date(log.timestamp), "MMM d, HH:mm:ss")}</span>
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
  )
}

