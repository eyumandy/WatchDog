/**
 * EventList Component
 *
 * This component displays a chronological list of security events.
 * Each event includes an icon, description, timestamp, and severity level.
 *
 * Features:
 * - Event type indicators
 * - Severity level display
 * - Timestamp formatting
 * - Animated transitions
 */

"use client"

import { motion } from "framer-motion"
import { AlertCircle, Video, Server, User, DoorClosed, Clock } from "lucide-react"
import { formatDistanceToNow } from "date-fns"

interface Event {
  id: number
  type: "alert" | "camera" | "system" | "user" | "door" | "schedule"
  description: string
  timestamp: string
  severity: "low" | "medium" | "high"
}

const getEventIcon = (type: Event["type"]) => {
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

const getSeverityColor = (severity: Event["severity"]) => {
  switch (severity) {
    case "high":
      return "bg-red-500/20 text-red-400"
    case "medium":
      return "bg-yellow-500/20 text-yellow-400"
    case "low":
      return "bg-green-500/20 text-green-400"
  }
}

const events: Event[] = [
  {
    id: 1,
    type: "alert",
    description: "Motion detected in Living Room",
    timestamp: "2023-06-15T14:30:00Z",
    severity: "high",
  },
  {
    id: 2,
    type: "system",
    description: "Camera 2 went offline",
    timestamp: "2023-06-15T15:45:00Z",
    severity: "medium",
  },
  { id: 3, type: "camera", description: "Movement in Backyard", timestamp: "2023-06-15T16:20:00Z", severity: "low" },
  { id: 4, type: "door", description: "Front door opened", timestamp: "2023-06-15T18:10:00Z", severity: "medium" },
]

export default function EventList() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="space-y-4"
    >
      {events.map((event) => (
        <motion.div
          key={event.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="bg-white/5 backdrop-blur-md rounded-lg p-4 flex items-center space-x-4 border border-white/10"
        >
          <div className="flex-shrink-0">{getEventIcon(event.type)}</div>
          <div className="flex-grow">
            <p className="text-sm text-white/80">{event.description}</p>
            <p className="text-xs text-white/60">
              {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
            </p>
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(event.severity)}`}>{event.severity}</span>
        </motion.div>
      ))}
    </motion.div>
  )
}

