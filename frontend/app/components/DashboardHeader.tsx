"use client"

import { useState, useRef, useEffect } from "react"
import { LogOut, Bell, ChevronDown, X } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"

interface DashboardHeaderProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

export default function DashboardHeader({ activeTab, setActiveTab }: DashboardHeaderProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isNotificationDropdownOpen, setIsNotificationDropdownOpen] = useState(false)
  const router = useRouter()
  const dropdownRef = useRef<HTMLDivElement>(null)
  const notificationDropdownRef = useRef<HTMLDivElement>(null)
  const tabs = ["Dashboard", "Event Timeline", "Security Logs", "Settings"]

  const handleLogout = () => {
    console.log("Logout clicked") // Debug log
    setIsDropdownOpen(false)
    router.push("/")
  }

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
      if (notificationDropdownRef.current && !notificationDropdownRef.current.contains(event.target as Node)) {
        setIsNotificationDropdownOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  return (
    <header className="relative z-50 bg-black/30 backdrop-blur-md border-b border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <nav>
            <ul className="flex space-x-6">
              {tabs.map((tab) => (
                <li key={tab}>
                  <Link
                    href={tab === "Dashboard" ? "/dashboard" : `/${tab.toLowerCase().replace(" ", "-")}`}
                    className={`text-sm font-medium transition-colors ${
                      activeTab === tab ? "text-white" : "text-white/60 hover:text-white"
                    }`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <div className="flex items-center space-x-4">
            <div className="relative" ref={notificationDropdownRef}>
              <button
                onClick={() => setIsNotificationDropdownOpen(!isNotificationDropdownOpen)}
                className="text-white/60 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                aria-label="Notifications"
              >
                <Bell size={20} />
              </button>
              <AnimatePresence>
                {isNotificationDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 mt-2 w-64 bg-gray-900 rounded-md shadow-lg py-1 z-50 border border-white/10"
                    style={{ top: "100%" }}
                  >
                    <div className="p-4 text-center bg-gray-900/70">
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="text-sm font-medium text-white">Notifications</h3>
                        <button
                          onClick={() => setIsNotificationDropdownOpen(false)}
                          className="text-white/60 hover:text-white transition-colors"
                        >
                          <X size={16} />
                        </button>
                      </div>
                      <div className="bg-white/5 rounded-md p-3">
                        <p className="text-sm text-white/80">No new notifications</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center space-x-2 px-3 py-2 rounded-md bg-white/10 text-white hover:bg-white/20 active:bg-white/30 transition-colors cursor-pointer"
              >
                <span>JD</span>
                <ChevronDown
                  size={16}
                  className={`transform transition-transform ${isDropdownOpen ? "rotate-180" : ""}`}
                />
              </button>
              <AnimatePresence>
                {isDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 mt-2 w-56 bg-gray-900 rounded-md shadow-lg py-1 z-50 border border-white/10"
                    style={{ top: "100%" }}
                  >
                    <div className="px-4 py-3 border-b border-white/10">
                      <p className="text-sm font-medium text-white">John Doe</p>
                      <p className="text-xs text-white/60 mt-1">john.doe@example.com</p>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-white/80 hover:bg-white/10 active:bg-white/20 transition-colors flex items-center cursor-pointer"
                    >
                      <LogOut className="mr-2" size={16} />
                      Log out
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

