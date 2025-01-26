"use client"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import Image from "next/image"
import { format } from "date-fns"
import { securityLogs } from "./SecurityLogEntries"
import {
  AlertCircle,
  Video,
  Server,
  User,
  DoorClosed,
  Clock,
  Play,
  Pause,
  Maximize2,
  Minimize2,
  Volume2,
  VolumeX,
  SkipBack,
  SkipForward,
  Camera,
} from "lucide-react"

interface SecurityLogDetailsProps {
  selectedLogId: number | null
}

const getLogIcon = (type: string) => {
  switch (type) {
    case "alert":
      return <AlertCircle size={24} className="text-red-400" />
    case "camera":
      return <Video size={24} className="text-blue-400" />
    case "system":
      return <Server size={24} className="text-green-400" />
    case "user":
      return <User size={24} className="text-purple-400" />
    case "door":
      return <DoorClosed size={24} className="text-yellow-400" />
    case "schedule":
      return <Clock size={24} className="text-indigo-400" />
    default:
      return null
  }
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "high":
      return "bg-red-500/20 text-red-400"
    case "medium":
      return "bg-yellow-500/20 text-yellow-400"
    case "low":
      return "bg-green-500/20 text-green-400"
    default:
      return "bg-gray-500/20 text-gray-400"
  }
}

export default function SecurityLogDetails({ selectedLogId }: SecurityLogDetailsProps) {
  const [isVideoFullscreen, setIsVideoFullscreen] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(60) // Assuming 60 seconds video duration
  const [volume, setVolume] = useState(1)
  const [showVolumeSlider, setShowVolumeSlider] = useState(false)
  const videoRef = useRef<HTMLDivElement>(null)
  const selectedLog = securityLogs.find((log) => log.id === selectedLogId)

  const detailsVariants = {
    hidden: { opacity: 0, x: 20 },
    visible: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  }

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prevTime) => {
          if (prevTime >= duration) {
            setIsPlaying(false)
            return 0
          }
          return prevTime + 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isPlaying, duration])

  const togglePlay = () => setIsPlaying(!isPlaying)
  const toggleMute = () => setIsMuted(!isMuted)
  const toggleFullscreen = () => {
    if (!videoRef.current) return
    if (!document.fullscreenElement) {
      videoRef.current.requestFullscreen()
      setIsVideoFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsVideoFullscreen(false)
    }
  }

  const handleTimelineChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = Number.parseInt(e.target.value)
    setCurrentTime(newTime)
    if (!isPlaying) setIsPlaying(true)
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = Number.parseFloat(e.target.value)
    setVolume(newVolume)
    setIsMuted(newVolume === 0)
  }

  const skipBackward = () => {
    setCurrentTime((prevTime) => Math.max(prevTime - 10, 0))
  }

  const skipForward = () => {
    setCurrentTime((prevTime) => Math.min(prevTime + 10, duration))
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = time % 60
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
  }

  if (!selectedLog) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-center h-full"
      >
        <p className="text-white/60">Select a log entry to view details</p>
      </motion.div>
    )
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={selectedLog.id}
        variants={detailsVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
        transition={{ duration: 0.3 }}
        className="space-y-6 h-full overflow-y-auto"
      >
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.3 }}
          className="flex items-center justify-between"
        >
          <div className="flex items-center space-x-4">
            {getLogIcon(selectedLog.type)}
            <h2 className="text-2xl font-light">
              {selectedLog.type.charAt(0).toUpperCase() + selectedLog.type.slice(1)} Event
            </h2>
          </div>
          <span className={`text-sm px-3 py-1 rounded-full ${getSeverityColor(selectedLog.severity)}`}>
            {selectedLog.severity.toUpperCase()}
          </span>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.3 }}
              className="bg-white/5 rounded-lg p-4 space-y-4"
            >
              <p className="text-lg text-white/90">{selectedLog.description}</p>
              <div className="flex justify-between text-sm text-white/60">
                <span>{format(new Date(selectedLog.timestamp), "MMMM d, yyyy HH:mm:ss")}</span>
                <span>{selectedLog.location}</span>
              </div>
            </motion.div>

            {selectedLog.involvedPersons.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.3 }}
                className="bg-white/5 rounded-lg p-4"
              >
                <h3 className="text-lg font-medium mb-4">Involved Persons</h3>
                <div className="flex space-x-4">
                  {selectedLog.involvedPersons.map((person, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.4 + index * 0.1, duration: 0.3 }}
                      className="flex flex-col items-center"
                    >
                      <Image
                        src={person.imageUrl || "/placeholder.svg"}
                        alt={person.name}
                        width={60}
                        height={60}
                        className="rounded-full mb-2"
                      />
                      <span className="text-sm text-white/80">{person.name}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {selectedLog.additionalInfo && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.3 }}
                className="bg-white/5 rounded-lg p-4"
              >
                <h3 className="text-lg font-medium mb-2">Additional Information</h3>
                <p className="text-white/80">{selectedLog.additionalInfo}</p>
              </motion.div>
            )}
          </div>

          <motion.div
            ref={videoRef}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.3 }}
            className={`bg-white/5 rounded-lg overflow-hidden ${isVideoFullscreen ? "fixed inset-4 z-50" : "h-[400px]"}`}
          >
            <div className="relative w-full h-full bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
              <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
              <div className="relative z-10 flex flex-col items-center justify-center space-y-4">
                <Camera size={48} className="text-white/60" />
                <div className="text-white/80 text-lg font-light">Camera Feed</div>
                <div className="text-white/60 text-sm">{selectedLog.location}</div>
              </div>
              <div className="absolute inset-x-4 bottom-4 bg-black/70 backdrop-blur-md rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex space-x-2">
                    <button
                      onClick={togglePlay}
                      className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"
                      aria-label={isPlaying ? "Pause video" : "Play video"}
                    >
                      {isPlaying ? (
                        <Pause size={20} className="text-white" />
                      ) : (
                        <Play size={20} className="text-white" />
                      )}
                    </button>
                    <button
                      onClick={skipBackward}
                      className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"
                      aria-label="Skip backward 10 seconds"
                    >
                      <SkipBack size={20} className="text-white" />
                    </button>
                    <button
                      onClick={skipForward}
                      className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"
                      aria-label="Skip forward 10 seconds"
                    >
                      <SkipForward size={20} className="text-white" />
                    </button>
                  </div>
                  <div className="text-white/80 text-sm">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </div>
                  <div className="flex space-x-2">
                    <div className="relative">
                      <button
                        onClick={() => setShowVolumeSlider(!showVolumeSlider)}
                        onMouseEnter={() => setShowVolumeSlider(true)}
                        onMouseLeave={() => setShowVolumeSlider(false)}
                        className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"
                        aria-label={isMuted ? "Unmute" : "Mute"}
                      >
                        {isMuted ? (
                          <VolumeX size={20} className="text-white" />
                        ) : (
                          <Volume2 size={20} className="text-white" />
                        )}
                      </button>
                      {showVolumeSlider && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-24 h-4 bg-black/80 rounded-full flex items-center px-2">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={volume}
                            onChange={handleVolumeChange}
                            className="w-full h-1 bg-white/20 rounded-full appearance-none cursor-pointer"
                            style={{
                              background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${volume * 100}%, rgba(255, 255, 255, 0.2) ${volume * 100}%, rgba(255, 255, 255, 0.2) 100%)`,
                            }}
                          />
                        </div>
                      )}
                    </div>
                    <button
                      onClick={toggleFullscreen}
                      className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"
                      aria-label={isVideoFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                    >
                      {isVideoFullscreen ? (
                        <Minimize2 size={20} className="text-white" />
                      ) : (
                        <Maximize2 size={20} className="text-white" />
                      )}
                    </button>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    min="0"
                    max={duration}
                    value={currentTime}
                    onChange={handleTimelineChange}
                    className="w-full h-1 bg-white/20 rounded-full appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(currentTime / duration) * 100}%, rgba(255, 255, 255, 0.2) ${(currentTime / duration) * 100}%, rgba(255, 255, 255, 0.2) 100%)`,
                    }}
                  />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

