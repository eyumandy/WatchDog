/**
 * SystemHealth Component
 *
 * This component displays the current health status of various system components
 * in a clean, user-friendly interface. It allows for expandable details for each
 * system component.
 */

"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { CheckCircle, AlertCircle, HelpCircle, Server, HardDrive, Wifi, Camera, ChevronDown } from "lucide-react"

interface HealthItem {
  label: string
  icon: typeof Server
  status: "healthy" | "warning" | "critical"
  details: string
}

const initialHealthItems: HealthItem[] = [
  { label: "Server", icon: Server, status: "healthy", details: "All systems operational" },
  { label: "Storage", icon: HardDrive, status: "healthy", details: "Sufficient space available" },
  { label: "Network", icon: Wifi, status: "healthy", details: "1Gbps up/down" },
  { label: "Camera", icon: Camera, status: "healthy", details: "Online and functioning" },
]

/**
 * Returns the appropriate icon component based on the health status
 * @param status - The current health status
 * @returns A React component representing the status icon
 */
const getStatusIcon = (status: HealthItem["status"]) => {
  switch (status) {
    case "healthy":
      return <CheckCircle size={16} className="text-green-400" />
    case "warning":
      return <AlertCircle size={16} className="text-yellow-400" />
    case "critical":
      return <AlertCircle size={16} className="text-red-400" />
    default:
      return <HelpCircle size={16} className="text-white/60" />
  }
}

export default function SystemHealth() {
  const [expanded, setExpanded] = useState<string | null>(null)
  const [healthData] = useState<HealthItem[]>(initialHealthItems)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10"
    >
      <h2 className="text-2xl font-light mb-4">System Health</h2>
      <div className="space-y-4">
        {healthData.map((item) => (
          <motion.div
            key={item.label}
            layout
            onClick={() => setExpanded(expanded === item.label ? null : item.label)}
            className="bg-white/5 rounded-lg p-4 cursor-pointer hover:bg-white/10 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <item.icon size={20} className="text-white/60" />
                <div>
                  <p className="text-sm font-medium">{item.label}</p>
                  <p className="text-xs text-white/60">{item.details}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(item.status)}
                <ChevronDown
                  size={16}
                  className={`text-white/60 transform transition-transform ${
                    expanded === item.label ? "rotate-180" : ""
                  }`}
                />
              </div>
            </div>
            <AnimatePresence>
              {expanded === item.label && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="mt-4"
                >
                  <div className="text-sm text-white/80">
                    <p>Status: {item.status}</p>
                    <p>Last updated: {new Date().toLocaleTimeString()}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

