"use client"

import { useAuth } from "@clerk/nextjs"
import { redirect } from "next/navigation"
import { MetricCard } from "@/components/MetricCard"
import { PredictionChart } from "@/components/PredictionChart"
import { Header } from "@/components/Header"

export default function DashboardPage() {
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
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Welcome to HorizonCast. Monitor your demand forecasts and model performance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            title="RMSE"
            value="1.6646"
            subtitle="Validation"
            trend="↓ 3.2%"
          />
          <MetricCard
            title="MAE"
            value="0.8783"
            subtitle="Validation"
            trend="↓ 1.8%"
          />
          <MetricCard
            title="Coverage"
            value="89.83%"
            subtitle="Interval (target: 90%)"
            trend="↑ 0.5%"
          />
          <MetricCard
            title="Business Cost"
            value="0.2547"
            subtitle="Test metrics"
            trend="↓ 5.1%"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <PredictionChart />
          </div>
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Recent Runs</h3>
            <div className="space-y-3">
              <div className="text-sm pb-3 border-b">
                <div className="font-medium">Run #001</div>
                <div className="text-muted-foreground text-xs">2 hours ago • Completed</div>
              </div>
              <div className="text-sm pb-3 border-b">
                <div className="font-medium">Run #002</div>
                <div className="text-muted-foreground text-xs">4 hours ago • Completed</div>
              </div>
              <div className="text-sm">
                <div className="font-medium">Run #003</div>
                <div className="text-muted-foreground text-xs">1 day ago • Completed</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
