import { Header } from "@/components/Header"
import { DatasetUpload } from "@/components/DatasetUpload"

export default function DatasetsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Datasets</h1>
          <p className="text-muted-foreground mt-2">
            Upload time-series data with at least <code>date</code>,{" "}
            <code>store_id</code>, <code>item_id</code>, and{" "}
            <code>sales</code> columns.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <DatasetUpload />
          </div>
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Your Datasets</h3>
            <div className="space-y-3">
              {[
                {
                  name: "M5 Sales (sample)",
                  rows: "2.1M",
                  updated: "2h ago",
                  status: "ready",
                },
                {
                  name: "Q4 Retail Forecast",
                  rows: "500K",
                  updated: "1d ago",
                  status: "ready",
                },
                {
                  name: "E-commerce Pilot",
                  rows: "1.5M",
                  updated: "3d ago",
                  status: "processing",
                },
              ].map((d) => (
                <div
                  key={d.name}
                  className="text-sm pb-3 border-b last:border-0"
                >
                  <div className="flex justify-between">
                    <span className="font-medium">{d.name}</span>
                    <span
                      className={
                        d.status === "ready"
                          ? "text-green-600 text-xs"
                          : "text-amber-600 text-xs"
                      }
                    >
                      {d.status}
                    </span>
                  </div>
                  <div className="text-muted-foreground text-xs mt-1">
                    {d.rows} rows • Updated {d.updated}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
