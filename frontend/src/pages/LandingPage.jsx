import React from 'react';
import { ArrowRight, Shield, Database, FileText, CheckCircle } from 'lucide-react';

const LandingPage = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-300">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
             <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xl">
                A
             </div>
             <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
                Local AI
             </span>
          </div>
          <button
            onClick={onGetStarted}
            className="text-sm font-medium text-gray-600 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400 transition-colors"
          >
            Sign In
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-28">
         <div className="container mx-auto px-6 relative z-10">
            <div className="mx-auto max-w-4xl text-center">
               <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-6xl mb-6">
                  Your Private, Intelligent <br/>
                  <span className="text-indigo-600 dark:text-indigo-400">Knowledge Assistant</span>
               </h1>
               <p className="mt-4 text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-10">
                  Chat with your documents locally. Secure, offline, and powered by RAG technology. 
                  Get accurate answers from your own data without exact keywords.
               </p>
               <div className="flex justify-center gap-4">
                  <button
                     onClick={onGetStarted}
                     className="px-8 py-4 text-lg font-semibold rounded-full bg-indigo-600 text-white hover:bg-indigo-700 transition-all shadow-lg hover:shadow-indigo-500/30 flex items-center gap-2"
                  >
                     Get Started <ArrowRight className="w-5 h-5" />
                  </button>
               </div>
            </div>
         </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-gray-50 dark:bg-gray-800/50">
         <div className="container mx-auto px-6">
            <div className="text-center mb-16">
               <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Why Local AI?</h2>
               <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                  Built for privacy and performance. Experience the power of AI running entirely on your machine.
               </p>
            </div>

            <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
               <FeatureCard 
                  icon={<Shield className="w-10 h-10 text-indigo-500" />}
                  title="Offline & Secure"
                  description="Your data never leaves your device. Query sensitive documents with complete peace of mind."
               />
               <FeatureCard 
                  icon={<Database className="w-10 h-10 text-purple-500" />}
                  title="RAG Powered"
                  description="Retrieval-Augmented Generation ensures answers are grounded in your actual documents, not hallucinations."
               />
               <FeatureCard 
                  icon={<FileText className="w-10 h-10 text-pink-500" />}
                  title="Multi-Format Support"
                  description="Upload PDF, TXT, and other common formats. We handle the parsing and indexing for you."
               />
            </div>
         </div>
      </div>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-12">
         <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
               <span className="font-bold text-gray-900 dark:text-white">Local AI Assistant</span>
               <p className="text-sm text-gray-500 mt-1">© {new Date().getFullYear()} All rights reserved.</p>
            </div>
            <div className="flex gap-6">
               <button className="text-gray-500 hover:text-indigo-600 transition-colors">Privacy</button>
               <button className="text-gray-500 hover:text-indigo-600 transition-colors">Terms</button>
               <button className="text-gray-500 hover:text-indigo-600 transition-colors">GitHub</button>
            </div>
         </div>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, description }) => (
  <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700">
    <div className="mb-6 bg-gray-50 dark:bg-gray-700/50 w-16 h-16 rounded-xl flex items-center justify-center">
      {icon}
    </div>
    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">{title}</h3>
    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
      {description}
    </p>
  </div>
);

export default LandingPage;
