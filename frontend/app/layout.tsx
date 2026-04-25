import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "HorizonCast - Demand Forecasting",
  description: "AI-powered demand forecasting with uncertainty quantification",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
