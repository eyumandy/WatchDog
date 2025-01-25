import { useState, useEffect, useCallback } from 'react'
import zxcvbn from 'zxcvbn'

export function usePasswordStrength(password: string) {
  const [strength, setStrength] = useState(0)
  const [feedback, setFeedback] = useState<string[]>([])

  const analyzePassword = useCallback((pass: string) => {
    const result = zxcvbn(pass)
    setStrength(result.score)
    setFeedback(result.feedback.suggestions)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => analyzePassword(password), 300)
    return () => clearTimeout(timer)
  }, [password, analyzePassword])

  return { strength, feedback }
}

