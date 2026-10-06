import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown, BookOpen, MessageCircle } from 'lucide-react';
import SkeletonLoader from './SkeletonLoader';

function cleanAnswerText(text) {
  if (!text) return '';
  return text
    .replace(/\[(?:resume|jd)-\d+\]/gi, '')
    .replace(/\s{2,}/g, ' ')
    .replace(/\s+([.,;:!?])/g, '$1')
    .trim();
}

export default function ResponseCard({ isLoading, qaLog }) {
  const bottomRef = useRef(null);
  const [openEvidence, setOpenEvidence] = useState({});

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [qaLog, isLoading]);

  const toggleEvidence = (idx) =>
    setOpenEvidence((prev) => ({ ...prev, [idx]: !prev[idx] }));

  return (
    <section className="insights-section animate-fade-up" style={{ animationDelay: '0.2s' }}>
      <div className="insights-header">
        <span className="insights-title">AI Insights</span>
        {qaLog.length > 0 && (
          <span className="insights-count">{qaLog.length} answer{qaLog.length !== 1 ? 's' : ''}</span>
        )}
      </div>

      {!qaLog.length && !isLoading && (
        <div className="insights-empty">
          <div className="insights-empty-icon">
            <MessageCircle size={20} />
          </div>
          Upload your resume, add a job description, then ask anything above.
        </div>
      )}

      {isLoading && !qaLog.length && <SkeletonLoader />}

      {qaLog.length > 0 && (
        <div className="answer-list">
          {qaLog.map((entry, idx) => {
            const isOpen = Boolean(openEvidence[idx]);
            return (
              <article className="answer-item animate-fade-in" key={`${entry.question}-${idx}`}>
                <p className="q-label">You asked</p>
                <p className="q-text">"{entry.question}"</p>
                <div className="a-text">{cleanAnswerText(entry.answer)}</div>

                {entry.sources?.length > 0 && (
                  <div>
                    <button
                      className="evidence-toggle-btn"
                      onClick={() => toggleEvidence(idx)}
                      aria-expanded={isOpen}
                    >
                      <BookOpen size={13} />
                      {isOpen ? 'Hide' : 'Show'} sources ({entry.sources.length})
                      <ChevronDown
                        size={13}
                        style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
                      />
                    </button>

                    {isOpen && (
                      <div className="evidence-list">
                        {entry.sources.map((src, sIdx) => {
                          const typeLabel = src.document_type === 'resume' ? 'Resume' : 'Job Description';
                          const meta = [
                            src.page ? `Page ${src.page}` : null,
                            src.section ? src.section.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : null,
                          ].filter(Boolean).join(' · ');
                          return (
                            <div className="evidence-card" key={src.label || sIdx}>
                              <div className="ev-type">{typeLabel}</div>
                              {meta && <div className="ev-meta">{meta}</div>}
                              <div className="ev-snippet">"{src.snippet}"</div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </article>
            );
          })}
          {isLoading && <SkeletonLoader />}
          <div ref={bottomRef} />
        </div>
      )}
    </section>
  );
}
