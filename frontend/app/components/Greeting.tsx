import { motion } from 'framer-motion'

interface GreetingProps {
  timeOfDay: string
}

export default function Greeting({ timeOfDay }: GreetingProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="text-4xl font-light mb-8"
    >
      Good {timeOfDay}, John
    </motion.div>
  )
}

