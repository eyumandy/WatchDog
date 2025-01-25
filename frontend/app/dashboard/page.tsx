/**
 * Dashboard Page
 *
 * This component serves as the main dashboard for the WatchDog application.
 * It provides an overview of the security system, including live feeds,
 * system health, quick actions, and recent activity.
 *
 * The dashboard uses a responsive grid layout to organize its components
 * and ensures a consistent user experience across different device sizes.
 */

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import DashboardHeader from "../components/DashboardHeader"
import LiveFeeds from "./components/LiveFeeds"
import SystemHealth from "./components/SystemHealth"
import RecentActivity from "./components/RecentActivity"
import QuickActions from "./components/QuickActions"
import NetworkBackground from "../components/NetworkBackground"
import Greeting from "../components/Greeting"

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("Dashboard")

  // Helper function to determine the time of day for the greeting
  const getTimeOfDay = () => {
    const hour = new Date().getHours()
    if (hour < 12) return "morning"
    if (hour < 18) return "afternoon"
    return "evening"
  }

  return (
    <div className="min-h-screen text-white overflow-hidden">
      {/* Dark blue background for the dashboard to create a professional and calm atmosphere */}
      <NetworkBackground
        color="rgb(31, 39, 75)"
        nodeColor="rgba(255, 255, 255, 0.4)"
        lineColor="rgba(255, 255, 255, 0.15)"
      />
      <div className="relative z-10">
        <DashboardHeader activeTab={activeTab} setActiveTab={setActiveTab} />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="container mx-auto px-4 py-8"
        >
          {/* Greeting component to welcome the user */}
          <Greeting timeOfDay={getTimeOfDay()} />

          {/* Main dashboard grid layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
            {/* Left column: Live Feeds and smaller components */}
            <div className="lg:col-span-2 space-y-8">
              <LiveFeeds />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <SystemHealth />
                <QuickActions />
              </div>
            </div>
            {/* Right column: Recent Activity */}
            <div className="space-y-8">
              <RecentActivity />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

