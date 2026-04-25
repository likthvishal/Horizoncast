import axios from "axios"

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    Authorization: "Bearer demo-key-12345",
  },
})

export const forecastApi = {
  startTraining: (config: unknown) =>
    client.post("/api/forecasts/train", config),
  getTrainingRun: (runId: string) =>
    client.get(`/api/forecasts/runs/${runId}`),
  predict: (request: unknown) =>
    client.post("/api/forecasts/predict", request),
  getExplanation: (runId: string) =>
    client.get(`/api/forecasts/runs/${runId}/explain`),
}

export const datasetApi = {
  uploadDataset: (dataset: unknown) =>
    client.post("/api/datasets/upload", dataset),
  getDataset: (datasetId: string) =>
    client.get(`/api/datasets/${datasetId}`),
  listDatasets: () => client.get("/api/datasets/"),
  deleteDataset: (datasetId: string) =>
    client.delete(`/api/datasets/${datasetId}`),
}

export default client
