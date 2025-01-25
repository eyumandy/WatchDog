import { useState } from 'react'
import { motion } from 'framer-motion'

export default function AccountSettings() {
  const [name, setName] = useState('John Doe')
  const [email, setEmail] = useState('john.doe@example.com')

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <h2 className="text-2xl font-light mb-4">Account Settings</h2>
      <div className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-white/80 mb-1">
            Name
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-white/20"
          />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-white/20"
          />
        </div>
        <div>
          <button className="px-4 py-2 bg-white/10 text-white rounded-md hover:bg-white/20 transition-colors">
            Change Password
          </button>
        </div>
      </div>
    </motion.div>
  )
}

