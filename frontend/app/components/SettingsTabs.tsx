/**
 * SettingsTabs Component
 *
 * This component provides a tabbed interface for accessing different
 * settings categories within the WatchDog system.
 *
 * Features:
 * - Tab-based navigation
 * - Smooth transitions between tabs
 * - Organized settings categories
 */

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import AccountSettings from "./AccountSettings"
import NotificationSettings from "./NotificationSettings"
import DisplaySettings from "./DisplaySettings"

type TabType = "Account" | "Notifications" | "Display"

export default function SettingsTabs() {
  const [activeTab, setActiveTab] = useState<TabType>("Account")
  const tabs: TabType[] = ["Account", "Notifications", "Display"]

  const TabContent = () => {
    switch (activeTab) {
      case "Account":
        return <AccountSettings />
      case "Notifications":
        return <NotificationSettings />
      case "Display":
        return <DisplaySettings />
    }
  }

  return (
    <div>
      <div className="mb-6 flex space-x-4 border-b border-white/10">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm ${
              activeTab === tab ? "text-white border-b-2 border-white" : "text-white/60 hover:text-white"
            } transition-colors`}
          >
            {tab}
          </button>
        ))}
      </div>
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <TabContent />
      </motion.div>
    </div>
  )
}

