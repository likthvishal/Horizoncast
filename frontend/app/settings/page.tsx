"use client"

import { useAuth } from "@clerk/nextjs"
import { redirect } from "next/navigation"
import { Header } from "@/components/Header"
import { UserButton } from "@clerk/nextjs"

export default function SettingsPage() {
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
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account and preferences.
          </p>
        </div>

        <div className="max-w-2xl space-y-6">
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Account</h3>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-muted-foreground">Signed in as</p>
                <p className="font-medium">{userId}</p>
              </div>
              <UserButton />
            </div>
          </div>

          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">API Keys</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Manage API keys for programmatic access.
            </p>
            <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90">
              Generate New Key
            </button>
          </div>

          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Preferences</h3>
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              <span className="text-sm">Email notifications on training completion</span>
            </label>
          </div>
        </div>
      </main>
    </div>
  )
}
