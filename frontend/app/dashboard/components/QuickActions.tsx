/**
 * QuickActions Component
 *
 * This component displays a grid of quick action buttons that allow users
 * to perform common tasks or access frequently used features of the application.
 */

"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Plus, Clock, Bell, Settings, X } from "lucide-react"
import { useRouter } from "next/navigation"
import Link from "next/link"

interface Action {
  label: string
  icon: typeof Plus
  color: string
  description: string
  link: string
}

const actions: Action[] = [
  {
    label: "Add Alert",
    icon: Plus,
    color: "bg-blue-500",
    description: "Set up a new custom alert for your security system.",
    link: "/alerts/new",
  },
  {
    label: "View Timeline",
    icon: Clock,
    color: "bg-green-500",
    description: "Access a chronological view of all security events.",
    link: "/event-timeline",
  },
  {
    label: "Manage Notifications",
    icon: Bell,
    color: "bg-purple-500",
    description: "Customize your notification preferences and channels.",
    link: "/settings",
  },
  {
    label: "System Settings",
    icon: Settings,
    color: "bg-pink-500",
    description: "Access and modify core system configurations and preferences.",
    link: "/settings",
  },
]

export default function QuickActions() {
  const [activeAction, setActiveAction] = useState<Action | null>(null)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10"
    >
      <h2 className="text-2xl font-light mb-4">Quick Actions</h2>
      <div className="grid grid-cols-2 gap-4">
        {actions.map((action) => (
          <Link
            key={action.label}
            href={action.link}
            className={`flex flex-col items-center justify-center p-4 rounded-lg ${action.color} bg-opacity-20 hover:bg-opacity-30 transition-colors`}
          >
            <action.icon size={24} className="mb-2" />
            <span className="text-sm text-center">{action.label}</span>
          </Link>
        ))}
      </div>
      <AnimatePresence>
        {activeAction && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
          >
            <motion.div
              initial={{ y: 50 }}
              animate={{ y: 0 }}
              exit={{ y: 50 }}
              className={`${activeAction.color} bg-opacity-20 backdrop-blur-md p-6 rounded-lg max-w-md w-full`}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-medium">{activeAction.label}</h3>
                <button
                  onClick={() => setActiveAction(null)}
                  className="text-white/60 hover:text-white transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <p className="text-white/80 mb-4">{activeAction.description}</p>
              <div className="flex justify-end space-x-2">
                <button
                  className="px-4 py-2 bg-white/10 rounded-md hover:bg-white/20 transition-colors"
                  onClick={() => setActiveAction(null)}
                >
                  Close
                </button>
                <Link
                  href={activeAction.link}
                  className="px-4 py-2 bg-white/20 rounded-md hover:bg-white/30 transition-colors"
                  onClick={() => setActiveAction(null)}
                >
                  Go to {activeAction.label}
                </Link>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

