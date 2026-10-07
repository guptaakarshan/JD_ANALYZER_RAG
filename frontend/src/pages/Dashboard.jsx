import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import ResumeUploadCard from '../components/ResumeUploadCard';
import JobDescriptionCard from '../components/JobDescriptionCard';
import MatchResults from '../components/MatchResults';
import AskAISection from '../components/AskAISection';
import ResponseCard from '../components/ResponseCard';
import toast from 'react-hot-toast';
import { askQuestion, analyzeMatch, getErrorMessage } from '../services/api';
import { Zap, Sparkles, ArrowRight } from 'lucide-react';

export default function Dashboard() {
  const [sessionId, setSessionId] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [isJdSaved, setIsJdSaved] = useState(false);

  // Structured Analysis State
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Q&A state
  const [qaLog, setQaLog] = useState([]);
  const [isLoadingQA, setIsLoadingQA] = useState(false);

  const isReady = uploadedFileName && isJdSaved;

  const handleResumeSuccess = (data) => {
    if (!data) {
      setUploadedFileName(null);
      setAnalysisResult(null);
      return;
    }
    setUploadedFileName(data.filename);
    if (data.sessionId) setSessionId(data.sessionId);
    // Reset old analysis when uploading new resume
    setAnalysisResult(null);
  };

  const handleJdSuccess = (result) => {
    if (typeof result === 'boolean') {
      setIsJdSaved(result);
      if (!result) setAnalysisResult(null);
    } else {
      setIsJdSaved(true);
      if (result) setSessionId(result);
      // Reset old analysis when saving new JD
      setAnalysisResult(null);
    }
  };

  const handleNewAnalysis = () => {
    setSessionId(null);
    setUploadedFileName(null);
    setIsJdSaved(false);
    setAnalysisResult(null);
    setQaLog([]);
  };

  const handleAnalyzeMatch = async () => {
    if (!sessionId) {
      toast.error('Session not initialized. Please re-upload your resume or job description.');
      return;
    }
    if (!uploadedFileName) {
      toast.error('Please upload your resume first.');
      return;
    }
    if (!isJdSaved) {
      toast.error('Please save a job description first.');
      return;
    }

    setIsAnalyzing(true);
    const tid = toast.loading('Calculating structured match score…');
    try {
      const data = await analyzeMatch(sessionId);
      setAnalysisResult(data);
      toast.dismiss(tid);
      toast.success('Match analysis complete!');
    } catch (err) {
      toast.dismiss(tid);
      toast.error(getErrorMessage(err));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAsk = async (question) => {
    if (!uploadedFileName) {
      toast.error('Upload a resume first.');
      return;
    }
    if (!isJdSaved) {
      toast.error('Save a job description first.');
      return;
    }

    setIsLoadingQA(true);
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
      setIsLoadingQA(false);
    }
  };

  return (
    <div className="app-shell">
      <Navbar onNewAnalysis={handleNewAnalysis} />

      <main className="app-main">
        {/* Hero Banner */}
        <div className="hero">
          <div className="hero-badge">
            <Zap size={11} strokeWidth={2.5} />
            AI-powered match analysis
          </div>
          <h1>Know exactly how well<br />you fit the role</h1>
          <p>
            Upload your resume, paste the job description, and get instant structured insights
            on your fit, strengths, and gaps.
          </p>
        </div>

        {/* Upload Inputs Grid */}
        <div className="uploads-row">
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
        </div>

        {/* Action Button: Analyze My Match */}
        {isReady && (
          <div className="analyze-action-bar animate-fade-in">
            <button
              className="btn-analyze-match"
              onClick={handleAnalyzeMatch}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <span className="spinner" />
                  Analyzing your match…
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Analyze My Match
                  <ArrowRight size={15} />
                </>
              )}
            </button>
          </div>
        )}

        {/* Helper Hint when not ready */}
        {!isReady && (
          <div className="ready-gate animate-fade-in">
            {!uploadedFileName && !isJdSaved
              ? 'Upload your resume and save a job description to analyze your match.'
              : !uploadedFileName
              ? 'Upload your resume to continue.'
              : 'Save a job description to continue.'}
          </div>
        )}

        {/* Structured Results Display */}
        {analysisResult && (
          <MatchResults analysis={analysisResult} />
        )}

        {/* Ask AI Section */}
        <AskAISection
          onAsk={handleAsk}
          isLoading={isLoadingQA}
          disabled={!isReady}
        />

        {/* AI Q&A Response Cards with Collapsible Evidence */}
        <ResponseCard
          qaLog={qaLog}
          isLoading={isLoadingQA}
        />
      </main>

      <footer className="app-footer">
        © {new Date().getFullYear()} MatchAI · Built for smarter job search
      </footer>
    </div>
  );
}
