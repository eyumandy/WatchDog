/**
 * Home Page
 *
 * This is the landing page for the WatchDog application.
 * It provides an introduction to the system and access to
 * the main dashboard.
 */

import Hero from "./components/Hero"

export default function Home() {
  return (
    <div className="relative min-h-screen bg-black text-white overflow-hidden">
      <Hero />
    </div>
  )
}