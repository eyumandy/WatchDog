/**
 * Login Page with animated background and modern glassmorphic design
 */
"use client"

import { useState } from "react"
import { Eye, EyeOff, Lock, Mail, ArrowRight, AlertCircle, Fingerprint, ShieldCheck } from "lucide-react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import FuturisticBackground from "../components/FuturisticBackground"
import PasswordStrengthMeter from "../components/PasswordStrengthMeter"
import { usePasswordStrength } from "../hooks/usePasswordStrength"

export default function Login() {
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { strength, feedback } = usePasswordStrength(password)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    router.push("/dashboard")
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-black overflow-hidden">
      <FuturisticBackground />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 bg-gray-700/25 backdrop-blur-xl p-8 rounded-2xl w-full max-w-md mx-4"
      >
        <div className="text-center mb-8">
          <h2 className="text-4xl font-light text-white mb-2">Welcome Back</h2>
          <p className="text-gray-400">Sign in to access your WatchDog dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="email"
              placeholder="Email"
              className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400"
            />
          </div>

          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-10 py-3 text-white placeholder-gray-400"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          <PasswordStrengthMeter strength={strength} feedback={feedback} />

          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={() => setRememberMe(!rememberMe)}
                className="mr-2"
              />
              <span className="text-sm text-gray-400">Remember me</span>
            </label>
            <a href="#" className="text-sm text-gray-400 hover:text-white">
              Forgot password?
            </a>
          </div>

          <button
            type="submit"
            className="w-full bg-white text-black py-3 rounded-lg hover:bg-gray-200 transition-colors font-medium flex items-center justify-center"
          >
            {isLoading ? (
              <motion.div
                className="h-5 w-5 border-2 border-black border-t-transparent rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
            ) : (
              <>
                Sign In <ArrowRight className="ml-2" size={18} />
              </>
            )}
          </button>

          <button
            type="button"
            className="w-full bg-transparent border border-white/20 text-white py-3 rounded-lg hover:bg-white/5 transition-colors flex items-center justify-center mt-4"
          >
            <Fingerprint className="mr-2" size={18} />
            Sign in with Biometrics
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-400">
          <p>
            Don't have an account?{" "}
            <a href="/signup" className="text-white hover:underline">
              Sign up
            </a>
          </p>
          <div className="flex items-center justify-center mt-4 text-gray-400">
            <ShieldCheck size={16} className="mr-2" />
            <span>Secure, encrypted connection</span>
          </div>
        </div>
      </motion.div>
    </div>
  )
}