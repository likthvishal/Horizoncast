"use client"

import { useAuth } from "@clerk/nextjs"
import { redirect } from "next/navigation"
import { Header } from "@/components/Header"
import { DatasetUpload } from "@/components/DatasetUpload"

export default function DatasetsPage() {
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
          <h1 className="text-3xl font-bold tracking-tight">Datasets</h1>
          <p className="text-muted-foreground mt-2">
            Upload and manage your forecast datasets.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <DatasetUpload />
          </div>
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Your Datasets</h3>
            <div className="space-y-3">
              <div className="text-sm pb-3 border-b">
                <div className="font-medium">M5 Sales Data</div>
                <div className="text-muted-foreground text-xs">2.1M rows • Updated 2h ago</div>
              </div>
              <div className="text-sm pb-3 border-b">
                <div className="font-medium">Retail Forecast</div>
                <div className="text-muted-foreground text-xs">500K rows • Updated 1d ago</div>
              </div>
              <div className="text-sm">
                <div className="font-medium">E-commerce Data</div>
                <div className="text-muted-foreground text-xs">1.5M rows • Updated 3d ago</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
