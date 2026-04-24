"use client"

import { useAuth } from "@clerk/nextjs"
import { redirect } from "next/navigation"

export default function Home() {
  const { isLoaded, userId } = useAuth()

  if (!isLoaded) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!userId) {
    redirect("/auth/sign-in")
  }

  redirect("/dashboard")
}
