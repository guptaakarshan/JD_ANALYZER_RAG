import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown, BookOpen, MessageSquare } from 'lucide-react';
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

  if (!qaLog.length && !isLoading) {
    return null;
  }

  return (
    <section className="insights-section animate-fade-up">
      <div className="insights-header">
        <span className="insights-title">
          <MessageSquare size={16} className="text-zinc mr-1.5 inline" />
          AI Answers & Insights
        </span>
        {qaLog.length > 0 && (
          <span className="insights-count">{qaLog.length} answer{qaLog.length !== 1 ? 's' : ''}</span>
        )}
      </div>

      {isLoading && !qaLog.length && <SkeletonLoader />}

      {qaLog.length > 0 && (
        <div className="answer-list">
          {qaLog.map((entry, idx) => {
            const isOpen = Boolean(openEvidence[idx]);
            const sourceCount = entry.sources?.length || 0;

            return (
              <article className="answer-item animate-fade-in" key={`${entry.question}-${idx}`}>
                <p className="q-label">YOU ASKED</p>
                <p className="q-text">"{entry.question}"</p>
                <div className="a-text">{cleanAnswerText(entry.answer)}</div>

                {sourceCount > 0 && (
                  <div className="evidence-block">
                    <button
                      className="evidence-toggle-btn"
                      onClick={() => toggleEvidence(idx)}
                      aria-expanded={isOpen}
                    >
                      <BookOpen size={13} />
                      Evidence · {sourceCount} source{sourceCount !== 1 ? 's' : ''}
                      <ChevronDown
                        size={13}
                        style={{
                          transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                          transition: 'transform 0.2s',
                        }}
                      />
                    </button>

                    {isOpen && (
                      <div className="evidence-list animate-fade-in">
                        {entry.sources.map((src, sIdx) => {
                          const isResume = src.document_type === 'resume';
                          const typeLabel = isResume ? 'Resume' : 'Job Description';
                          const sectionName = src.section
                            ? src.section
                                .split(' ')
                                .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                                .join(' ')
                            : isResume
                            ? 'Experience'
                            : 'Requirements';

                          const pageMeta = src.page ? `Page ${src.page}` : null;
                          const headerMeta = [typeLabel, pageMeta, sectionName]
                            .filter(Boolean)
                            .join(' · ');

                          return (
                            <div className="evidence-card" key={sIdx}>
                              <div className="ev-type">{headerMeta}</div>
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
