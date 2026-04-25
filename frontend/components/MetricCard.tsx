import { TrendingUp, TrendingDown } from "lucide-react"

export const MetricCard = ({
  title,
  value,
  subtitle,
  trend,
}: {
  title: string
  value: string
  subtitle: string
  trend?: string
}) => {
  const isUp = trend?.startsWith("↑")
  const isDown = trend?.startsWith("↓")
  return (
    <div className="bg-card p-6 rounded-lg border hover:shadow-sm transition">
      <p className="text-sm text-muted-foreground">{title}</p>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-bold tracking-tight">{value}</span>
        {trend && (
          <span
            className={`text-xs font-medium flex items-center gap-0.5 ${
              isDown ? "text-green-600" : isUp ? "text-amber-600" : "text-muted-foreground"
            }`}
          >
            {isDown ? <TrendingDown className="h-3 w-3" /> : isUp ? <TrendingUp className="h-3 w-3" /> : null}
            {trend.replace("↓", "").replace("↑", "").trim()}
          </span>
        )}
      </div>
      <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>
    </div>
  )
}
