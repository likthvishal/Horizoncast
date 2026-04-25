import { Header } from "@/components/Header"

export default function ModelsPage() {
  const models = [
    {
      id: "mdl_lgbm_tweedie",
      name: "LightGBM (Tweedie)",
      version: "v3",
      rmse: 1.7162,
      coverage: 89.8,
      status: "production",
      created: "2h ago",
    },
    {
      id: "mdl_lgbm_rmse",
      name: "LightGBM (RMSE)",
      version: "v2",
      rmse: 1.7388,
      coverage: 88.4,
      status: "candidate",
      created: "1d ago",
    },
    {
      id: "mdl_baseline_seasonal",
      name: "Seasonal Naive",
      version: "v1",
      rmse: 2.4101,
      coverage: 71.2,
      status: "baseline",
      created: "4d ago",
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Models</h1>
            <p className="text-muted-foreground mt-2">
              Trained forecasters with versioned artifacts and validation
              metrics.
            </p>
          </div>
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90">
            + New Training Run
          </button>
        </div>

        <div className="bg-card rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr className="border-b">
                <th className="text-left p-4 font-medium">Model</th>
                <th className="text-left p-4 font-medium">Version</th>
                <th className="text-right p-4 font-medium">Test RMSE</th>
                <th className="text-right p-4 font-medium">Coverage</th>
                <th className="text-left p-4 font-medium">Status</th>
                <th className="text-left p-4 font-medium">Created</th>
                <th className="p-4"></th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.id} className="border-b last:border-0 hover:bg-muted/30">
                  <td className="p-4">
                    <div className="font-medium">{m.name}</div>
                    <div className="text-xs text-muted-foreground font-mono">
                      {m.id}
                    </div>
                  </td>
                  <td className="p-4 font-mono">{m.version}</td>
                  <td className="p-4 text-right font-mono">{m.rmse.toFixed(4)}</td>
                  <td className="p-4 text-right font-mono">{m.coverage}%</td>
                  <td className="p-4">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        m.status === "production"
                          ? "bg-green-100 text-green-700"
                          : m.status === "candidate"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {m.status}
                    </span>
                  </td>
                  <td className="p-4 text-muted-foreground">{m.created}</td>
                  <td className="p-4 text-right">
                    <button className="text-sm text-primary hover:underline">
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  )
}
