/**
 * Root Layout
 *
 * This is the root layout component for the WatchDog application.
 * It provides the basic HTML structure and includes global styles
 * and transitions.
 */

import "./globals.css"
import { Inter } from "next/font/google"
import PageTransition from "./components/PageTransition"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "WatchDog Surveillance",
  description: "Advanced security monitoring solutions",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <PageTransition>{children}</PageTransition>
      </body>
    </html>
  )
}

