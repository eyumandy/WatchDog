"use client"

import React, { useRef, useEffect } from "react"
import { motion } from "framer-motion"

interface NetworkBackgroundProps {
  color?: string
  nodeColor?: string
  lineColor?: string
}

// Adjustable variables to match the image style
const NODE_COUNT = 100
const CONNECTION_DISTANCE = 200
const NODE_RADIUS = 1
const LINE_WIDTH = 0.6
const ANIMATION_SPEED = 1.2

export default function NetworkBackground({
  color = "rgb(15, 23, 42)",
  nodeColor = "rgba(255, 255, 255, 0.4)",
  lineColor = "rgba(255, 255, 255, 0.15)",
}: NetworkBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const resizeCanvas = () => {
      const dpr = window.devicePixelRatio || 1
      canvas.width = window.innerWidth * dpr
      canvas.height = window.innerHeight * dpr
      ctx.scale(dpr, dpr)
      canvas.style.width = `${window.innerWidth}px`
      canvas.style.height = `${window.innerHeight}px`
    }

    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    interface Node {
      x: number
      y: number
      vx: number
      vy: number
    }

    const nodes: Node[] = Array.from({ length: NODE_COUNT }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * ANIMATION_SPEED,
      vy: (Math.random() - 0.5) * ANIMATION_SPEED,
    }))

    const animate = () => {
      ctx.fillStyle = color
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Update node positions
      nodes.forEach((node) => {
        node.x += node.vx
        node.y += node.vy

        // Bounce off edges
        if (node.x < 0 || node.x > canvas.width) node.vx *= -1
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1

        // Keep within bounds
        node.x = Math.max(0, Math.min(canvas.width, node.x))
        node.y = Math.max(0, Math.min(canvas.height, node.y))
      })

      // Draw connections
      ctx.beginPath()
      ctx.strokeStyle = lineColor
      ctx.lineWidth = LINE_WIDTH
      nodes.forEach((nodeA, i) => {
        nodes.slice(i + 1).forEach((nodeB) => {
          const dx = nodeA.x - nodeB.x
          const dy = nodeA.y - nodeB.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          if (distance < CONNECTION_DISTANCE) {
            const opacity = 1 - distance / CONNECTION_DISTANCE
            ctx.strokeStyle = `rgba(255, 255, 255, ${opacity * 0.15})`
            ctx.beginPath()
            ctx.moveTo(nodeA.x, nodeA.y)
            ctx.lineTo(nodeB.x, nodeB.y)
            ctx.stroke()
          }
        })
      })

      // Draw nodes
      ctx.fillStyle = nodeColor
      nodes.forEach((node) => {
        ctx.beginPath()
        ctx.arc(node.x, node.y, NODE_RADIUS, 0, Math.PI * 2)
        ctx.fill()
      })

      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
    }
  }, [color, nodeColor, lineColor])

  return (
    <motion.canvas
      ref={canvasRef}
      className="fixed inset-0"
      style={{ background: color }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    />
  )
}

