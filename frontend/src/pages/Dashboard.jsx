import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import ResumeUploadCard from '../components/ResumeUploadCard';
import JobDescriptionCard from '../components/JobDescriptionCard';
import AskAISection from '../components/AskAISection';
import ResponseCard from '../components/ResponseCard';
import toast from 'react-hot-toast';
import { askQuestion, getErrorMessage } from '../services/api';
import { Zap, FileText, BrainCircuit, MessageSquare } from 'lucide-react';

// Progress step indicator
function StepsStrip({ resumeReady, jdReady }) {
  const steps = [
    { label: 'Resume', done: resumeReady, icon: FileText },
    { label: 'Job Description', done: jdReady, icon: BrainCircuit },
    { label: 'Ask AI', done: false, active: resumeReady && jdReady, icon: MessageSquare },
  ];

  return (
    <div className="steps-strip">
      {steps.map((step, i) => (
        <React.Fragment key={step.label}>
          <div className={`step-node${step.done ? ' done' : step.active ? ' active' : ''}`}>
            <div className="step-dot">
              {step.done ? '✓' : i + 1}
            </div>
            {step.label}
          </div>
          {i < steps.length - 1 && <div className="step-connector" />}
        </React.Fragment>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [sessionId, setSessionId] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [isJdSaved, setIsJdSaved] = useState(false);
  const [qaLog, setQaLog] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const isReady = uploadedFileName && isJdSaved;

  const handleResumeSuccess = (data) => {
    if (!data) { setUploadedFileName(null); return; }
    setUploadedFileName(data.filename);
    if (data.sessionId) setSessionId(data.sessionId);
  };

  const handleJdSuccess = (result) => {
    if (typeof result === 'boolean') {
      setIsJdSaved(result);
    } else {
      setIsJdSaved(true);
      if (result) setSessionId(result);
    }
  };

  const handleNewAnalysis = () => {
    setSessionId(null);
    setUploadedFileName(null);
    setIsJdSaved(false);
    setQaLog([]);
  };

  const handleAsk = async (question) => {
    if (!uploadedFileName) { toast.error('Upload a resume first.'); return; }
    if (!isJdSaved) { toast.error('Save a job description first.'); return; }

    setIsLoading(true);
    try {
      const data = await askQuestion(question, sessionId);
      setQaLog((prev) => [
        ...prev,
        {
          question,
          answer: data.answer,
          sources: data.sources || [],
          retrieval_stats: data.retrieval_stats || null,
        },
      ]);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Navbar onNewAnalysis={handleNewAnalysis} />

      <main className="app-main">
        {/* Hero */}
        <div className="hero">
          <div className="hero-badge">
            <Zap size={11} strokeWidth={3} />
            AI-powered match analysis
          </div>
          <h1>Know exactly how well<br />you fit the role</h1>
          <p>Upload your resume, paste the job description, and get instant AI insights on your fit, strengths, and gaps.</p>
        </div>

        {/* Step progress */}
        <StepsStrip resumeReady={!!uploadedFileName} jdReady={isJdSaved} />

        {/* Upload cards */}
        <ResumeUploadCard
          onUploadSuccess={handleResumeSuccess}
          uploadedFileName={uploadedFileName}
          sessionId={sessionId}
        />

        <JobDescriptionCard
          onSaveSuccess={handleJdSuccess}
          isSaved={isJdSaved}
          sessionId={sessionId}
        />

        {/* Gate hint */}
        {!isReady && (
          <div className="ready-gate animate-fade-in">
            {!uploadedFileName && !isJdSaved
              ? 'Complete both steps above to start asking questions.'
              : !uploadedFileName
                ? 'Upload your resume to continue.'
                : 'Save a job description to continue.'}
          </div>
        )}

        {/* Ask AI */}
        <AskAISection onAsk={handleAsk} isLoading={isLoading} disabled={!isReady} />

        {/* AI responses */}
        <ResponseCard qaLog={qaLog} isLoading={isLoading} />
      </main>

      <footer className="app-footer">
        © {new Date().getFullYear()} MatchAI · Built for smarter job search
      </footer>
    </div>
  );
}
