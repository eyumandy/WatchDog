/**
 * Hero section with animated triangle and fluid background
 */
'use client'

import { motion } from "framer-motion"
import { useRouter } from "next/navigation"

const Triangle = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-100 h-100"
    initial={{ scale: 0.8, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    transition={{ duration: 1 }}
  >
    <motion.path
      d="M50 10 L90 80 L10 80 Z"
      fill="none"
      stroke="white"
      strokeWidth="1"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 2, ease: "easeInOut" }}
    />
  </motion.svg>
)

export default function Hero() {
  const router = useRouter()

  return (
    <div className="relative min-h-screen flex flex-col justify-center items-center">      
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
        className="text-center relative z-10 max-w-4xl px-4 sm:px-6 lg:px-8"
      >
        <Triangle />
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="text-6xl sm:text-7xl md:text-8xl font-extralight mb-6 tracking-tighter text-white"
        >
          WatchDog
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="text-lg sm:text-xl text-gray-300 mb-12 max-w-2xl mx-auto font-light tracking-wide"
        >
          Advanced surveillance, simplified.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
        >
          <button
            onClick={() => router.push("/login")}
            className="bg-white text-black font-medium py-3 px-8 rounded-full transition duration-300 ease-in-out hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-opacity-50 text-sm uppercase tracking-wider"
          >
            Get Started
          </button>
        </motion.div>
      </motion.div>
    </div>
  )
}