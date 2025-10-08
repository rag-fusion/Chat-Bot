import { Moon, Sun, Wifi, WifiOff } from "lucide-react";

export default function Header({ dark, setDark, isOnline = true }) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <div className="mr-4 hidden md:flex">
          <a className="mr-6 flex items-center space-x-2" href="/">
            <span className="hidden font-bold sm:inline-block">
              Offline Multimodal RAG
            </span>
          </a>
        </div>

        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            {/* Add search or other controls here if needed */}
          </div>
          <nav className="flex items-center space-x-2">
            <button
              onClick={() => setDark(!dark)}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring h-9 py-2 w-9 px-0"
            >
              {dark ? (
                <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              ) : (
                <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              )}
              <span className="sr-only">Toggle theme</span>
            </button>

            <button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring h-9 py-2 w-9 px-0">
              {isOnline ? (
                <Wifi className="h-[1.2rem] w-[1.2rem] text-green-500" />
              ) : (
                <WifiOff className="h-[1.2rem] w-[1.2rem] text-destructive" />
              )}
              <span className="sr-only">Connection status</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
