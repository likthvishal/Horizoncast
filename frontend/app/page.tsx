import Link from "next/link"
import { Header } from "@/components/Header"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Demo Mode — Local Preview
          </div>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
            Demand forecasting with{" "}
            <span className="text-primary">calibrated uncertainty</span>
          </h1>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            HorizonCast combines classical time-series features, LLM embeddings,
            LightGBM, and conformal prediction to give you forecasts with
            confidence intervals you can actually trust.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/dashboard"
              className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition"
            >
              Open Dashboard
            </Link>
            <Link
              href="/datasets"
              className="px-6 py-3 border rounded-lg font-medium hover:bg-muted transition"
            >
              Upload Dataset
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 max-w-4xl mx-auto">
          <div className="bg-card p-6 rounded-lg border">
            <div className="text-3xl font-bold text-primary mb-2">89.83%</div>
            <div className="font-medium mb-1">Interval coverage</div>
            <p className="text-sm text-muted-foreground">
              Conformal prediction gives empirical coverage close to the 90%
              target.
            </p>
          </div>
          <div className="bg-card p-6 rounded-lg border">
            <div className="text-3xl font-bold text-primary mb-2">1.66</div>
            <div className="font-medium mb-1">Validation RMSE</div>
            <p className="text-sm text-muted-foreground">
              Strong point accuracy on the M5 benchmark dataset.
            </p>
          </div>
          <div className="bg-card p-6 rounded-lg border">
            <div className="text-3xl font-bold text-primary mb-2">0.25</div>
            <div className="font-medium mb-1">Inventory cost</div>
            <p className="text-sm text-muted-foreground">
              Asymmetric stockout vs. holding cost — built for retail.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
