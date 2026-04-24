"use client"

import { useState } from "react"
import { Upload, AlertCircle, CheckCircle } from "lucide-react"

interface FileUploadState {
  isDragging: boolean
  file: File | null
  preview: { rows: any[]; columns: string[] } | null
  isLoading: boolean
  error: string | null
  success: boolean
}

export const DatasetUpload = () => {
  const [state, setState] = useState<FileUploadState>({
    isDragging: false,
    file: null,
    preview: null,
    isLoading: false,
    error: null,
    success: false,
  })

  const handleFileSelect = async (file: File) => {
    // Validate file type
    if (!file.name.endsWith(".csv") && !file.name.endsWith(".parquet")) {
      setState((s) => ({
        ...s,
        error: "Only CSV and Parquet files are supported",
      }))
      return
    }

    // Validate file size (max 500MB)
    if (file.size > 500 * 1024 * 1024) {
      setState((s) => ({
        ...s,
        error: "File size exceeds 500MB limit",
      }))
      return
    }

    setState((s) => ({ ...s, file, isLoading: true, error: null }))

    try {
      // Read and preview file
      const text = await file.text()
      const lines = text.split("\n")
      const headers = lines[0].split(",")
      const previewRows = lines.slice(1, 6).map((line) => {
        const values = line.split(",")
        return Object.fromEntries(headers.map((h, i) => [h.trim(), values[i]?.trim()]))
      })

      setState((s) => ({
        ...s,
        preview: { rows: previewRows, columns: headers.map((h) => h.trim()) },
        isLoading: false,
      }))
    } catch (err) {
      setState((s) => ({
        ...s,
        error: `Failed to read file: ${err instanceof Error ? err.message : "Unknown error"}`,
        isLoading: false,
      }))
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setState((s) => ({ ...s, isDragging: false }))
    if (e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleUpload = async () => {
    if (!state.file) return

    setState((s) => ({ ...s, isLoading: true }))

    try {
      // TODO: Upload to backend
      setState((s) => ({
        ...s,
        success: true,
        isLoading: false,
      }))

      setTimeout(() => {
        setState((s) => ({ ...s, file: null, preview: null, success: false }))
      }, 3000)
    } catch (err) {
      setState((s) => ({
        ...s,
        error: `Upload failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        isLoading: false,
      }))
    }
  }

  return (
    <div className="bg-card p-8 rounded-lg border">
      <h3 className="font-semibold mb-4">Upload Dataset</h3>

      {!state.file ? (
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            state.isDragging ? "border-primary bg-primary/5" : "border-muted"
          }`}
          onDragEnter={() => setState((s) => ({ ...s, isDragging: true }))}
          onDragLeave={() => setState((s) => ({ ...s, isDragging: false }))}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-sm font-medium">Drag and drop your CSV or Parquet file</p>
          <p className="text-xs text-muted-foreground mt-1">Max 500MB</p>
          <label className="block mt-4">
            <input
              type="file"
              accept=".csv,.parquet"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            />
            <button
              type="button"
              onClick={() => document.querySelector('input[type="file"]')?.click()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90"
            >
              Choose File
            </button>
          </label>
        </div>
      ) : (
        <>
          <div className="mb-4 p-4 bg-muted rounded-lg">
            <p className="text-sm font-medium">{state.file.name}</p>
            <p className="text-xs text-muted-foreground">
              {(state.file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>

          {state.preview && (
            <div className="mb-4">
              <p className="text-sm font-medium mb-2">Preview ({state.preview.columns.length} columns)</p>
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="border-b">
                      {state.preview.columns.map((col) => (
                        <th key={col} className="text-left p-2 text-muted-foreground">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {state.preview.rows.map((row, i) => (
                      <tr key={i} className="border-b">
                        {state.preview!.columns.map((col) => (
                          <td key={col} className="p-2">
                            {row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={handleUpload}
              disabled={state.isLoading || state.success}
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 disabled:opacity-50"
            >
              {state.isLoading ? "Uploading..." : state.success ? "✓ Uploaded" : "Upload"}
            </button>
            <button
              onClick={() => setState((s) => ({ ...s, file: null, preview: null }))}
              className="px-4 py-2 bg-muted text-foreground rounded-lg hover:opacity-80"
            >
              Cancel
            </button>
          </div>
        </>
      )}

      {state.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2 items-start">
          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{state.error}</p>
        </div>
      )}

      {state.success && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex gap-2 items-start">
          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-green-700">Dataset uploaded successfully!</p>
        </div>
      )}
    </div>
  )
}
