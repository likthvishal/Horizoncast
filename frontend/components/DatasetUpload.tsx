"use client"

import { useState } from "react"
import { Upload, AlertCircle, CheckCircle, FileText } from "lucide-react"

interface PreviewState {
  rows: Record<string, string>[]
  columns: string[]
}

export const DatasetUpload = () => {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<PreviewState | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleFileSelect = async (selectedFile: File) => {
    setError(null)
    setSuccess(false)

    if (!selectedFile.name.endsWith(".csv") && !selectedFile.name.endsWith(".parquet")) {
      setError("Only CSV and Parquet files are supported")
      return
    }
    if (selectedFile.size > 500 * 1024 * 1024) {
      setError("File size exceeds 500MB limit")
      return
    }

    setFile(selectedFile)
    setIsLoading(true)

    try {
      if (selectedFile.name.endsWith(".csv")) {
        const text = await selectedFile.slice(0, 64 * 1024).text()
        const lines = text.split("\n").filter((l) => l.trim().length > 0)
        if (lines.length === 0) {
          throw new Error("File is empty")
        }
        const headers = lines[0].split(",").map((h) => h.trim())
        const previewRows = lines.slice(1, 6).map((line) => {
          const values = line.split(",")
          return Object.fromEntries(
            headers.map((h, i) => [h, (values[i] ?? "").trim()])
          )
        })
        setPreview({ rows: previewRows, columns: headers })
      } else {
        setPreview(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to read file")
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append("file", file)
      const res = await fetch("http://localhost:8000/api/upload/csv", {
        method: "POST",
        headers: { Authorization: "Bearer demo-key-12345" },
        body: formData,
      })
      if (!res.ok) {
        throw new Error(`Upload failed: ${res.status}`)
      }
      setSuccess(true)
    } catch (err) {
      setError(
        err instanceof Error
          ? `${err.message}. Make sure the backend is running on :8000.`
          : "Upload failed"
      )
    } finally {
      setIsLoading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setPreview(null)
    setError(null)
    setSuccess(false)
  }

  return (
    <div className="bg-card p-8 rounded-lg border">
      <h3 className="font-semibold mb-4">Upload Dataset</h3>

      {!file ? (
        <label
          className={`block border-2 border-dashed rounded-lg p-12 text-center transition cursor-pointer ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-muted hover:border-primary/50"
          }`}
          onDragEnter={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragOver={(e) => e.preventDefault()}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setIsDragging(false)
            const f = e.dataTransfer.files[0]
            if (f) handleFileSelect(f)
          }}
        >
          <Upload className="mx-auto h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-sm font-medium">Drag and drop a CSV or Parquet file</p>
          <p className="text-xs text-muted-foreground mt-1">or click to browse — max 500MB</p>
          <input
            type="file"
            accept=".csv,.parquet"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) handleFileSelect(f)
            }}
          />
        </label>
      ) : (
        <>
          <div className="mb-4 p-4 bg-muted rounded-lg flex items-center gap-3">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <div className="flex-1">
              <p className="text-sm font-medium">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>

          {preview && (
            <div className="mb-4">
              <p className="text-sm font-medium mb-2">
                Preview ({preview.columns.length} columns)
              </p>
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full text-xs">
                  <thead className="bg-muted/50">
                    <tr>
                      {preview.columns.map((col) => (
                        <th
                          key={col}
                          className="text-left p-2 font-medium border-b"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.rows.map((row, i) => (
                      <tr key={i} className="border-b last:border-0">
                        {preview.columns.map((col) => (
                          <td key={col} className="p-2 font-mono">
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
              disabled={isLoading || success}
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 disabled:opacity-50"
            >
              {isLoading ? "Uploading..." : success ? "Uploaded ✓" : "Upload to Backend"}
            </button>
            <button
              onClick={reset}
              className="px-4 py-2 border rounded-lg hover:bg-muted"
            >
              Cancel
            </button>
          </div>
        </>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2 items-start">
          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {success && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex gap-2 items-start">
          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-green-700">Dataset uploaded successfully!</p>
        </div>
      )}
    </div>
  )
}
