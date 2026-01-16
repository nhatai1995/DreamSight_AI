import DreamForm from "@/components/DreamForm";
import AuthButton from "@/components/AuthButton";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 overflow-x-hidden selection:bg-purple-500/30 selection:text-purple-200">
      {/* Background Animated Gradient */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-900/10 rounded-full blur-[120px] mix-blend-screen animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-cyan-900/10 rounded-full blur-[120px] mix-blend-screen animate-pulse" style={{ animationDelay: "2s" }} />
        <div className="absolute top-[20%] right-[20%] w-[30%] h-[30%] bg-indigo-900/10 rounded-full blur-[100px] mix-blend-screen animate-pulse" style={{ animationDelay: "4s" }} />
      </div>

      {/* Grid Overlay */}
      <div className="fixed inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-20 pointer-events-none" />

      {/* Auth Header - Fixed Top Right */}
      <div className="fixed top-4 right-4 z-50">
        <AuthButton />
      </div>

      <main className="relative z-10 flex flex-col items-center justify-start min-h-screen px-4 py-16 md:py-24">
        {/* Hero Section */}
        <header className="text-center mb-16 relative">
          <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-[200px] h-[200px] bg-purple-500/20 blur-[100px] rounded-full" />

          <div className="relative inline-block mb-4">
            <span className="absolute inset-0 blur-2xl bg-purple-500/30 rounded-full" />
            <span className="relative text-6xl md:text-7xl animate-pulse">👁️</span>
          </div>

          <h1 className="relative text-5xl md:text-7xl font-bold mb-4 tracking-tighter">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-fuchsia-300 to-cyan-400 drop-shadow-[0_0_15px_rgba(168,85,247,0.5)]">
              DreamSight
            </span>{" "}
            <span className="text-slate-700 font-light hidden md:inline">|</span>{" "}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400 font-light drop-shadow-[0_0_15px_rgba(34,211,238,0.3)]">
              Oracle
            </span>
          </h1>

          <p className="text-gray-400 text-lg md:text-xl max-w-xl mx-auto font-light leading-relaxed tracking-wide">
            Unlock the hidden messages of your subconscious through
            <span className="text-purple-300 mx-1">ancient wisdom</span>
            and
            <span className="text-cyan-300 mx-1">artificial intelligence</span>.
          </p>
        </header>

        {/* Main Interface */}
        <DreamForm />

        {/* Footer */}
        <footer className="mt-24 text-center">
          <p className="text-slate-600 text-sm flex items-center justify-center gap-2">
            <span>Powered by</span>
            <span className="text-slate-500 font-medium">LangChain</span>
            <span>&</span>
            <span className="text-slate-500 font-medium">Full-Stack Magic</span>
          </p>
        </footer>
      </main>
    </div>
  );
}
