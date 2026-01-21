import { useState } from 'react';
import { ArrowRight, Lock, Database, FileText, Image as ImageIcon, Mic } from 'lucide-react';
import { Auth } from './Auth';

export default function LandingPage({ onLogin }) {
  const [showAuth, setShowAuth] = useState(false);

  if (showAuth) {
    return (
      <div className="relative min-h-screen">
          <button 
            onClick={() => setShowAuth(false)}
            className="absolute top-4 left-4 z-50 px-4 py-2 bg-gray-200 dark:bg-gray-800 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors"
          >
            ← Back
          </button>
          <Auth onLogin={onLogin} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-sans selection:bg-blue-500/30">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl">
            <div className="w-8 h-8 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white">
              AI
            </div>
            <span>OfflineRAG</span>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setShowAuth(true)}
              className="text-sm font-medium hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            >
              Log in
            </button>
            <button 
              onClick={() => setShowAuth(true)}
              className="bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-4 py-2 rounded-full text-sm font-medium hover:opacity-90 transition-opacity"
            >
              Sign Up
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="lg:w-1/2 space-y-8">
              <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight leading-[1.1]">
                Chat with your <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                  Private Data
                </span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-400 leading-relaxed max-w-2xl">
                An offline, privacy-first RAG assistant that understands text, images, and audio. No data leaves your device.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => setShowAuth(true)}
                  className="group flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-full text-lg font-semibold transition-all hover:shadow-lg hover:shadow-blue-500/25"
                >
                  Get Started
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button className="flex items-center justify-center gap-2 px-8 py-4 rounded-full text-lg font-medium border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">
                  View Demo
                </button>
              </div>
            </div>
            {/* Visual Element */}
            <div className="lg:w-1/2 relative">
                <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/20 to-purple-500/20 blur-3xl rounded-full" />
                <div className="relative bg-gray-900 rounded-2xl border border-gray-800 shadow-2xl overflow-hidden aspect-video group transform hover:scale-[1.02] transition-transform duration-500">
                   <img 
                      src="/hero-bg.png" 
                      alt="Offline RAG Dashboard" 
                      className="w-full h-full object-cover"
                   />
                </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <section className="py-24 bg-gray-50 dark:bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Why OfflineRAG?</h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Built for privacy and performance. Process your documents locally without relying on cloud APIs.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Lock className="w-6 h-6 text-green-500" />}
              title="100% Private"
              description="Your data never leaves your machine. All processing happens locally."
            />
            <FeatureCard 
              icon={<Database className="w-6 h-6 text-blue-500" />}
              title="Multimodal"
              description="Process PDFs, Images, and Audio files seamlessly."
            />
            <FeatureCard 
              icon={<FileText className="w-6 h-6 text-purple-500" />}
              title="Context Aware"
              description="Smart retrieval system that understands the context of your queries."
            />
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-8 border-t border-gray-200 dark:border-gray-800">
         <div className="max-w-7xl mx-auto px-6 text-center text-gray-500 text-sm">
            © 2026 OfflineRAG. Open Source Project.
         </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
      <div className="w-12 h-12 bg-gray-50 dark:bg-gray-700/50 rounded-lg flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-600 dark:text-gray-400">{description}</p>
    </div>
  );
}
