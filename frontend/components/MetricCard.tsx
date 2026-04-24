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
  return (
    <div className="bg-card p-6 rounded-lg border">
      <p className="text-sm text-muted-foreground">{title}</p>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-bold">{value}</span>
        {trend && <span className="text-sm text-green-600">{trend}</span>}
      </div>
      <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>
    </div>
  )
}
