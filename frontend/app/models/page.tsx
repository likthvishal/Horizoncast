"use client"

import { useAuth } from "@clerk/nextjs"
import { redirect } from "next/navigation"
import { Header } from "@/components/Header"

export default function ModelsPage() {
  const { isLoaded, userId } = useAuth()

  if (!isLoaded) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!userId) {
    redirect("/auth/sign-in")
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Models & Training</h1>
          <p className="text-muted-foreground mt-2">
            Train, manage, and deploy forecasting models.
          </p>
        </div>

        <div className="bg-card p-8 rounded-lg border text-center">
          <h2 className="text-xl font-semibold mb-2">No models yet</h2>
          <p className="text-muted-foreground mb-4">
            Upload a dataset and start training your first model.
          </p>
          <button className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90">
            Create Model
          </button>
        </div>
      </main>
    </div>
  )
}
