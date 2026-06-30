import React from 'react';
import { FileText } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-black text-white">
      <div className="max-w-3xl mx-auto px-6 h-14 flex items-center justify-center">
        {/* Center: icon + title + subtitle */}
        <div className="flex items-center gap-3">
          <div className="bg-white/10 rounded-lg p-1.5">
            <FileText className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold tracking-tight">JD Analyzer</span>
            <span className="text-xs text-gray-400">Analyze resumes against job descriptions using AI</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
