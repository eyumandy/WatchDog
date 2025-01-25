"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Bell, Camera, Server, AlertTriangle, User, DoorClosed, Clock, Filter } from "lucide-react"

interface Activity {
  id: number
  type: "alert" | "camera" | "system" | "user" | "door" | "schedule"
  message: string
  time: string
  severity: "low" | "medium" | "high"
}

const getIcon = (type: Activity["type"]) => {
  switch (type) {
    case "alert":
      return <AlertTriangle size={16} className="text-yellow-400" />
    case "camera":
      return <Camera size={16} className="text-blue-400" />
    case "system":
      return <Server size={16} className="text-green-400" />
    case "user":
      return <User size={16} className="text-purple-400" />
    case "door":
      return <DoorClosed size={16} className="text-red-400" />
    case "schedule":
      return <Clock size={16} className="text-indigo-400" />
    default:
      return <Bell size={16} className="text-white/60" />
  }
}

const getSeverityColor = (severity: Activity["severity"]) => {
  switch (severity) {
    case "high":
      return "bg-red-500/20 text-red-400"
    case "medium":
      return "bg-yellow-500/20 text-yellow-400"
    case "low":
      return "bg-green-500/20 text-green-400"
    default:
      return "bg-white/20 text-white/60"
  }
}

const initialActivities: Activity[] = [
  { id: 1, type: "alert", message: "Motion detected in Living Room", time: "2 min ago", severity: "high" },
  { id: 2, type: "camera", message: "Camera went offline", time: "15 min ago", severity: "medium" },
  { id: 3, type: "system", message: "System update completed", time: "1 hour ago", severity: "low" },
  { id: 4, type: "user", message: "User John logged in", time: "2 hours ago", severity: "low" },
  { id: 5, type: "door", message: "Front door opened", time: "3 hours ago", severity: "medium" },
  { id: 6, type: "schedule", message: "Night mode activated", time: "8 hours ago", severity: "low" },
]

export default function RecentActivity() {
  const [activities] = useState<Activity[]>(initialActivities)
  const [filter, setFilter] = useState<Activity["type"] | "all">("all")
  const [showFilters, setShowFilters] = useState(false)

  const filteredActivities = filter === "all" ? activities : activities.filter((activity) => activity.type === filter)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 h-full"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-light">Recent Activity</h2>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"
        >
          <Filter size={16} />
        </button>
      </div>
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mb-4"
          >
            <div className="flex flex-wrap gap-2">
              {["all", "alert", "camera", "system", "user", "door", "schedule"].map((type) => (
                <button
                  key={type}
                  onClick={() => setFilter(type as Activity["type"] | "all")}
                  className={`px-3 py-1 rounded-full text-xs ${
                    filter === type ? "bg-white/20 text-white" : "bg-white/5 text-white/60 hover:bg-white/10"
                  } transition-colors`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-16rem)]">
        <AnimatePresence initial={false}>
          {filteredActivities.map((activity) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="flex items-start space-x-3 bg-white/5 rounded-lg p-3"
            >
              <div className="mt-1">{getIcon(activity.type)}</div>
              <div className="flex-grow">
                <p className="text-sm text-white/80">{activity.message}</p>
                <div className="flex justify-between items-center mt-1">
                  <p className="text-xs text-white/60">{activity.time}</p>
                  <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(activity.severity)}`}>
                    {activity.severity}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

