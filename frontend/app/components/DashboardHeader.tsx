"use client"

import { useState, useRef, useEffect } from "react"
import { LogOut, Bell, ChevronDown } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"

interface DashboardHeaderProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

export default function DashboardHeader({ activeTab, setActiveTab }: DashboardHeaderProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const router = useRouter()
  const dropdownRef = useRef<HTMLDivElement>(null)
  const tabs = ["Dashboard", "Event Timeline", "Settings"]

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
            <button className="text-white/60 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10">
              <Bell size={20} />
            </button>
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

