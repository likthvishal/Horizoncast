"use client"

export const PredictionChart = () => {
  return (
    <div className="bg-card p-6 rounded-lg border">
      <h3 className="font-semibold mb-4">Forecast Preview</h3>
      <div className="h-64 bg-muted rounded flex items-center justify-center">
        <p className="text-sm text-muted-foreground">
          Chart will display here once data is available
        </p>
      </div>
    </div>
  )
}
