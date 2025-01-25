/**
 * EventFilters Component
 *
 * This component provides filtering capabilities for the event timeline.
 * Users can filter events by type (All, Motion, Alerts, System) to focus
 * on specific categories of security events.
 *
 * Features:
 * - Multiple filter categories
 * - Active filter indication
 * - Smooth transitions between filter states
 */

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Filter } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

export type FilterType = "All" | "Motion" | "Alerts" | "System"

interface EventFiltersProps {
  onFilterChange?: (filter: FilterType) => void
}

export default function EventFilters({ onFilterChange }: EventFiltersProps) {
  const [activeFilter, setActiveFilter] = useState<FilterType>("All")
  const filters: FilterType[] = ["All", "Motion", "Alerts", "System"]

  const handleFilterChange = (filter: FilterType) => {
    setActiveFilter(filter)
    onFilterChange?.(filter)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mb-6 flex items-center space-x-4"
    >
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>
            <Filter size={20} className="text-white/60" />
          </TooltipTrigger>
          <TooltipContent>
            <p>Filter events by type</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
      <div className="flex space-x-2">
        {filters.map((filter) => (
          <button
            key={filter}
            onClick={() => handleFilterChange(filter)}
            className={`px-3 py-1 rounded-full text-sm ${
              activeFilter === filter ? "bg-white/20 text-white" : "bg-white/5 text-white/60 hover:bg-white/10"
            } transition-colors`}
          >
            {filter}
          </button>
        ))}
      </div>
    </motion.div>
  )
}

