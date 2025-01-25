import { motion } from 'framer-motion'

interface PasswordStrengthMeterProps {
  strength: number
  feedback: string[]
}

const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong']
const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-blue-500']

export default function PasswordStrengthMeter({ strength, feedback }: PasswordStrengthMeterProps) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm text-white/60">Password Strength</span>
        <span className="text-sm text-white/60">{strengthLabels[strength]}</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <motion.div 
          className={`h-full ${strengthColors[strength]}`}
          initial={{ width: 0 }}
          animate={{ width: `${((strength + 1) / 5) * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
      {feedback.length > 0 && (
        <motion.ul
          initial="initial"
          animate="animate"
          variants={{
            animate: { transition: { staggerChildren: 0.05 } }
          }}
          className="mt-2 space-y-1"
        >
          {feedback.map((tip, index) => (
            <motion.li
              key={index}
              variants={{
                initial: { opacity: 0, x: -20 },
                animate: { opacity: 1, x: 0 }
              }}
              className="text-xs text-white/60"
            >
              • {tip}
            </motion.li>
          ))}
        </motion.ul>
      )}
    </div>
  )
}

