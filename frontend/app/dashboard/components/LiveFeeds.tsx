import { useState, useCallback, useEffect, useRef } from "react"
import { Pause, Play, Maximize2, Minimize2, Volume2, VolumeX, Settings, AlertCircle, X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

const STREAM_URL = "http://localhost:5000/video_feed"

export default function LiveFeeds() {
  const [isPaused, setIsPaused] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [cameraStatus, setCameraStatus] = useState("Online")
  const [isEnlarged, setIsEnlarged] = useState(false)
  const videoRef = useRef(null)

  useEffect(() => {
    // Check camera status periodically
    const checkStatus = async () => {
      try {
        setCameraStatus("Online")
      } catch (error) {
        setCameraStatus("Offline")
      }
    }

    const interval = setInterval(checkStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
    } else if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }, [])

  const toggleEnlarged = useCallback(() => {
    setIsEnlarged((prev) => !prev)
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

        {/* Video Feed */}
        {cameraStatus === "Online" && !isPaused ? (
          <img
            ref={videoRef}
            src={STREAM_URL}
            className="w-full h-full object-cover"
            alt="Live Camera Feed"
            style={{
              imageRendering: 'optimizespeed' as any,
              transform: 'translate3d(0,0,0)',
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
            }}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            {cameraStatus === "Online" ? (
              <div className="flex items-center space-x-2 text-white/60">
                <Pause size={20} />
                <span>Feed Paused</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-red-400">
                <AlertCircle size={20} />
                <span>Camera Offline</span>
              </div>
            )}
          </div>
        )}

        {isEnlarged && (
          <button
            onClick={toggleEnlarged}
            className="absolute top-2 right-2 p-1 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
            aria-label="Close enlarged view"
          >
            <X size={16} />
          </button>
        )}

        {/* Controls */}
        <div className="absolute bottom-2 left-2 right-2 flex justify-between items-center z-10">
          <div className="flex space-x-2">
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

      {/* Settings Panel */}
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