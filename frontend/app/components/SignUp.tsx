import { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Lock, Mail, ArrowRight, AlertCircle, User, CheckCircle, XCircle } from 'lucide-react'
import PasswordStrengthMeter from './PasswordStrengthMeter'
import { usePasswordStrength } from '../hooks/usePasswordStrength'

interface SignUpProps {
  onSwitchToLogin: () => void
}

export default function SignUp({ onSwitchToLogin }: SignUpProps) {
  const [showPassword, setShowPassword] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isEmailValid, setIsEmailValid] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const { strength, feedback } = usePasswordStrength(password)

  const validateEmail = (email: string) => {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return re.test(email)
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value
    setEmail(newEmail)
    setIsEmailValid(validateEmail(newEmail))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    setMessage(null)
    
    if (!name || !email || !password) {
      setError('Please fill in all fields')
      setIsLoading(false)
      return
    }

    if (!isEmailValid) {
      setError('Please enter a valid email address')
      setIsLoading(false)
      return
    }

    if (strength < 3) {
      setError('Please use a stronger password')
      setIsLoading(false)
      return
    }

    try {
      // Simulate API request
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Simulating a successful sign up
      setMessage({ type: 'success', text: 'Account created successfully. Redirecting to login...' })
      setTimeout(() => {
        onSwitchToLogin()
      }, 2000)
    } catch {
      setMessage({ type: 'error', text: 'An error occurred during sign up. Please try again.' })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="text-white"
    >
      <h2 className="text-4xl font-light text-white mb-2 text-center">Create Account</h2>
      <p className="text-white/60 text-center mb-6">Join WatchDog and enhance your security</p>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="relative">
          <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50" size={18} />
          <input
            id="name"
            name="name"
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50 transition duration-300"
            placeholder="Full Name"
            aria-label="Full Name"
          />
        </div>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50" size={18} />
          <input
            id="email"
            name="email"
            type="email"
            required
            value={email}
            onChange={handleEmailChange}
            className={`w-full pl-10 pr-4 py-3 bg-white/10 border ${isEmailValid ? 'border-white/20' : 'border-red-500'} rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50 transition duration-300`}
            placeholder="Email"
            aria-label="Email"
            aria-invalid={!isEmailValid}
          />
          {!isEmailValid && (
            <p className="mt-1 text-xs text-red-400">Please enter a valid email address</p>
          )}
        </div>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50" size={18} />
          <input
            id="password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full pl-10 pr-10 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50 transition duration-300"
            placeholder="Password"
            aria-label="Password"
          />
          <button
            type="button"
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 hover:text-white transition-colors"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
        <PasswordStrengthMeter strength={strength} feedback={feedback} />
        {error && (
          <div className="flex items-center space-x-2 text-red-400 text-sm">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          type="submit"
          disabled={!isEmailValid || strength < 3 || isLoading}
          className="w-full bg-white text-black py-3 px-4 rounded-lg hover:bg-gray-200 transition duration-300 font-medium flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <motion.div
              className="h-5 w-5 border-2 border-black border-t-transparent rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
          ) : (
            <>
              Sign Up
              <ArrowRight className="ml-2" size={18} />
            </>
          )}
        </motion.button>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className={`mt-6 p-4 rounded-lg shadow-lg flex items-center space-x-3 ${
              message.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle className="flex-shrink-0" size={20} />
            ) : (
              <XCircle className="flex-shrink-0" size={20} />
            )}
            <span className="text-sm font-medium">{message.text}</span>
          </motion.div>
        )}
      </form>
      <div className="mt-6 text-center">
        <p className="text-white/60 text-sm">
          Already have an account?{' '}
          <button onClick={onSwitchToLogin} className="text-white hover:underline transition-colors">
            Log in
          </button>
        </p>
      </div>
    </motion.div>
  )
}

