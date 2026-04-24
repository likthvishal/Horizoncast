"""HorizonCast JavaScript/TypeScript SDK"""

import axios, { AxiosInstance } from "axios"

interface PredictionResult {
  value: number
  lowerBound?: number
  upperBound?: number
  confidence?: number
}

interface TrainingConfig {
  datasetId: string
  trainEndDate?: string
  valEndDate?: string
  includeEmbeddings?: boolean
}

interface TrainingRun {
  runId: string
  datasetId: string
  status: "pending" | "running" | "completed" | "failed"
  metrics?: Record<string, number>
  createdAt: string
}

export class HorizonCast {
  private client: AxiosInstance

  constructor(apiUrl: string = "http://localhost:8000", apiKey: string = "demo-key-12345") {
    this.client = axios.create({
      baseURL: apiUrl,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
    })
  }

  async startTraining(config: TrainingConfig): Promise<{ runId: string; jobId: string }> {
    const response = await this.client.post("/api/forecasts/train", config)
    return response.data
  }

  async getTrainingRun(runId: string): Promise<TrainingRun> {
    const response = await this.client.get(`/api/forecasts/runs/${runId}`)
    return response.data
  }

  async waitForTraining(runId: string, timeoutMs: number = 3600000): Promise<TrainingRun> {
    const startTime = Date.now()
    const pollInterval = 5000

    while (Date.now() - startTime < timeoutMs) {
      const run = await this.getTrainingRun(runId)
      if (["completed", "failed"].includes(run.status)) {
        return run
      }
      await new Promise((resolve) => setTimeout(resolve, pollInterval))
    }

    throw new Error(`Training run ${runId} timeout after ${timeoutMs}ms`)
  }

  async predict(runId: string, data: Record<string, number>): Promise<PredictionResult> {
    const response = await this.client.post("/api/forecasts/predict", {
      run_id: runId,
      data,
    })
    return {
      value: response.data.prediction,
      lowerBound: response.data.lower_bound,
      upperBound: response.data.upper_bound,
      confidence: response.data.confidence,
    }
  }

  async explain(runId: string): Promise<Record<string, any>> {
    const response = await this.client.get(`/api/forecasts/runs/${runId}/explain`)
    return response.data
  }
}

export default HorizonCast
