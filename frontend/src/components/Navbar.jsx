import React from 'react';
import { FileText, Plus } from 'lucide-react';

export default function Navbar({ onNewAnalysis }) {
  return (
    <nav className="bg-black text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 w-full flex items-center justify-between">
        {/* Center: icon + title + subtitle */}
        <div className="flex items-center gap-3">
          <div className="bg-white/10 rounded-lg p-1.5">
            <FileText className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold tracking-tight">JD Analyzer</span>
            <span className="text-xs text-gray-400">AI-powered resume &amp; job match</span>
          </div>
        </div>
        <button className="new-analysis-button" onClick={onNewAnalysis}><Plus size={15} /> New analysis</button>
      </div>
    </nav>
  );
}
