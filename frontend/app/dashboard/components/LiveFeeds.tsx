/**
 * LiveFeeds Component
 *
 * This component displays a live feed from the main camera in the security system.
 * It includes controls for play/pause, fullscreen, mute, and settings.
 */

"use client"

import { useState, useCallback } from "react"
import { Pause, Play, Maximize2, Minimize2, Volume2, VolumeX, Settings, AlertCircle, X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

export default function LiveFeeds() {
  const [isPaused, setIsPaused] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [cameraStatus, setCameraStatus] = useState<"Online" | "Offline">("Online")
  const [isEnlarged, setIsEnlarged] = useState(false)

  /**
   * Toggles fullscreen mode for the document
   */
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
    } else if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }, [])

  const toggleEnlarged = useCallback(() => {
    setIsEnlarged((prev) => !prev)
    // Trigger a resize event to ensure proper rendering
    window.dispatchEvent(new Event("resize"))
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`rounded-2xl p-6 border border-white/10 transition-all duration-300 ${
        isEnlarged ? "fixed inset-4 z-50 bg-gray-900" : "bg-white/5 backdrop-blur-md"
      }`}
    >
      <h2 className="text-2xl font-light mb-4">Live Feed</h2>
      <div
        className={`relative ${isEnlarged ? "h-[calc(100%-2rem)]" : "aspect-video"} bg-black/50 rounded-xl overflow-hidden`}
      >
        <div className="absolute top-2 left-2 z-10 flex items-center space-x-2">
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${
              cameraStatus === "Online" ? "bg-green-500" : "bg-red-500"
            }`}
          >
            {cameraStatus.toUpperCase()}
          </span>
          <span className="text-sm text-white/80">Main Camera</span>
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          {cameraStatus === "Online" ? (
            <span className="text-white/60">Camera Feed: Main Camera</span>
          ) : (
            <div className="flex items-center space-x-2 text-red-400">
              <AlertCircle size={20} />
              <span>Camera Offline</span>
            </div>
          )}
        </div>
        {isEnlarged && (
          <button
            onClick={toggleEnlarged}
            className="absolute top-2 right-2 p-1 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
            aria-label="Close enlarged view"
          >
            <X size={16} />
          </button>
        )}
        <div className="absolute bottom-2 left-2 right-2 flex justify-between items-center z-10">
          <div className="flex space-x-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={() => setIsPaused(!isPaused)}
                    className="p-1 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                    aria-label={isPaused ? "Play" : "Pause"}
                  >
                    {isPaused ? <Play size={16} /> : <Pause size={16} />}
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{isPaused ? "Play" : "Pause"}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={toggleEnlarged}
                    className="p-1 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                    aria-label={isEnlarged ? "Minimize" : "Enlarge"}
                  >
                    {isEnlarged ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{isEnlarged ? "Minimize" : "Enlarge"}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={() => setIsMuted(!isMuted)}
                    className="p-1 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                    aria-label={isMuted ? "Unmute" : "Mute"}
                  >
                    {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{isMuted ? "Unmute" : "Mute"}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="p-1 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                  aria-label="Toggle settings"
                >
                  <Settings size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Settings</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.2 }}
            className={`mt-4 p-4 bg-white/10 rounded-lg ${isEnlarged ? "absolute bottom-4 left-4 right-4" : ""}`}
          >
            <h3 className="text-lg font-medium mb-2">Camera Settings</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span>Motion Detection</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <span>Night Vision</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

