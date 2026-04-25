import Link from "next/link"
import { Activity } from "lucide-react"

export const Header = () => {
  return (
    <header className="bg-card border-b sticky top-0 z-50 backdrop-blur supports-[backdrop-filter]:bg-card/80">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-primary text-primary-foreground flex items-center justify-center">
              <Activity className="h-4 w-4" />
            </div>
            <span className="text-lg font-semibold tracking-tight">
              HorizonCast
            </span>
          </Link>
          <nav className="hidden md:flex gap-6 text-sm">
            <Link
              href="/dashboard"
              className="text-muted-foreground hover:text-foreground transition"
            >
              Dashboard
            </Link>
            <Link
              href="/datasets"
              className="text-muted-foreground hover:text-foreground transition"
            >
              Datasets
            </Link>
            <Link
              href="/models"
              className="text-muted-foreground hover:text-foreground transition"
            >
              Models
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener"
            className="text-sm text-muted-foreground hover:text-foreground transition"
          >
            API
          </a>
          <Link
            href="/settings"
            className="text-sm text-muted-foreground hover:text-foreground transition"
          >
            Settings
          </Link>
        </div>
      </div>
    </header>
  )
}
