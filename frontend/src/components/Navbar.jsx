import React from 'react';
import { Zap, Plus } from 'lucide-react';

export default function Navbar({ onNewAnalysis }) {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <div className="brand-icon">
            <Zap size={16} color="white" strokeWidth={2.5} />
          </div>
          <div>
            <div className="brand-name">MatchAI</div>
            <div className="brand-sub">Resume × Job fit</div>
          </div>
        </div>
        <button className="btn-new" onClick={onNewAnalysis}>
          <Plus size={13} strokeWidth={2.5} />
          New analysis
        </button>
      </div>
    </nav>
  );
}
