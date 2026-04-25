import { Header } from "@/components/Header"

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account, API keys, and preferences.
          </p>
        </div>

        <div className="max-w-2xl space-y-6">
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Account</h3>
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Mode</span>
                <span className="font-medium">Local Demo</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tenant</span>
                <span className="font-mono">default-tenant</span>
              </div>
            </div>
          </div>

          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-2">API Key (demo)</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Use this key with the Python or JavaScript SDK.
            </p>
            <code className="block bg-muted p-3 rounded text-xs font-mono">
              demo-key-12345
            </code>
          </div>

          <div className="bg-card p-6 rounded-lg border">
            <h3 className="font-semibold mb-4">Backend Connection</h3>
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">API URL</span>
                <span className="font-mono">http://localhost:8000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">API docs</span>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener"
                  className="text-primary hover:underline"
                >
                  /docs
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
