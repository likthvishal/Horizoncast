"use client"

import { useMemo } from "react"

function generateSeries(n: number) {
  const points: { x: number; actual: number; pred: number; lower: number; upper: number }[] = []
  for (let i = 0; i < n; i++) {
    const seasonal = 8 + 4 * Math.sin((i / n) * Math.PI * 4)
    const trend = i * 0.02
    const noise = (Math.sin(i * 1.7) + Math.cos(i * 0.9)) * 1.2
    const actual = Math.max(0, seasonal + trend + noise)
    const pred = seasonal + trend + noise * 0.4
    const halfWidth = 1.6 + 0.4 * Math.abs(Math.sin(i * 0.3))
    points.push({
      x: i,
      actual,
      pred,
      lower: pred - halfWidth,
      upper: pred + halfWidth,
    })
  }
  return points
}

export const PredictionChart = () => {
  const data = useMemo(() => generateSeries(60), [])
  const width = 720
  const height = 280
  const padding = { top: 20, right: 20, bottom: 30, left: 40 }
  const innerW = width - padding.left - padding.right
  const innerH = height - padding.top - padding.bottom

  const allValues = data.flatMap((d) => [d.actual, d.lower, d.upper])
  const yMin = Math.min(...allValues) - 1
  const yMax = Math.max(...allValues) + 1

  const x = (i: number) => padding.left + (i / (data.length - 1)) * innerW
  const y = (v: number) =>
    padding.top + innerH - ((v - yMin) / (yMax - yMin)) * innerH

  const intervalPath =
    data.map((d, i) => `${i === 0 ? "M" : "L"} ${x(i)},${y(d.upper)}`).join(" ") +
    " " +
    [...data]
      .reverse()
      .map((d, i) => `L ${x(data.length - 1 - i)},${y(d.lower)}`)
      .join(" ") +
    " Z"

  const actualPath = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${x(i)},${y(d.actual)}`)
    .join(" ")

  const predPath = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${x(i)},${y(d.pred)}`)
    .join(" ")

  const yTicks = [yMin, (yMin + yMax) / 2, yMax]

  return (
    <div className="bg-card p-6 rounded-lg border">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold">Forecast vs. Actual</h3>
          <p className="text-xs text-muted-foreground mt-1">
            Last 60 days, with 90% conformal prediction intervals
          </p>
        </div>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-3 rounded-sm bg-primary/20" />
            <span className="text-muted-foreground">Interval</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-0.5 w-3 bg-primary" />
            <span className="text-muted-foreground">Forecast</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-0.5 w-3 bg-foreground" />
            <span className="text-muted-foreground">Actual</span>
          </div>
        </div>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        preserveAspectRatio="none"
      >
        {yTicks.map((t, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={y(t)}
              y2={y(t)}
              stroke="currentColor"
              strokeOpacity="0.08"
              strokeDasharray="3 3"
            />
            <text
              x={padding.left - 6}
              y={y(t)}
              textAnchor="end"
              dominantBaseline="middle"
              fontSize="10"
              fill="currentColor"
              opacity="0.5"
            >
              {t.toFixed(1)}
            </text>
          </g>
        ))}

        <path d={intervalPath} fill="hsl(var(--primary))" fillOpacity="0.18" />

        <path
          d={predPath}
          stroke="hsl(var(--primary))"
          strokeWidth="2"
          fill="none"
        />

        <path
          d={actualPath}
          stroke="currentColor"
          strokeWidth="1.5"
          fill="none"
          strokeDasharray="4 3"
        />

        <line
          x1={padding.left}
          x2={width - padding.right}
          y1={height - padding.bottom}
          y2={height - padding.bottom}
          stroke="currentColor"
          strokeOpacity="0.2"
        />
      </svg>

      <div className="text-xs text-muted-foreground mt-2 flex justify-between">
        <span>Day 1</span>
        <span>Day {data.length}</span>
      </div>
    </div>
  )
}
