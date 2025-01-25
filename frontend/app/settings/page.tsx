/**
 * Settings Page
 *
 * This page provides access to various system configuration options.
 * Users can modify account settings, notification preferences, and display options.
 *
 * Features:
 * - Tab-based navigation
 * - Account management
 * - Notification preferences
 * - Display customization
 */

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import NetworkBackground from "../components/NetworkBackground"
import DashboardHeader from "../components/DashboardHeader"
import SettingsTabs from "../components/SettingsTabs"

export default function Settings() {
  const [activeTab, setActiveTab] = useState("Settings")

  return (
    <div className="min-h-screen text-white overflow-hidden">
      <NetworkBackground
        color="rgb(63, 23, 121)" // Dark purple background for settings
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
          <h1 className="text-3xl font-light mb-8">Settings</h1>
          <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10">
            <SettingsTabs />
          </div>
        </motion.div>
      </div>
    </div>
  )
}

