export const Header = () => {
  return (
    <header className="bg-card border-b sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <h1 className="text-2xl font-bold">HorizonCast</h1>
          <nav className="hidden md:flex gap-6">
            <a href="/dashboard" className="text-sm hover:text-primary">Dashboard</a>
            <a href="/datasets" className="text-sm hover:text-primary">Datasets</a>
            <a href="/models" className="text-sm hover:text-primary">Models</a>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <a href="/settings" className="text-sm hover:text-primary">Settings</a>
        </div>
      </div>
    </header>
  )
}
