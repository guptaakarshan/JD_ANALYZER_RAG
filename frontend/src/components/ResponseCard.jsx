import React, { useEffect, useRef } from 'react';
import { MessageSquare } from 'lucide-react';
import SkeletonLoader from './SkeletonLoader';

export default function ResponseCard({ isLoading, qaLog }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [qaLog, isLoading]);

  const isEmpty = !isLoading && qaLog.length === 0;

  return (
    <section className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 p-6">
      <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-4">
        4. Answer
      </p>

      {/* Empty state — shown only when nothing has happened yet */}
      {isEmpty && (
        <div className="rounded-xl border border-dashed border-gray-200 py-14 flex flex-col items-center justify-center gap-3 text-center px-6 bg-gray-50/10">
          <div className="bg-gray-50 rounded-full p-3 shrink-0">
            <MessageSquare className="h-6 w-6 text-gray-400" strokeWidth={1.5} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700">No questions asked yet</p>
            <p className="text-xs text-gray-400 mt-1 max-w-[280px] mx-auto leading-relaxed">
              Upload a resume and save a job description, then type a question to start.
            </p>
          </div>
        </div>
      )}

      {/* Loading state for the very first question (log still empty) */}
      {isLoading && qaLog.length === 0 && (
        <div className="py-4">
          <SkeletonLoader />
        </div>
      )}

      {/* Q&A log — previous answers always stay visible while a new one loads */}
      {qaLog.length > 0 && (
        <div className="space-y-4 max-h-[480px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-transparent">
          {qaLog.map((entry, i) => (
            <div key={i} className="space-y-3">
              {/* Question bubble */}
              <div className="flex justify-end">
                <div className="bg-black text-white text-sm px-4 py-2.5 rounded-2xl rounded-tr-sm max-w-[85%] leading-relaxed shadow-sm">
                  {entry.question}
                </div>
              </div>
              {/* Answer bubble */}
              <div className="flex justify-start">
                <div className="bg-gray-100/80 border border-gray-100 text-gray-800 text-sm px-4 py-3 rounded-2xl rounded-tl-sm max-w-[85%] leading-relaxed whitespace-pre-wrap shadow-sm">
                  {entry.answer}
                </div>
              </div>
            </div>
          ))}

          {/* Skeleton Loader appended below the last answer while a new one loads */}
          {isLoading && (
            <div className="pt-2">
              <SkeletonLoader />
            </div>
          )}

          {/* Scroll anchor */}
          <div ref={bottomRef} />
        </div>
      )}
    </section>
  );
}
