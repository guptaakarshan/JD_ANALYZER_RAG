import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import ResumeUploadCard from '../components/ResumeUploadCard';
import JobDescriptionCard from '../components/JobDescriptionCard';
import AskAISection from '../components/AskAISection';
import ResponseCard from '../components/ResponseCard';
import toast from 'react-hot-toast';
import { askQuestion, getErrorMessage } from '../services/api';

export default function Dashboard() {
  const [sessionId, setSessionId] = useState(null);
  // Track what has been indexed on the backend
  const [uploadedFileName, setUploadedFileName] = useState(null); // null = not uploaded
  const [isJdSaved, setIsJdSaved] = useState(false);

  // Q&A state
  const [qaLog, setQaLog] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Both must be ready before Ask AI is useful
  const isReady = uploadedFileName && isJdSaved;

  const handleResumeSuccess = (data) => {
    if (!data) {
      setUploadedFileName(null);
      return;
    }
    setUploadedFileName(data.filename);
    if (data.sessionId) {
      setSessionId(data.sessionId);
    }
  };

  const handleJdSuccess = (result) => {
    if (typeof result === 'boolean') {
      setIsJdSaved(result);
    } else {
      setIsJdSaved(true);
      if (result) {
        setSessionId(result);
      }
    }
  };

  const handleAsk = async (question) => {
    if (!uploadedFileName) {
      toast.error('Please upload a resume first.');
      return;
    }
    if (!isJdSaved) {
      toast.error('Please save a job description first.');
      return;
    }

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
    <div className="min-h-screen bg-[#F4F4F5] flex flex-col">
      <Navbar />

      <main className="flex-1 w-full max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-6">
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

        {/* Readiness hint */}
        {!isReady && (
          <p className="text-xs text-gray-400 text-center">
            {!uploadedFileName && !isJdSaved
              ? 'Upload a resume and save a job description to enable Q&A.'
              : !uploadedFileName
                ? 'Upload a resume to enable Q&A.'
                : 'Save a job description to enable Q&A.'}
          </p>
        )}

        <AskAISection onAsk={handleAsk} isLoading={isLoading} />

        <ResponseCard qaLog={qaLog} isLoading={isLoading} />
      </main>

      <footer className="py-6 text-center text-xs text-gray-400 border-t border-gray-200 bg-white">
        © {new Date().getFullYear()} JD Analyzer. Built for smarter recruitment.
      </footer>
    </div>
  );
}
