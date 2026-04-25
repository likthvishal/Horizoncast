import { MetricCard } from "@/components/MetricCard"
import { PredictionChart } from "@/components/PredictionChart"
import { Header } from "@/components/Header"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground mt-2">
              Latest run from the M5 benchmark — point forecasts and 90%
              prediction intervals.
            </p>
          </div>
          <div className="text-sm text-muted-foreground">
            Last run: <span className="font-medium text-foreground">2h ago</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            title="Test RMSE"
            value="1.7162"
            subtitle="Lower is better"
            trend="↓ 3.2%"
          />
          <MetricCard
            title="Test MAE"
            value="0.8933"
            subtitle="Lower is better"
            trend="↓ 1.8%"
          />
          <MetricCard
            title="Coverage @ 90%"
            value="89.83%"
            subtitle="Empirical interval coverage"
            trend="↑ 0.5%"
          />
          <MetricCard
            title="Business Cost"
            value="0.2547"
            subtitle="Asymmetric inventory cost"
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
              {[
                { id: "run_8f2a", status: "Completed", ago: "2 hours ago", rmse: "1.7162" },
                { id: "run_4c1d", status: "Completed", ago: "1 day ago", rmse: "1.7388" },
                { id: "run_9b6e", status: "Completed", ago: "3 days ago", rmse: "1.7521" },
                { id: "run_1a7f", status: "Failed", ago: "4 days ago", rmse: "—" },
              ].map((run) => (
                <div key={run.id} className="text-sm pb-3 border-b last:border-0">
                  <div className="flex justify-between">
                    <span className="font-medium font-mono">{run.id}</span>
                    <span
                      className={
                        run.status === "Completed"
                          ? "text-green-600 text-xs"
                          : "text-red-600 text-xs"
                      }
                    >
                      {run.status}
                    </span>
                  </div>
                  <div className="text-muted-foreground text-xs flex justify-between mt-1">
                    <span>{run.ago}</span>
                    <span>RMSE: {run.rmse}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Top Features (SHAP)</h3>
            <div className="space-y-3">
              {[
                { name: "lag_7", importance: 0.35 },
                { name: "roll_mean_28", importance: 0.22 },
                { name: "sell_price", importance: 0.15 },
                { name: "lag_28", importance: 0.12 },
                { name: "day_of_week", importance: 0.08 },
                { name: "snap_flag", importance: 0.05 },
              ].map((f) => (
                <div key={f.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-mono">{f.name}</span>
                    <span className="text-muted-foreground">
                      {(f.importance * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${f.importance * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Configuration</h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between border-b pb-2">
                <dt className="text-muted-foreground">Model</dt>
                <dd className="font-medium">LightGBM (Tweedie)</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt className="text-muted-foreground">Conformal alpha</dt>
                <dd className="font-medium font-mono">0.10</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt className="text-muted-foreground">Lookback days</dt>
                <dd className="font-medium font-mono">365</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt className="text-muted-foreground">Holding cost</dt>
                <dd className="font-medium font-mono">$0.10</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Stockout cost</dt>
                <dd className="font-medium font-mono">$0.50</dd>
              </div>
            </dl>
          </div>
        </div>
      </main>
    </div>
  )
}
