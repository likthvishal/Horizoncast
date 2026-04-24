"""React hooks for API data fetching."""

import { useQuery, useMutation } from "@tanstack/react-query"
import { forecastApi, datasetApi } from "./api"

export const useTrainingRun = (runId: string | null) => {
  return useQuery({
    queryKey: ["trainingRun", runId],
    queryFn: () => (runId ? forecastApi.getTrainingRun(runId) : null),
    enabled: !!runId,
  })
}

export const useDatasets = () => {
  return useQuery({
    queryKey: ["datasets"],
    queryFn: () => datasetApi.listDatasets(),
  })
}

export const useUploadDataset = () => {
  return useMutation({
    mutationFn: (dataset: any) => datasetApi.uploadDataset(dataset),
  })
}

export const useStartTraining = () => {
  return useMutation({
    mutationFn: (config: any) => forecastApi.startTraining(config),
  })
}
