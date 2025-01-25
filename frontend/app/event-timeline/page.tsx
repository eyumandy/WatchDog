/**
 * Event Timeline Page
 *
 * This page displays a chronological view of all security events and activities
 * within the WatchDog system. It provides filtering capabilities and real-time
 * updates of security events.
 *
 * Features:
 * - Event filtering by type and severity
 * - Chronological event listing
 * - Real-time event updates
 */

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import NetworkBackground from "../components/NetworkBackground"
import DashboardHeader from "../components/DashboardHeader"
import EventList from "../components/EventList"
import EventFilters from "../components/EventFilters"

export default function EventTimeline() {
  const [activeTab, setActiveTab] = useState("Event Timeline")

  return (
    <div className="min-h-screen text-white overflow-hidden">
      <NetworkBackground
        color="rgb(20, 83, 45)" // Dark green background for the event timeline
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
          <h1 className="text-3xl font-light mb-8">Event Timeline</h1>
          <div className="mb-8">
            <EventFilters />
          </div>
          <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10">
            <EventList />
          </div>
        </motion.div>
      </div>
    </div>
  )
}

